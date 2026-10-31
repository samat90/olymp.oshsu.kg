"""Question checks shared by the quiz editor and the Excel import, the import itself and its template."""
import math
import re
from io import BytesIO

from judge.models.quiz import Question

TYPE_CODES = [code for code, _name in Question.TYPES]
LANGUAGES = (('python', 'Python'), ('cpp', 'C++'), ('c', 'C'), ('java', 'Java'), ('pascal', 'Pascal'),
             ('javascript', 'JavaScript'), ('csharp', 'C#'), ('text', 'Текст'))
LANGUAGE_CODES = [code for code, _name in LANGUAGES]
TIME_MIN, TIME_MAX = 5, 240
WEIGHT_CODES = (0, 1, 2)
MAX_QUESTIONS = 100
MAX_ANSWERS = 20
MAX_WORD = 24
# (min, max) options of each type; types missing here have no options.
OPTION_LIMITS = {
    Question.SINGLE: (2, 4), Question.TRUEFALSE: (2, 2), Question.MULTI: (2, 6), Question.ORDER: (3, 6),
    Question.CODE: (2, 4), Question.POLL: (2, 6),
}
TRUE_FALSE = ('Верно', 'Неверно')


class QuestionError(Exception):
    def __init__(self, message, field=''):
        super().__init__(message)
        self.field = field


def text_value(value, limit, field, name):
    value = '' if value is None else str(value)
    value = value.replace('\r\n', '\n').strip()
    if len(value) > limit:
        raise QuestionError('%s: не больше %d символов' % (name, limit), field)
    return value


def number(value, field, name, default=None):
    if value is None or str(value).strip() == '':
        if default is None:
            raise QuestionError('%s: нужно число' % name, field)
        return default
    try:
        result = float(str(value).strip().replace(',', '.').replace(' ', ''))
    except ValueError:
        raise QuestionError('%s: нужно число' % name, field)
    if not math.isfinite(result) or abs(result) > 1e12:
        raise QuestionError('%s: неверное число' % name, field)
    return int(result) if result == int(result) else result


def answer_list(values):
    if isinstance(values, str):
        values = re.split(r'[;|\n]', values)
    if not isinstance(values, (list, tuple)):
        return []
    result = []
    for value in values:
        value = str(value).strip()[:100]
        if value and value not in result:
            result.append(value)
    if len(result) > MAX_ANSWERS:
        raise QuestionError('Не больше %d ответов' % MAX_ANSWERS, 'answers')
    return result


def has_options(type, data):
    if type == Question.CODE:
        return not data.get('input')
    return type in OPTION_LIMITS


def clean_data(type, data):
    data = data if isinstance(data, dict) else {}
    if type == Question.WORD:
        word = ' '.join(str(data.get('word') or '').split()).upper()
        if len(word) > MAX_WORD:
            raise QuestionError('Слово: не больше %d букв' % MAX_WORD, 'word')
        return {'word': word}
    if type == Question.TEXT:
        return {'answers': answer_list(data.get('answers')),
                'tolerance': abs(number(data.get('tolerance'), 'tolerance', 'Допуск', 0))}
    if type == Question.CODE:
        if data.get('input'):
            return {'input': True, 'answers': answer_list(data.get('answers')),
                    'tolerance': abs(number(data.get('tolerance'), 'tolerance', 'Допуск', 0))}
        return {'input': False}
    if type == Question.SLIDER:
        lo = number(data.get('min'), 'min', 'Минимум', 0)
        hi = number(data.get('max'), 'max', 'Максимум', 100)
        step = number(data.get('step'), 'step', 'Шаг', 1)
        if lo >= hi:
            raise QuestionError('Минимум должен быть меньше максимума', 'max')
        if step <= 0 or step > hi - lo:
            raise QuestionError('Шаг должен быть больше 0 и не больше диапазона', 'step')
        if (hi - lo) / step > 100000:
            raise QuestionError('Слишком мелкий шаг', 'step')
        answer = number(data.get('answer'), 'answer', 'Ответ', lo)
        if not lo <= answer <= hi:
            raise QuestionError('Ответ должен быть от минимума до максимума', 'answer')
        tolerance = abs(number(data.get('tolerance'), 'tolerance', 'Допуск', 0))
        unit = str(data.get('unit') or '').strip()[:12]
        return {'min': lo, 'max': hi, 'step': step, 'answer': answer, 'tolerance': tolerance, 'unit': unit}
    if type == Question.PIN:
        x = min(max(number(data.get('x'), 'x', 'X', 50), 0), 100)
        y = min(max(number(data.get('y'), 'y', 'Y', 50), 0), 100)
        r = min(max(number(data.get('r'), 'r', 'Радиус', 10), 1), 50)
        return {'x': round(x, 2), 'y': round(y, 2), 'r': round(r, 2)}
    return {}


