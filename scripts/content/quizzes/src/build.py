import json, os, random, shutil, sys, hashlib
import cairosvg
sys.path.insert(0, os.path.dirname(__file__))
import pics
from content_a import INFORMATIKA, MATEMATIKA, FIZIKA
from content_b import HIMIYA, BIOLOGIYA, ISTORIYA
from content_c import GEOGRAFIYA, LITERATURA, ENGLISH

QUIZZES = [INFORMATIKA, MATEMATIKA, FIZIKA, HIMIYA, BIOLOGIYA, ISTORIYA, GEOGRAFIYA, LITERATURA, ENGLISH]
EXTRA = {
    'clocks_time_zone': lambda: pics.two_clocks(15, 0, 9, 0, 'Бишкек', 'Лондон'),
    'clock_3': lambda: pics.one_clock(3, 0),
    'clock_730': lambda: pics.one_clock(7, 30),
}
OUT = sys.argv[1]

def render(name, dest):
    fn = EXTRA.get(name) or getattr(pics, name)
    svg = fn()
    open(dest[:-4] + '.svg', 'w').write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=dest, output_width=1200, output_height=675)

errors = []
shutil.rmtree(OUT, ignore_errors=True)
for quiz in QUIZZES:
    key = quiz['key']
    d = os.path.join(OUT, key); os.makedirs(d)
    want = 50 if key == 'english50' else 30
    qs = quiz['questions']
    if len(qs) != want: errors.append('%s: %d questions' % (key, len(qs)))
    texts = set()
    out = []
    pos_count = {}
    n_single = sum(1 for q in qs if q['type'] in ('single', 'code'))
    slots = ([0, 1, 2, 3] * 30)[:n_single]
    random.Random(key).shuffle(slots)
    for i, q in enumerate(qs):
        rnd = random.Random(hashlib.md5(('%s-%d' % (key, i)).encode()).hexdigest())
        t = q['type']
        item = {'type': t, 'text': q['text'], 'time_limit': q['t'], 'weight': 1, 'explanation': q['expl'],
                'code': q['code'], 'code_language': q['lang'], 'data': {}, 'options': [], 'image': None}
        sig = q['text'] + q['code'] + (q['img'] or '') + '|'.join(map(str, q['opts']))
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
        if len(item['text']) > 2000: errors.append('long text')
        if q['img']:
            fname = 'q%02d_%s.png' % (i + 1, q['img'])
            render(q['img'], os.path.join(d, fname))
            item['image'] = fname
        out.append(item)
    cover = 'cover.png'
    svg = pics.cover(key, '%d вопросов' % want if key != 'english50' else '50 questions')
    open(os.path.join(d, 'cover.svg'), 'w').write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(d, cover), output_width=1200, output_height=675)
    meta = {k: quiz[k] for k in ('key', 'title', 'subject', 'theme', 'description')}
    meta['cover'] = cover; meta['questions'] = out
    json.dump(meta, open(os.path.join(d, 'quiz.json'), 'w'), ensure_ascii=False, indent=1)
    print(key, len(out), 'imgs', sum(1 for x in out if x['image']), 'correct positions', dict(sorted(pos_count.items())),
          'types', {t: sum(1 for x in out if x['type'] == t) for t in set(x['type'] for x in out)})
print('ERRORS', errors)
