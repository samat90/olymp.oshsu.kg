"""Build the programming quizzes (content_prog.py) into <out>/<key>/: python3 build_prog.py <out>"""
import json, os, random, shutil, sys, hashlib
import cairosvg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pics
from content_prog import QUIZZES

OUT = sys.argv[1]
errors = []
for quiz in QUIZZES:
    key = quiz['key']
    d = os.path.join(OUT, key)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    qs = quiz['questions']
    if len(qs) != 50: errors.append('%s: %d questions' % (key, len(qs)))
    texts = set()
    out = []
    pos_count = {}
    n_single = sum(1 for q in qs if q['type'] in ('single', 'code'))
    slots = ([0, 1, 2, 3] * 30)[:n_single]
    random.Random(key).shuffle(slots)
    for i, q in enumerate(qs):
        rnd = random.Random(hashlib.md5(('%s-%d' % (key, i)).encode()).hexdigest())
        t = q['type']
        item = {'type': t, 'text': q['text'], 'time_limit': q['t'], 'weight': q['w'], 'explanation': q['expl'],
                'code': q['code'], 'code_language': q['lang'], 'data': {}, 'options': [], 'image': None}
        sig = q['text'] + q['code'] + '|'.join(map(str, q['opts']))
        if sig in texts: errors.append('%s #%d duplicate' % (key, i + 1))
        texts.add(sig)
        if t in ('single', 'code'):
            opts = q['opts']
            if len(opts) != 4 or len(set(opts)) != 4: errors.append('%s #%d options %r' % (key, i + 1, opts))
            others = [1, 2, 3]; rnd.shuffle(others)
            order = others[:]; order.insert(slots.pop(), 0)
            item['options'] = [{'text': opts[j], 'is_correct': j == 0} for j in order]
            pos = order.index(0); pos_count[pos] = pos_count.get(pos, 0) + 1
            if t == 'code': item['data'] = {'input': False}
        elif t == 'multi':
            opts = [(o.lstrip('*'), o.startswith('*')) for o in q['opts']]
            rnd.shuffle(opts)
            item['options'] = [{'text': a, 'is_correct': c} for a, c in opts]
            if not any(c for _, c in opts): errors.append('%s #%d multi no correct' % (key, i + 1))
        elif t == 'truefalse':
            v = q['opts'][0]
            item['options'] = [{'text': 'Верно', 'is_correct': v}, {'text': 'Неверно', 'is_correct': not v}]
        elif t == 'order':
            if not 3 <= len(q['opts']) <= 6: errors.append('%s #%d order size' % (key, i + 1))
            item['options'] = [{'text': o, 'is_correct': False} for o in q['opts']]
        elif t == 'text':
            item['data'] = {'answers': q['answers'], 'tolerance': 0}
        elif t == 'word':
            item['data'] = {'word': q['word']}
        else:
            errors.append('bad type')
        for o in item['options']:
            if len(o['text']) > 300: errors.append('long option')
        if len(item['text']) > 2000 or len(item['code']) > 4000: errors.append('long text')
        out.append(item)
    svg = pics.cover(key, '50 вопросов')
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(d, 'cover.png'), output_width=1200,
                     output_height=675)
    meta = {k: quiz[k] for k in ('key', 'title', 'subject', 'theme', 'description')}
    meta['cover'] = 'cover.png'
    meta['questions'] = out
    with open(os.path.join(d, 'quiz.json'), 'w') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(key, len(out), 'correct positions', dict(sorted(pos_count.items())),
          'weights', {w: sum(1 for x in out if x['weight'] == w) for w in (0, 1, 2)},
          'types', {t: sum(1 for x in out if x['type'] == t) for t in sorted(set(x['type'] for x in out))})
print('ERRORS', errors)