def clean_options(type, data, options):
    """Normalised options: [{'id', 'text', 'is_correct', 'has_image'}]."""
    if not has_options(type, data):
        return []
    if not isinstance(options, list):
        options = []
    result = []
    for raw in options:
        if not isinstance(raw, dict):
            continue
        option_id = raw.get('id')
        result.append({'id': option_id if isinstance(option_id, int) else None,
                       'text': text_value(raw.get('text'), 300, 'options', 'Вариант'),
                       'is_correct': bool(raw.get('is_correct')), 'has_image': bool(raw.get('image'))})
    low, high = OPTION_LIMITS[type]
    if type == Question.TRUEFALSE:
        first_correct = result[0]['is_correct'] if result else True
        if len(result) > 1 and not first_correct and not result[1]['is_correct']:
            first_correct = True
        ids = [o['id'] for o in result] + [None, None]
        return [{'id': ids[0], 'text': TRUE_FALSE[0], 'is_correct': first_correct, 'has_image': False},
                {'id': ids[1], 'text': TRUE_FALSE[1], 'is_correct': not first_correct, 'has_image': False}]
    if len(result) > high:
        raise QuestionError('Не больше %d вариантов' % high, 'options')
    if type in (Question.ORDER, Question.POLL):
        for option in result:
            option['is_correct'] = False
    elif type in (Question.SINGLE, Question.CODE):
        seen = False
        for option in result:
            option['is_correct'] = option['is_correct'] and not seen
            seen = seen or option['is_correct']
    return result


def clean_question(payload):
    """Check and normalise a question from the editor or the import: (fields, options). Raises QuestionError."""
    if not isinstance(payload, dict):
        raise QuestionError('Неверный запрос')
    type = payload.get('type')
    if type not in TYPE_CODES:
        raise QuestionError('Неизвестный тип вопроса', 'type')
    try:
        time_limit = int(payload.get('time_limit', 20))
    except (TypeError, ValueError):
        raise QuestionError('Время: нужно число секунд', 'time_limit')
    if not TIME_MIN <= time_limit <= TIME_MAX:
        raise QuestionError('Время: от %d до %d секунд' % (TIME_MIN, TIME_MAX), 'time_limit')
    try:
        weight = int(payload.get('weight', 1))
    except (TypeError, ValueError):
        weight = -1
    if weight not in WEIGHT_CODES:
        raise QuestionError('Неверные очки', 'weight')
    code = text_value(payload.get('code'), 4000, 'code', 'Код')
    language = str(payload.get('code_language') or '')
    if language not in LANGUAGE_CODES:
        language = 'python' if type == Question.CODE else ''
    data = clean_data(type, payload.get('data'))
    fields = {
        'type': type, 'text': text_value(payload.get('text'), 2000, 'text', 'Текст вопроса'),
        'code': code, 'code_language': language if code or type == Question.CODE else '',
        'time_limit': time_limit, 'weight': weight, 'data': data,
        'explanation': text_value(payload.get('explanation'), 2000, 'explanation', 'Пояснение'),
    }
    return fields, clean_options(type, data, payload.get('options'))


def problems(fields, options, has_image):
    """What still prevents the question from being played properly (shown in the editor, not blocking saves)."""
    type, data = fields['type'], fields['data']
    found = []
    if not fields['text'] and not has_image and not fields['code']:
        found.append('Нет текста вопроса')
    if type == Question.CODE and not fields['code']:
        found.append('Добавьте код')
    if has_options(type, data):
        low = OPTION_LIMITS[type][0]
        if len(options) < low:
            found.append('Нужно минимум %d варианта' % low)
        if any(not o['text'] and not o.get('has_image') for o in options):
            found.append('Есть пустой вариант')
        if type in (Question.SINGLE, Question.TRUEFALSE, Question.CODE) and not any(o['is_correct'] for o in options):
            found.append('Отметьте верный вариант')
        if type == Question.MULTI and not any(o['is_correct'] for o in options):
            found.append('Отметьте хотя бы один верный вариант')
    if type == Question.WORD and len(data.get('word', '').replace(' ', '')) < 2:
        found.append('Введите слово')
    if (type == Question.TEXT or (type == Question.CODE and data.get('input'))) and not data.get('answers'):
        found.append('Добавьте хотя бы один ответ')
    if type == Question.PIN and not has_image:
        found.append('Загрузите картинку')
    return found


