"""Download free pictures for the themed quizzes from Wikimedia (Wikipedia/Commons).

Usage: python fetch_images.py <quizzes folder> [<review folder>] [key ...]
Each question's img spec is 'en:Article' (the article's lead FREE picture), 'ru:Статья', or 'c:File name'
(an exact Wikimedia Commons file; if it does not exist the best Commons search hit is used).
Pictures are shrunk to 800 px JPEG, saved as <key>/qNN.jpg (cover.jpg for the cover), and the author and licence
go to <key>/credits.json. Already downloaded pictures are skipped. A contact sheet per quiz goes to the review folder.
Only freely licensed files are accepted (public domain, CC0, CC BY, CC BY-SA, GFDL).
"""
import io, json, os, re, sys, time, urllib.parse, urllib.request
from html import unescape
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import QUIZZES

UA = 'OlympQuizBuilder/1.0 (https://olymp.oshsu.kg; quiz pictures for a school site)'
FREE = re.compile(r'public domain|^pd|cc0|cc[ -]by|gfdl|attribution|no restrictions|copyrighted free use|free art|ogl|fal|free art license', re.I)
SPACE_AGENCY = re.compile(r'nasa|jpl|\besa\b', re.I)
WIDTH = 800


def get(url, tries=4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read()
        except Exception as e:
            if attempt == tries - 1:
                raise
            time.sleep(2 + attempt * 3)


def api(host, **params):
    params.update(format='json', formatversion='2')
    time.sleep(0.25)
    return json.loads(get('https://%s/w/api.php?%s' % (host, urllib.parse.urlencode(params))))


def clean(html):
    text = unescape(re.sub(r'<[^>]+>', '', html or '')).strip()
    return re.sub(r'\s+', ' ', text)[:120]


def imageinfo(host, filename):
    data = api(host, action='query', titles='File:' + filename, prop='imageinfo',
               iiprop='url|extmetadata|mime', iiurlwidth=WIDTH)
    page = data['query']['pages'][0]
    if page.get('missing') and not page.get('known'):
        return None
    info = (page.get('imageinfo') or [None])[0]
    if not info:
        return None
    meta = info.get('extmetadata', {})
    lic = clean(meta.get('LicenseShortName', {}).get('value', ''))
    return {'file': page['title'][5:], 'thumb': info.get('thumburl') or info['url'], 'license': lic,
            'author': clean(meta.get('Artist', {}).get('value', '')) or clean(meta.get('Credit', {}).get('value', '')),
            'page': info.get('descriptionurl', ''), 'mime': info.get('mime', '')}


def commons_search(words):
    data = api('commons.wikimedia.org', action='query', list='search', srnamespace=6, srlimit=5,
               srsearch=words + ' filetype:bitmap|drawing')
    for hit in data['query']['search']:
        name = hit['title'][5:]
        if re.search(r'\.(jpe?g|png|svg|webp|gif|tiff?)$', name, re.I):
            return name
    return None


def resolve(spec):
    kind, _, name = spec.partition(':')
    if kind == 'c':
        info = imageinfo('commons.wikimedia.org', name)
        if info is None:
            hit = commons_search(re.sub(r'\.[a-z]+$', '', name, flags=re.I))
            info = hit and imageinfo('commons.wikimedia.org', hit)
            if info:
                info['note'] = 'search'
        return info
    host = '%s.wikipedia.org' % kind
    data = api(host, action='query', titles=name, prop='pageimages', piprop='name', pilicense='free', redirects=1)
    page = data['query']['pages'][0]
    fname = page.get('pageimage')
    if not fname:
        hit = commons_search(name)
        info = hit and imageinfo('commons.wikimedia.org', hit)
        if info:
            info['note'] = 'search'
        return info
    return imageinfo(host, fname)


def shrink(raw):
    image = Image.open(io.BytesIO(raw))
    image.load()
    if image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGBA')
        bg = Image.new('RGB', image.size, (255, 255, 255))
        bg.paste(image, mask=image.getchannel('A'))
        image = bg
    image = image.convert('RGB')
    image.thumbnail((WIDTH, WIDTH), Image.LANCZOS)
    for q in (82, 75, 68, 60, 52):
        buf = io.BytesIO()
        image.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
        if buf.tell() <= 90 * 1024:
            break
    return buf.getvalue(), image


def sheet(key, items, folder):
    if not items:
        return
    cols, cw, ch = 5, 260, 230
    rows = (len(items) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * cw, rows * ch), (240, 240, 240))
    draw = ImageDraw.Draw(canvas)
    for i, (label, image) in enumerate(items):
        x, y = (i % cols) * cw, (i // cols) * ch
        im = image.copy()
        im.thumbnail((cw - 10, ch - 34))
        canvas.paste(im, (x + 5, y + 5))
        draw.text((x + 5, y + ch - 26), label[:44], fill=(0, 0, 0))
    canvas.save(os.path.join(folder, key + '.jpg'), quality=80)


def main():
    out = sys.argv[1]
    review = sys.argv[2] if len(sys.argv) > 2 else None
    only = set(sys.argv[3:])
    if review:
        os.makedirs(review, exist_ok=True)
    report = []
    for quiz in QUIZZES:
        key = quiz['key']
        if only and key not in only:
            continue
        folder = os.path.join(out, key)
        os.makedirs(folder, exist_ok=True)
        cpath = os.path.join(folder, 'credits.json')
        credits = json.load(open(cpath, encoding='utf-8')) if os.path.exists(cpath) else {}
        jobs = [('cover.jpg', quiz['cover'])] + [('q%02d.jpg' % (i + 1), q['img'])
                                                 for i, q in enumerate(quiz['questions']) if q['img']]
        thumbs = []
        for fname, spec in jobs:
            dest = os.path.join(folder, fname)
            if os.path.exists(dest) and credits.get(fname, {}).get('spec') == spec:
                thumbs.append(('%s %s' % (fname[:-4], credits[fname]['file'][:30]), Image.open(dest)))
                continue
            try:
                info = resolve(spec)
                if info is None:
                    report.append('%s %s: NOT FOUND %s' % (key, fname, spec))
                    continue
                if not info['license'] and (SPACE_AGENCY.search(info['file']) or SPACE_AGENCY.search(info['author'])):
                    info['license'] = 'Public domain (NASA)'
                if not FREE.search(info['license'] or ''):
                    report.append('%s %s: NOT FREE (%s) %s' % (key, fname, info['license'], info['file']))
                    continue
                data, image = shrink(get(info['thumb']))
                with open(dest, 'wb') as f:
                    f.write(data)
                info['spec'] = spec
                credits[fname] = info
                thumbs.append(('%s %s' % (fname[:-4], info['file'][:30]), image))
                if info.get('note'):
                    report.append('%s %s: by search -> %s' % (key, fname, info['file']))
            except Exception as e:
                report.append('%s %s: ERROR %s %s' % (key, fname, spec, e))
        with open(cpath, 'w', encoding='utf-8') as f:
            json.dump(credits, f, ensure_ascii=False, indent=1, sort_keys=True)
        if review:
            sheet(key, thumbs, review)
        print('%s: %d/%d pictures' % (key, len(thumbs), len(jobs)), flush=True)
    print('\n'.join(report))
    if review:
        with open(os.path.join(review, 'report.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))


if __name__ == '__main__':
    main()
