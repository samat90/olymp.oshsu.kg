"""Find sample tests in a problem statement written in Markdown.

Statements on the site look like this:

    ## Пример
    **Ввод**
    ```
    5
    ```
    **Вывод**
    ```
    15
    ```

Labels may be in Russian, Kyrgyz or English and may be headings instead of
bold text. A fenced block right after an input label is a sample input; the
next fenced block after an output label is its answer.
"""
import re

INPUT_LABELS = ('ввод', 'вход', 'входные данные', 'пример ввода', 'пример входных данных', 'входные',
                'киргизүү', 'кирүү', 'input', 'sample input', 'stdin')
OUTPUT_LABELS = ('вывод', 'выход', 'выходные данные', 'пример вывода', 'пример выходных данных', 'выходные',
                 'чыгаруу', 'output', 'sample output', 'stdout')

FENCE = re.compile(r'^(```|~~~)[^\n]*\n(.*?)^\1[ \t]*$', re.M | re.S)
LABEL = re.compile(r'^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*|__)?[ \t]*([^\n*_#]{1,60}?)'
                   r'[ \t]*(?:\*\*|__)?[ \t]*:?[ \t]*$', re.M)


def _label_kind(text):
    text = re.sub(r'\s*\d+\s*$', '', text.strip().lower().rstrip(':').strip())
    if text in INPUT_LABELS:
        return 'in'
    if text in OUTPUT_LABELS:
        return 'out'
    return None


def extract_samples(markdown):
    """Return a list of {'input': str, 'output': str}."""
    if not markdown:
        return []
    markdown = markdown.replace('\r\n', '\n')
    samples = []
    pending_input = None
    pos = 0
    for block in FENCE.finditer(markdown):
        before = markdown[pos:block.start()]
        pos = block.end()
        labels = [m.group(1) for m in LABEL.finditer(before)]
        kind = None
        for label in reversed(labels):
            kind = _label_kind(label)
            if kind:
                break
        body = block.group(2)
        if kind == 'in':
            pending_input = body
        elif kind == 'out' and pending_input is not None:
            samples.append({'input': pending_input, 'output': body})
            pending_input = None
    return samples