# ---------------------------------------------------------------- Excel

MAX_FILE = 2 * 1024 * 1024
MAX_ROWS = 100
MAX_OPTIONS = 6
COLUMNS = ['Тип', 'Вопрос', 'Код', 'Язык'] + ['Вариант %d' % i for i in range(1, MAX_OPTIONS + 1)] + \
    ['Верные', 'Время', 'Очки', 'Пояснение', 'Мин', 'Макс', 'Шаг', 'Допуск', 'Ед. изм.']
HEADER_KEYS = {
    'тип': 'type', 'вопрос': 'text', 'код': 'code', 'язык': 'lang', 'верные': 'correct', 'верный': 'correct',
    'ответ': 'correct', 'ответы': 'correct', 'время': 'time', 'очки': 'weight', 'пояснение': 'explanation',
    'мин': 'min', 'макс': 'max', 'шаг': 'step', 'допуск': 'tolerance', 'ед. изм.': 'unit', 'единица': 'unit',
    'ед.изм.': 'unit',
}
TYPE_ALIASES = {
    'один': Question.SINGLE, 'один вариант': Question.SINGLE, 'одиночный': Question.SINGLE,
    'верно/неверно': Question.TRUEFALSE, 'верно неверно': Question.TRUEFALSE, 'да/нет': Question.TRUEFALSE,
    'несколько': Question.MULTI, 'несколько верных': Question.MULTI,
    'слово': Question.WORD, 'собери слово': Question.WORD,
    'порядок': Question.ORDER, 'расставь по порядку': Question.ORDER,
    'код': Question.CODE, 'что выведет код': Question.CODE,
    'ответ': Question.TEXT, 'ввод': Question.TEXT, 'введи ответ': Question.TEXT,
    'ползунок': Question.SLIDER, 'число на шкале': Question.SLIDER,
    'точка': Question.PIN, 'точка на картинке': Question.PIN,
    'опрос': Question.POLL, 'облако': Question.CLOUD, 'облако слов': Question.CLOUD,
    'открытый': Question.OPEN, 'открытый ответ': Question.OPEN,
}
LANGUAGE_ALIASES = {name.lower(): code for code, name in LANGUAGES}
LANGUAGE_ALIASES.update({code: code for code in LANGUAGE_CODES})
LANGUAGE_ALIASES.update({'c++': 'cpp', 'js': 'javascript', 'c#': 'csharp', 'паскаль': 'pascal', 'питон': 'python'})
EXAMPLES = [
    ['Один вариант', 'Столица Кыргызстана?', '', '', 'Ош', 'Бишкек', 'Каракол', 'Нарын', '', '', '2', 20,
     'обычные', 'Бишкек — столица с 1991 года.'],
    ['Несколько верных', 'Какие числа простые?', '', '', '2', '9', '11', '15', '', '', '1, 3', 30, 'x2'],
    ['Верно / Неверно', 'Вода кипит при 100 °C на уровне моря.', '', '', '', '', '', '', '', '', 'Верно', 10],
    ['Введи ответ', 'Сколько будет 7 × 8?', '', '', '', '', '', '', '', '', '56', 20],
    ['Что выведет код', 'Что выведет программа?', 'print(2 ** 3)', 'Python', '6', '8', '9', '', '', '', '2', 30],
    ['Собери слово', 'Пошаговый план решения задачи', '', '', '', '', '', '', '', '', 'Алгоритм', 30],
    ['Расставь по порядку', 'От меньшего к большему', '', '', '1 КБ', '1 МБ', '1 ГБ', '1 ТБ', '', '', '', 30],
    ['Ползунок', 'Высота пика Ленина, м', '', '', '', '', '', '', '', '', 7134, 30, 'обычные', '', 5000, 8000,
     1, 100, 'м'],
    ['Опрос', 'Какой урок любимый?', '', '', 'Математика', 'Информатика', 'Физика', '', '', '', '', 20,
     'без очков'],
]
INSTRUCTIONS = [
    ('Колонка', 'Что писать'),
    ('Тип', 'Один вариант, Верно / Неверно, Несколько верных, Собери слово, Расставь по порядку, '
            'Что выведет код, Введи ответ, Ползунок, Опрос, Облако слов, Открытый ответ. '
            'Точку на картинке добавляйте в редакторе: ей нужна картинка.'),
    ('Вопрос', 'Текст вопроса. Можно markdown и формулы в $...$.'),
    ('Код, Язык', 'Для «Что выведет код»: текст программы и язык (Python, C++, C, Java, Pascal, JavaScript, C#).'),
    ('Вариант 1–6', 'Варианты ответа. Один вариант и код: 2–4; несколько верных и опрос: 2–6; '
                    'порядок: 3–6 пунктов сразу в верном порядке (игрокам они перемешаются).'),
    ('Верные', 'Номера верных вариантов: «2» или «1, 3». Верно / Неверно: «Верно» или «Неверно». '
               'Собери слово: само слово. Введи ответ: допустимые ответы через «;». '
               'Код без вариантов: ответ через «;». Ползунок: число.'),
    ('Время', 'Секунды на ответ, от 5 до 240. Пусто — 20.'),
    ('Очки', 'обычные, x2 или без очков. Пусто — обычные.'),
    ('Пояснение', 'Показывается после ответа. Можно оставить пустым.'),
    ('Мин, Макс, Шаг', 'Для ползунка: шкала от Мин до Макс с шагом Шаг.'),
    ('Допуск', 'Ползунок и числовые ответы: насколько можно ошибиться и всё равно получить очки.'),
    ('Ед. изм.', 'Для ползунка: подпись к числу, например «км».'),
    ('', 'Не больше %d строк за раз. Пустые строки пропускаются. Первая строка — заголовки, не меняйте их.'
         % MAX_ROWS),
]


