"""Write quiz.json for every themed quiz from the question sources (content.py) and the downloaded pictures.

Usage: python build_themed.py <quizzes folder>
Run fetch_images.py first. A question whose picture is missing keeps its text only. Picture credits
(author, licence, Wikimedia Commons) are added to the question's explanation, shown after the answer.
"""
import hashlib, json, os, random, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import QUIZZES

TYPES = {'single', 'code', 'truefalse', 'multi', 'order', 'word', 'text', 'slider'}


def credit_line(c):
    # Site markdown: only *...* makes italics; brackets in a URL end the link early; _ * [ ] in a name break it.
    author = re.sub(r'[_*\[\]]', ' ', c.get('author') or '').strip()
    author = re.sub(r'\s*\(talk\b[^)]*\)', '', author).strip()
    if not author or author.lower().startswith('unknown'):
        author = 'автор неизвестен'
    lic = re.sub(r'[_*\[\]]', ' ', c.get('license') or '').strip()
    page = c.get('page', '').replace('(', '%28').replace(')', '%29')
    site = 'Wikimedia Commons' if 'commons.wikimedia.org' in page else 'Wikipedia'
    return '*Фото: %s, %s, [%s](%s)*' % (author, lic, site, page)


def build(quiz, out, errors):
    key = quiz['key']
    folder = os.path.join(out, key)
    cpath = os.path.join(folder, 'credits.json')
    credits = json.load(open(cpath, encoding='utf-8')) if os.path.exists(cpath) else {}
    qs = quiz['questions']
    if len(qs) not in (25, 50):
        errors.append('%s: %d questions' % (key, len(qs)))
    n_single = sum(1 for q in qs if q['type'] in ('single', 'code'))
    slots = ([0, 1, 2, 3] * 10)[:n_single]
    random.Random(key).shuffle(slots)
    seen = set()
    items = []
    for i, q in enumerate(qs):
        rnd = random.Random(hashlib.md5(('%s-%d' % (key, i)).encode()).hexdigest())
        t = q['type']
        if t not in TYPES:
            errors.append('%s #%d type %s' % (key, i + 1, t))
        sig = q['text'] + '|' + (q['img'] or '') + '|' + q.get('code', '')
        if sig in seen:
            errors.append('%s #%d duplicate question' % (key, i + 1))
        seen.add(sig)
        item = {'type': t, 'text': q['text'], 'time_limit': q['t'], 'weight': q['w'], 'explanation': q['e'],
                'code': '', 'code_language': '', 'data': {}, 'options': [], 'image': None}
        if t == 'code':
            item['code'] = q['code'].strip('\n')
            item['code_language'] = q['lang']
            item['data'] = {'input': False}
        if t in ('single', 'code'):
            opts = q['opts']
            if len(set(opts)) != 4:
                errors.append('%s #%d options %r' % (key, i + 1, opts))
            others = [1, 2, 3]
            rnd.shuffle(others)
            order = others[:]
            order.insert(slots.pop(), 0)
            item['options'] = [{'text': opts[j], 'is_correct': j == 0} for j in order]
        elif t == 'multi':
            opts = [(o.lstrip('*'), o.startswith('*')) for o in q['opts']]
            if not 2 <= len(opts) <= 6 or not any(c for _, c in opts):
                errors.append('%s #%d multi' % (key, i + 1))
            rnd.shuffle(opts)
            item['options'] = [{'text': a, 'is_correct': c} for a, c in opts]
        elif t == 'truefalse':
            v = bool(q['opts'][0])
            item['options'] = [{'text': 'Верно', 'is_correct': v}, {'text': 'Неверно', 'is_correct': not v}]
        elif t == 'order':
            if not 3 <= len(q['opts']) <= 6:
                errors.append('%s #%d order size' % (key, i + 1))
            item['options'] = [{'text': o, 'is_correct': False} for o in q['opts']]
        elif t == 'word':
            word = q['word'].upper()
            if len(word) > 24 or ' ' in word:
                errors.append('%s #%d word' % (key, i + 1))
            item['data'] = {'word': word}
        elif t == 'text':
            item['data'] = {'answers': q['answers'], 'tolerance': 0}
        elif t == 'slider':
            s = q['slider']
            if not (s['min'] < s['max'] and s['min'] <= s['answer'] <= s['max']):
                errors.append('%s #%d slider' % (key, i + 1))
            item['data'] = s
        for o in item['options']:
            if len(o['text']) > 300:
                errors.append('%s #%d long option' % (key, i + 1))
        fname = 'q%02d.jpg' % (i + 1)
        if q['img'] and fname in credits and os.path.exists(os.path.join(folder, fname)):
            item['image'] = fname
            line = credit_line(credits[fname])
            item['explanation'] = (item['explanation'] + '\n\n' + line).strip()
        items.append(item)
    spec = {'key': key, 'title': quiz['title'], 'subject': quiz['subject'], 'theme': quiz['theme'],
            'description': quiz['description'] + ' Фото: Wikimedia Commons, свободные лицензии (авторы указаны в пояснениях).',
            'cover': 'cover.jpg' if 'cover.jpg' in credits and os.path.exists(os.path.join(folder, 'cover.jpg')) else None,
            'questions': items}
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, 'quiz.json'), 'w', encoding='utf-8') as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
    return sum(1 for it in items if it['image'])


def main():
    out = sys.argv[1]
    errors = []
    keys = set()
    for quiz in QUIZZES:
        if quiz['key'] in keys:
            errors.append('duplicate key ' + quiz['key'])
        if len(quiz['key']) > 12:
            errors.append('key longer than 12 characters: ' + quiz['key'])
        keys.add(quiz['key'])
        n = build(quiz, out, errors)
        print('%s: %d pictures' % (quiz['key'], n))
    print('\n'.join(errors) or 'OK, %d quizzes' % len(QUIZZES))
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
