"""Read a problem from a text file (Markdown) and, optionally, a zip with tests.

The format is described in resources/problem-template.md. In short:

    # Название задачи
    Время: 1 с
    Память: 256 МБ

    Условие...
    ## Входные данные
    ## Выходные данные
    ## Пример 1  (Ввод/Вывод with ``` blocks)
    ## Пояснение
    ## Тесты     (optional: ### Тест 1 with Ввод/Вывод blocks)

Everything is optional except the statement itself. Tests come from the zip,
from the "Тесты" section, or, as a last resort, from the samples.
"""
import io
import os
import re
import zipfile
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from judge.utils.problem_samples import extract_samples
from judge.utils.test_files import natural_key, pair_test_files

STATEMENT_EXTENSIONS = ('.md', '.txt', '.markdown')
MAX_TEST_BYTES = 64 * 1024 * 1024

TIME_RE = re.compile(r'^\s*(?:ограничение\s+)?(?:по\s+)?(?:времени|время|time(?:\s+limit)?|убакыт)\s*[:=—-]\s*'
                     r'([\d.,]+)\s*(мс|ms|миллисекунд\w*|с|сек\w*|s|sec\w*|секунд\w*)?\s*\.?\s*$', re.I)
MEMORY_RE = re.compile(r'^\s*(?:ограничение\s+)?(?:по\s+)?(?:памяти|память|memory(?:\s+limit)?|эс\s+тутум)\s*'
                       r'[:=—-]\s*([\d.,]+)\s*(кб|kb|kib|мб|mb|mib|мегабайт\w*|гб|gb|gib)?\s*\.?\s*$', re.I)
POINTS_RE = re.compile(r'^\s*(?:баллы|балл|очки|points|упай)\s*[:=—-]\s*([\d.,]+)\s*$', re.I)
TITLE_RE = re.compile(r'^\s*#\s+(.+?)\s*#*\s*$')
TESTS_HEADING_RE = re.compile(r'^\s*#{2,3}\s*(тесты|tests|тестовые данные|тесттер)\s*:?\s*$', re.I | re.M)
HEADING_RE = re.compile(r'^\s*##\s+\S', re.M)
TITLE_LABEL_RE = re.compile(r'^\s*(?:название|задача|title|аталышы)\s*[:=—-]\s*(.+)$', re.I)


@dataclass
class ParsedProblem:
    name: str = ''
    description: str = ''
    time_limit: float = 1.0
    memory_limit: int = 262144   # KB
    points: float = 100
    tests: List[Tuple[bytes, bytes]] = field(default_factory=list)
    tests_source: str = ''
    samples: list = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def decode_text(data: bytes) -> str:
    for encoding in ('utf-8-sig', 'cp1251'):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode('utf-8', 'replace')


def _number(text):
    return float(text.replace(',', '.'))


def name_from_filename(filename: str) -> str:
    base = os.path.splitext(os.path.basename(filename or ''))[0]
    base = re.sub(r'^(задача|problem)\s*[-—:.]?\s*', '', base, flags=re.I).strip()
    if base.lower() in ('условие', 'statement', 'problem', 'readme', 'шарт', ''):
        return ''
    return base


def parse_statement(text: str, filename: str = '') -> ParsedProblem:
    result = ParsedProblem()
    text = text.replace('\r\n', '\n').replace('\r', '\n').strip('\n')
    lines = text.split('\n')

    # Header: title and limits before the statement starts.
    body_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        match = TITLE_RE.match(line)
        if match and not result.name and not line.startswith('##'):
            result.name = match.group(1).strip()
            body_start = i + 1
            continue
        match = TITLE_LABEL_RE.match(line)
        if match and not result.name:
            result.name = match.group(1).strip()
            body_start = i + 1
            continue
        match = TIME_RE.match(line)
        if match:
            value = _number(match.group(1))
            unit = (match.group(2) or 'с').lower()
            result.time_limit = value / 1000 if unit.startswith(('мс', 'ms', 'милли')) else value
            body_start = i + 1
            continue
        match = MEMORY_RE.match(line)
        if match:
            value = _number(match.group(1))
            unit = (match.group(2) or 'мб').lower()
            if unit.startswith(('кб', 'kb', 'kib')):
                result.memory_limit = int(value)
            elif unit.startswith(('гб', 'gb', 'gib')):
                result.memory_limit = int(value * 1024 * 1024)
            else:
                result.memory_limit = int(value * 1024)
            body_start = i + 1
            continue
        match = POINTS_RE.match(line)
        if match:
            result.points = _number(match.group(1))
            body_start = i + 1
            continue
        break

    body = '\n'.join(lines[body_start:]).strip('\n')

    # A "Тесты" section is data, not part of the statement.
    tests_match = TESTS_HEADING_RE.search(body)
    if tests_match:
        after = body[tests_match.end():]
        next_heading = re.search(r'^\s*##\s+(?!#)', after, re.M)
        tests_text = after[:next_heading.start()] if next_heading else after
        rest = after[next_heading.start():] if next_heading else ''
        body = (body[:tests_match.start()].rstrip('\n') + ('\n\n' + rest.lstrip('\n') if rest else '')).strip('\n')
        result.tests = [(s['input'].encode(), s['output'].encode()) for s in extract_samples(tests_text)]
        if result.tests:
            result.tests_source = 'section'

    result.description = body + '\n'
    result.samples = extract_samples(body)
    if not result.name:
        result.name = name_from_filename(filename)
    if not result.name:
        result.warnings.append('Не найдено название задачи. Впишите его вручную.')
    if not body.strip():
        result.warnings.append('Условие задачи пустое.')
    return result