def template_bytes():
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    book = Workbook()
    sheet = book.active
    sheet.title = 'Вопросы'
    sheet.append(COLUMNS)
    for row in EXAMPLES:
        sheet.append(row)
    header_fill = PatternFill('solid', fgColor='DCE6F2')
    for cell in sheet[1]:
        cell.font = Font(bold=True)
        cell.fill = header_fill
    widths = {'A': 20, 'B': 40, 'C': 18, 'D': 10, 'K': 12, 'L': 8, 'M': 11, 'N': 30}
    for column in range(1, len(COLUMNS) + 1):
        letter = sheet.cell(row=1, column=column).column_letter
        sheet.column_dimensions[letter].width = widths.get(letter, 12)
    sheet.freeze_panes = 'A2'
    help_sheet = book.create_sheet('Инструкция')
    for row in INSTRUCTIONS:
        help_sheet.append(list(row))
    help_sheet.column_dimensions['A'].width = 18
    help_sheet.column_dimensions['B'].width = 100
    for cell in help_sheet[1]:
        cell.font = Font(bold=True)
    for row in help_sheet.iter_rows(min_row=2):
        row[1].alignment = Alignment(wrap_text=True, vertical='top')
        row[0].alignment = Alignment(vertical='top')
        row[0].font = Font(bold=True)
    buf = BytesIO()
    book.save(buf)
    return buf.getvalue()


def cell_text(value):
    if value is None:
        return ''
    if isinstance(value, float) and value == int(value):
        value = int(value)
    return str(value).strip()


def header_map(header):
    mapping = {}
    for index, title in enumerate(header):
        name = ' '.join(cell_text(title).lower().replace('ё', 'е').split())
        match = re.fullmatch(r'вариант\s*(\d)', name)
        if match and 1 <= int(match.group(1)) <= MAX_OPTIONS:
            mapping['opt%s' % match.group(1)] = index
        elif name in HEADER_KEYS and HEADER_KEYS[name] not in mapping:
            mapping[HEADER_KEYS[name]] = index
    return mapping


def parse_type(value):
    name = ' '.join(cell_text(value).lower().replace('ё', 'е').split())
    if name in TYPE_CODES:
        return name
    for code, title in Question.TYPES:
        if name == title.lower():
            return code
    return TYPE_ALIASES.get(name.replace(' / ', '/'), TYPE_ALIASES.get(name))


def parse_weight(value):
    name = cell_text(value).lower().replace('х', 'x').replace(' ', '')
    if name in ('', '1', 'обычные', 'обычный', 'x1'):
        return 1
    if name in ('2', 'x2', 'двойные', 'двойной', 'двойныеочки'):
        return 2
    if name in ('0', 'безочков', 'нет', 'x0'):
        return 0
    raise QuestionError('Очки: обычные, x2 или без очков')