def read_upload(statement_name: str, statement_data: Optional[bytes], zip_data: Optional[bytes]) -> ParsedProblem:
    """Combine a statement file and/or a zip archive into one problem."""
    archive = None
    if zip_data:
        try:
            archive = zipfile.ZipFile(io.BytesIO(zip_data))
        except zipfile.BadZipFile:
            result = ParsedProblem()
            result.warnings.append('Архив повреждён или это не zip.')
            return result

    if statement_data is None and archive is not None:
        candidates = [n for n in archive.namelist()
                      if n.lower().endswith(STATEMENT_EXTENSIONS) and not n.endswith('/') and
                      not os.path.basename(n).startswith('.') and '__MACOSX' not in n]
        # Prefer a file that looks like a statement over test files saved as .txt.
        candidates.sort(key=lambda n: (not re.search(r'услов|statement|problem|задач|шарт', n, re.I),
                                       re.search(r'(input|output)\d*\.txt$', n, re.I) is not None, len(n)))
        if candidates:
            statement_name = candidates[0]
            statement_data = archive.read(candidates[0])

    if statement_data is None:
        result = ParsedProblem()
        result.warnings.append('Не найден файл с условием (.md или .txt).')
        return result

    result = parse_statement(decode_text(statement_data), statement_name)
    if not result.name and archive is not None and statement_name:
        folder = os.path.dirname(statement_name)
        result.name = name_from_filename(os.path.basename(folder)) if folder else ''
        if result.name:
            result.warnings = [w for w in result.warnings if 'название' not in w]

    if archive is not None:
        names = [n for n in archive.namelist() if n != statement_name]
        total = sum(archive.getinfo(n).file_size for n in names)
        if total > MAX_TEST_BYTES:
            result.warnings.append('Тесты занимают больше 64 МБ, архив не принят.')
        else:
            pairs = pair_test_files(names)
            # Nested zips with tests ("tests.zip" inside the archive) are common too.
            if not pairs:
                for inner in sorted((n for n in names if n.lower().endswith('.zip')), key=natural_key):
                    try:
                        nested = zipfile.ZipFile(io.BytesIO(archive.read(inner)))
                    except zipfile.BadZipFile:
                        continue
                    pairs = pair_test_files(nested.namelist())
                    if pairs:
                        result.tests = [(nested.read(a), nested.read(b)) for a, b in pairs]
                        result.tests_source = 'archive'
                        break
            else:
                result.tests = [(archive.read(a), archive.read(b)) for a, b in pairs]
                result.tests_source = 'archive'

    if not result.tests and result.samples:
        result.tests = [(s['input'].encode(), s['output'].encode()) for s in result.samples]
        result.tests_source = 'samples'
        result.warnings.append('Тестов нет, поэтому тестами стали примеры из условия. Лучше добавить настоящие тесты.')
    if not result.tests:
        result.warnings.append('Тесты не найдены. Задачу можно сохранить и загрузить тесты потом.')
    return result


def build_tests_zip(tests) -> bytes:
    out = io.BytesIO()
    width = max(2, len(str(len(tests))))
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
        for i, (inp, ans) in enumerate(tests, 1):
            zf.writestr('%0*d.in' % (width, i), inp)
            zf.writestr('%0*d.out' % (width, i), ans)
    return out.getvalue()