def row_payload(get):
    """Turn one sheet row into an editor payload."""
    type = parse_type(get('type'))
    if type is None:
        raise QuestionError('Неизвестный тип «%s»' % cell_text(get('type'))[:40])
    if type == Question.PIN:
        raise QuestionError('Точку на картинке добавьте в редакторе: нужна картинка')
    time_text = cell_text(get('time'))
    try:
        time_limit = int(float(time_text.replace(',', '.'))) if time_text else 20
    except ValueError:
        raise QuestionError('Время: нужно число секунд')
    options = [cell_text(get('opt%d' % i)) for i in range(1, MAX_OPTIONS + 1)]
    while options and not options[-1]:
        options.pop()
    correct = cell_text(get('correct'))
    payload = {'type': type, 'text': cell_text(get('text')), 'code': cell_text(get('code')),
               'code_language': LANGUAGE_ALIASES.get(cell_text(get('lang')).lower(), ''),
               'time_limit': time_limit, 'weight': parse_weight(get('weight')),
               'explanation': cell_text(get('explanation')), 'data': {}, 'options': []}
    numbers = []
    if type in (Question.SINGLE, Question.MULTI) or (type == Question.CODE and options):
        for part in re.split(r'[,;\s]+', correct):
            if not part:
                continue
            if not part.isdigit() or not 1 <= int(part) <= len(options):
                raise QuestionError('Верные: номера вариантов от 1 до %d' % len(options))
            numbers.append(int(part))
        if not numbers:
            raise QuestionError('Укажите номер верного варианта')
        if type != Question.MULTI and len(numbers) > 1:
            raise QuestionError('Здесь только один верный вариант')
    if type == Question.TRUEFALSE:
        name = correct.lower().replace('ё', 'е')
        if name in ('верно', 'да', 'true', '1', '+', 'правда'):
            truth = True
        elif name in ('неверно', 'нет', 'false', '2', '-', 'ложь'):
            truth = False
        else:
            raise QuestionError('Верные: «Верно» или «Неверно»')
        payload['options'] = [{'text': TRUE_FALSE[0], 'is_correct': truth},
                              {'text': TRUE_FALSE[1], 'is_correct': not truth}]
    elif type in OPTION_LIMITS and (type != Question.CODE or options):
        if any(not text for text in options):
            raise QuestionError('Пустой вариант между заполненными')
        payload['options'] = [{'text': text, 'is_correct': n in numbers} for n, text in enumerate(options, 1)]
        low, high = OPTION_LIMITS[type]
        if not low <= len(options) <= high:
            raise QuestionError('Нужно от %d до %d вариантов' % (low, high))
    if type == Question.WORD:
        payload['data'] = {'word': correct or (options[0] if options else '')}
    elif type == Question.TEXT or (type == Question.CODE and not options):
        payload['data'] = {'answers': correct, 'tolerance': get('tolerance')}
        if type == Question.CODE:
            payload['data']['input'] = True
    elif type == Question.SLIDER:
        payload['data'] = {'min': get('min'), 'max': get('max'), 'step': get('step'), 'answer': correct,
                           'tolerance': get('tolerance'), 'unit': cell_text(get('unit'))}
    return payload


def read_rows(upload):
    """Yield (row number, payload or QuestionError) for every non-empty row of the first sheet."""
    from openpyxl import load_workbook

    if upload.size > MAX_FILE:
        raise QuestionError('Файл больше 2 МБ')
    try:
        book = load_workbook(BytesIO(upload.read(MAX_FILE + 1)), read_only=True, data_only=True)
    except Exception:
        raise QuestionError('Нужен файл Excel (.xlsx)')
    try:
        sheet = book.worksheets[0]
        rows = sheet.iter_rows(max_col=len(COLUMNS) + 6, values_only=True)
        header = next(rows, None)
        mapping = header_map(header or [])
        if 'type' not in mapping or 'text' not in mapping:
            raise QuestionError('В первой строке нужны заголовки из шаблона (Тип, Вопрос, ...)')
        result, count = [], 0
        for number, row in enumerate(rows, 2):
            if row is None or all(cell_text(v) == '' for v in row):
                continue
            count += 1
            if count > MAX_ROWS:
                raise QuestionError('Не больше %d строк за раз' % MAX_ROWS)

            def get(name, row=row):
                index = mapping.get(name)
                return row[index] if index is not None and index < len(row) else None
            try:
                result.append((number, clean_question(row_payload(get))))
            except QuestionError as e:
                result.append((number, e))
        return result
    finally:
        book.close()
