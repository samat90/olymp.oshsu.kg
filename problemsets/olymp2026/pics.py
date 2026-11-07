#!/usr/bin/env python3
"""Draw the SVG pictures for the statements:  python3 pics.py [problem ...]
Every function writes <problem>/img/<file>.svg; the pictures are plain SVG, no external files."""
import math
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT = 'font-family="Segoe UI, Arial, sans-serif"'
PICS = {}


def pic(problem, name):
    def wrap(fn):
        PICS.setdefault(problem, []).append((name, fn))
        return fn
    return wrap


def svg(w, h, body, bg='#f6f8fb'):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" %s>\n'
            '<rect width="%d" height="%d" rx="10" fill="%s"/>\n%s\n</svg>\n' % (w, h, w, h, FONT, w, h, bg, body))


def text(x, y, s, size=13, color='#24364a', anchor='middle', weight='normal'):
    return '<text x="%.1f" y="%.1f" font-size="%d" fill="%s" text-anchor="%s" font-weight="%s">%s</text>' % (
        x, y, size, color, anchor, weight, s)


def node(x, y, label, fill='#2e86c1', r=15, color='#fff'):
    return ('<circle cx="%.1f" cy="%.1f" r="%d" fill="%s" stroke="#1b4f72" stroke-width="1.5"/>' % (x, y, r, fill) +
            text(x, y + 4.5, label, 13, color, weight='bold'))


def edge(x1, y1, x2, y2, label=None, color='#7f8c8d', width=2, arrow=False, r=15, dash=False):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    ax, ay = x1 + dx / L * r, y1 + dy / L * r
    bx, by = x2 - dx / L * (r + (4 if arrow else 0)), y2 - dy / L * (r + (4 if arrow else 0))
    s = '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%s"%s%s/>' % (
        ax, ay, bx, by, color, width, ' marker-end="url(#arr)"' if arrow else '',
        ' stroke-dasharray="6 4"' if dash else '')
    if label is not None:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        s += ('<rect x="%.1f" y="%.1f" width="%d" height="17" rx="4" fill="#fff" opacity="0.9"/>' %
              (mx - 4 - 3.6 * len(str(label)), my - 9, 8 + 7.2 * len(str(label))) + text(mx, my + 4.5, label, 12))
    return s


ARROW = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
         'orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#555"/></marker></defs>')


def graph(w, h, pos, edges, directed=False, colors=None, extra=''):
    """pos: {label: (x, y)}, edges: [(a, b, label or None)]"""
    body = ARROW if directed else ''
    for e in edges:
        a, b = e[0], e[1]
        lab = e[2] if len(e) > 2 else None
        col = e[3] if len(e) > 3 else '#7f8c8d'
        body += edge(pos[a][0], pos[a][1], pos[b][0], pos[b][1], lab, col, arrow=directed)
    for v, (x, y) in pos.items():
        body += node(x, y, v, (colors or {}).get(v, '#2e86c1'))
    return svg(w, h, body + extra)


# ---------------------------------------------------------------- fractals

@pic('sierpinski', 'sierpinski.svg')
def sierpinski():
    k, cell = 2, 36
    n = 3 ** k
    body = []
    for i in range(n):
        for j in range(n):
            x, y, f = i, j, True
            while x or y:
                if x % 3 == 1 and y % 3 == 1:
                    f = False
                x //= 3
                y //= 3
            body.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="#fff" stroke-width="1"/>' % (
                40 + j * cell, 40 + i * cell, cell, cell, '#b03a2e' if f else '#f3e5c8'))
    for i in range(n):
        body.append(text(40 + i * cell + cell / 2, 32, i, 11, '#555'))
        body.append(text(30, 40 + i * cell + cell / 2 + 4, i, 11, '#555'))
    body.append('<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#1f618d" stroke-width="3"/>' % (
        40 + 0 * cell, 40 + 1 * cell, 3 * cell, 4 * cell))
    return svg(40 + n * cell + 20, 40 + n * cell + 20, '\n'.join(body))


@pic('dragon', 'dragon.svg')
def dragon():
    N = 1 << 10
    x = y = 0
    dx, dy = 1, 0
    pts = [(0, 0)]
    for n in range(1, N + 1):
        x += dx
        y += dy
        pts.append((x, y))
        m = n
        while m % 2 == 0:
            m //= 2
        if ((m - 1) // 2) % 2 == 0:
            dx, dy = -dy, dx
        else:
            dx, dy = dy, -dx
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    sc = 9
    W, H = (max(xs) - min(xs)) * sc + 60, (max(ys) - min(ys)) * sc + 60
    ox, oy = 30 - min(xs) * sc, 30 + max(ys) * sc
    body = []
    cols = ['#c0392b', '#d35400', '#d68910', '#27ae60', '#16a085', '#2e86c1', '#7d3c98', '#34495e']
    for i in range(N):
        a, b = pts[i], pts[i + 1]
        body.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % (
            ox + a[0] * sc, oy - a[1] * sc, ox + b[0] * sc, oy - b[1] * sc, cols[i * len(cols) // N]))
    body.append('<circle cx="%d" cy="%d" r="6" fill="#000"/>' % (ox, oy))
    body.append(text(ox + 10, oy + 20, '(0, 0)', 13, '#000', 'start', 'bold'))
    body.append(text(W - 20, H - 12, 'первые 1024 отрезка', 12, '#555', 'end'))
    return svg(W, H, '\n'.join(body))


@pic('pascalmod', 'pascal.svg')
def pascal():
    rows, p, cell = 81, 3, 6
    W = rows * cell + 40
    body = []
    row = [1]
    for n in range(rows):
        for k, v in enumerate(row):
            x = 20 + (rows - n) * cell / 2 + k * cell
            y = 20 + n * cell * 0.87
            body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (
                x, y, cell - 0.6, cell * 0.87 - 0.6, '#1f3a5f' if v == 0 else '#f0c75e'))
        row = [1] + [(row[i] + row[i + 1]) % p for i in range(len(row) - 1)] + [1]
    return svg(W, int(rows * cell * 0.87 + 40), '\n'.join(body))


@pic('thuemorse', 'thuemorse.svg')
def thuemorse():
    n, w = 64, 8
    body = []
    for i in range(n):
        t = bin(i).count('1') & 1
        body.append('<rect x="%d" y="30" width="%d" height="90" fill="%s" stroke="#fff" stroke-width="0.5"/>' % (
            20 + i * w, w, '#5b3a29' if t else '#efe0c4'))
    for b in (1, 2, 4, 8, 16, 32, 64):
        x = 20 + b * w
        body.append('<line x1="%d" y1="24" x2="%d" y2="126" stroke="#c0392b" stroke-width="1.5"/>' % (x, x))
        body.append(text(x, 142, b, 11, '#c0392b'))
    body.append(text(20, 18, 't[0] … t[63]', 12, '#24364a', 'start'))
    return svg(n * w + 40, 155, '\n'.join(body))


def hilbert_pts(k):
    n = 1 << k
    pts = []
    for d in range(n * n):
        x = y = 0
        s, t = 1, d
        while s < n:
            rx = 1 & (t // 2)
            ry = 1 & (t ^ rx)
            if ry == 0:
                if rx == 1:
                    x, y = s - 1 - x, s - 1 - y
                x, y = y, x
            x += s * rx
            y += s * ry
            t //= 4
            s *= 2
        pts.append((x, y))
    return pts


@pic('hilbert', 'hilbert.svg')
def hilbert():
    body = []
    size = 150
    for idx, k in enumerate((1, 2, 3)):
        n = 1 << k
        c = size / n
        ox, oy = 20 + idx * (size + 30), 20
        for i in range(n):
            for j in range(n):
                body.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#e8f3e2" stroke="#b9d6ad"/>' % (
                    ox + i * c, oy + (n - 1 - j) * c, c, c))
        pts = hilbert_pts(k)
        path = ' '.join('%s%.1f %.1f' % ('M' if i == 0 else 'L', ox + x * c + c / 2, oy + (n - 1 - y) * c + c / 2)
                        for i, (x, y) in enumerate(pts))
        body.append('<path d="%s" fill="none" stroke="#1e8449" stroke-width="3" stroke-linejoin="round"/>' % path)
        if k <= 2:
            for d, (x, y) in enumerate(pts):
                body.append(text(ox + x * c + c / 2 + (0 if k == 1 else 9), oy + (n - 1 - y) * c + c / 2 - 6,
                                 d, 12 if k == 1 else 10, '#7b241c', weight='bold'))
        body.append(text(ox + size / 2, oy + size + 22, 'порядок %d' % k, 13))
    return svg(3 * size + 100, size + 60, '\n'.join(body))


def curve(x1, y1, x2, y2, bend=30, label=None, color='#555', r=15):
    """Directed arc bent to the left of the direction x1 -> x2."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    cx, cy = mx - dy / L * bend, my + dx / L * bend
    # shorten both ends by r along the tangents
    def cut(px, py, qx, qy, d):
        l = math.hypot(qx - px, qy - py) or 1
        return px + (qx - px) / l * d, py + (qy - py) / l * d
    ax, ay = cut(x1, y1, cx, cy, r)
    bx, by = cut(x2, y2, cx, cy, r + 4)
    s = '<path d="M%.1f %.1f Q%.1f %.1f %.1f %.1f" fill="none" stroke="%s" stroke-width="2" marker-end="url(#arr)"/>' % (
        ax, ay, cx, cy, bx, by, color)
    if label is not None:
        s += text((mx + cx) / 2, (my + cy) / 2 + 4, label, 12, color, weight='bold')
    return s


def loop(x, y, label=None, r=15):
    return ('<path d="M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f" fill="none" stroke="#555" stroke-width="2" '
            'marker-end="url(#arr)"/>' % (x - 8, y - r + 2, x - 30, y - 60, x + 30, y - 60, x + 9, y - r - 2) +
            (text(x, y - 50, label, 12, '#555', weight='bold') if label else ''))


# ---------------------------------------------------------------- graphs

@pic('mstcount', 'mstcount.svg')
def mstcount():
    pos = {'1': (70, 70), '2': (70, 230), '3': (220, 150), '4': (360, 230)}
    E = [('1', '2', 1, '#1e8449'), ('2', '3', 1, '#1e8449'), ('1', '3', 1, '#1e8449'), ('3', '4', 2, '#c0392b'),
         ('2', '4', 3, '#95a5a6')]
    extra = text(210, 285, 'любые два зелёных канала + красный', 13)
    return graph(420, 300, pos, E, extra=extra)


@pic('best', 'best.svg')
def best():
    P = {'1': (230, 170), '2': (80, 120), '3': (380, 120)}
    body = ARROW
    body += curve(*P['1'], *P['2'], 25, '1') + curve(*P['2'], *P['1'], 25, '2')
    body += curve(*P['1'], *P['3'], 25, '3') + curve(*P['3'], *P['1'], 25, '4')
    body += loop(*P['1'], '5')
    for v, (x, y) in P.items():
        body += node(x, y, v, '#d68910')
    body += text(230, 225, 'маршрут: 1, 2, затем 3, 4 и 5 в любом порядке', 13)
    return svg(460, 245, body)


@pic('dilworth', 'dilworth.svg')
def dilworth():
    pos = {'1': (80, 50), '3': (240, 110), '2': (80, 170), '4': (160, 230), '5': (80, 320), '6': (260, 320)}
    E = [('1', '2', None, '#2e86c1'), ('2', '4', None, '#2e86c1'), ('4', '5', None, '#2e86c1'),
         ('1', '3', None, '#bdc3c7'), ('3', '4', None, '#c0392b'), ('4', '6', None, '#c0392b')]
    extra = text(300, 30, 'выше', 12, '#555') + text(300, 345, 'ниже', 12, '#555')
    return graph(340, 360, pos, E, directed=True, extra=extra,
                 colors={'1': '#2e86c1', '2': '#2e86c1', '5': '#2e86c1', '3': '#c0392b', '6': '#c0392b', '4': '#7d3c98'})


@pic('closure', 'closure.svg')
def closure():
    pos = {'1': (70, 60), '2': (330, 60), '3': (70, 200), '4': (200, 200), '5': (330, 200)}
    prof = {'1': '+12', '2': '+3', '3': '−5', '4': '−3', '5': '−8'}
    E = [('1', '3'), ('1', '4'), ('2', '5'), ('3', '4')]
    extra = ''.join(text(x + 26, y - 18, prof[v], 13, '#1e8449' if prof[v][0] == '+' else '#c0392b', 'start', 'bold')
                    for v, (x, y) in pos.items())
    extra += text(200, 255, 'стрелка a → b: проект a требует проекта b', 13)
    return graph(420, 275, pos, E, directed=True, extra=extra,
                 colors={'1': '#1e8449', '3': '#1e8449', '4': '#1e8449', '2': '#95a5a6', '5': '#95a5a6'})


@pic('twosat', 'twosat.svg')
def twosat():
    body = ('<rect x="40" y="95" width="380" height="50" rx="8" fill="#e9dcc3" stroke="#8a6d3b" stroke-width="2"/>' +
            text(230, 125, 'дастархан', 14, '#5b3a29', weight='bold') +
            text(120, 30, 'сторона жениха (0)', 13, '#1f618d', weight='bold') +
            text(340, 30, 'сторона невесты (1)', 13, '#922b21', weight='bold'))
    body += node(90, 65, '1', '#2e86c1') + node(150, 65, '3', '#2e86c1') + node(320, 65, '2', '#c0392b')
    body += text(230, 180, 'пожелания: (2 = 1 или 3 = 1), (1 = 1 или 3 = 0), (2 = 0 или 1 = 0)', 12)
    body += text(230, 202, 'ответ: 010', 13, '#24364a', weight='bold')
    return svg(460, 220, body)


# ---------------------------------------------------------------- probability, number theory

@pic('necklace', 'necklace.svg')
def necklace():
    cols = {'a': '#c0392b', 'b': '#2e86c1', 'c': '#f1c40f'}
    body = ''
    for idx, word in enumerate(('abcabc', 'acbacb')):
        cx, cy = 110 + idx * 240, 110
        body += '<circle cx="%d" cy="%d" r="62" fill="none" stroke="#8a6d3b" stroke-width="2"/>' % (cx, cy)
        for i, ch in enumerate(word):
            a = -math.pi / 2 + 2 * math.pi * i / 6
            body += '<circle cx="%.1f" cy="%.1f" r="17" fill="%s" stroke="#333" stroke-width="1.5"/>' % (
                cx + 62 * math.cos(a), cy + 62 * math.sin(a), cols[ch])
    body += ARROW + '<path d="M190 110 L270 110" stroke="#555" stroke-width="2" marker-end="url(#arr)"/>'
    body += text(230, 98, 'переворот', 12)
    body += text(230, 205, 'разные бусы, но один и тот же браслет', 13)
    return svg(460, 225, body)


@pic('primegcd', 'primegcd.svg')
def primegcd():
    n, c = 12, 26
    pr = {2, 3, 5, 7, 11}
    body = ''
    for x in range(1, n + 1):
        for y in range(1, n + 1):
            g = math.gcd(x, y)
            body += '<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="#fff"/>' % (
                40 + (y - 1) * c, 30 + (x - 1) * c, c, c, '#27ae60' if g in pr else '#ecf0f1')
            if g in pr:
                body += text(40 + (y - 1) * c + c / 2, 30 + (x - 1) * c + c / 2 + 4, g, 10, '#fff')
    for i in range(1, n + 1):
        body += text(40 + (i - 1) * c + c / 2, 24, i, 10, '#555') + text(30, 30 + (i - 1) * c + c / 2 + 4, i, 10, '#555')
    body += text(40 + n * c / 2, 30 + n * c + 22, 'x — строки, y — столбцы; зелёные пары простые', 12)
    return svg(n * c + 60, n * c + 65, body)


@pic('lambwalk', 'lambwalk.svg')
def lambwalk():
    pos = {'1': (60, 110), '2': (200, 110), '3': (340, 110)}
    body = ''
    body += '<line x1="75" y1="110" x2="185" y2="110" stroke="#8a6d3b" stroke-width="4"/>'
    body += '<line x1="215" y1="110" x2="325" y2="110" stroke="#8a6d3b" stroke-width="6"/>'
    body += text(130, 100, 'w = 2', 12) + text(270, 100, 'w = 3', 12)
    body += ARROW + curve(200, 110, 60, 110, 45, '2/5', '#c0392b') + curve(200, 110, 340, 110, -45, '3/5', '#1e8449')
    for v, (x, y) in pos.items():
        body += node(x, y, v, '#27ae60' if v == '1' else '#2e86c1')
    body += text(200, 200, 'с поляны 2: вероятность пропорциональна ширине тропы', 12)
    return svg(400, 220, body)


@pic('components2', 'components2.svg')
def components2():
    pos = {str(i): (60 + 80 * (i - 1), 70 + (40 if i in (3, 6) else 0)) for i in range(1, 8)}
    lit = {'1', '2', '4', '6', '7'}
    E = [('1', '2'), ('2', '3'), ('3', '4'), ('4', '5'), ('3', '6'), ('6', '7')]
    E = [(a, b, None, '#f1c40f' if a in lit and b in lit else '#bdc3c7') for a, b in E]
    extra = text(300, 175, 'горят 1, 2, 4, 6, 7: островки {1, 2}, {4}, {6, 7} — C = 3', 13)
    return graph(600, 195, pos, E, colors={v: '#f39c12' if v in lit else '#7f8c8d' for v in pos}, extra=extra)


@pic('ruin', 'ruin.svg')
def ruin():
    N = 6
    body = ARROW
    for i in range(N + 1):
        x = 50 + i * 75
        fill = '#c0392b' if i in (0, N) else ('#2e86c1' if i != 2 else '#d68910')
        body += node(x, 80, str(i), fill, 18)
        if 0 < i < N:
            body += curve(x, 80, x + 75, 80, -28, 'x/y', '#1e8449', 18)
            body += curve(x, 80, x - 75, 80, -28, '', '#922b21', 18)
    body += text(275, 150, 'число ашыков у Айбека; в 0 и a + b игра заканчивается', 13)
    return svg(560, 170, body)


@pic('wythoff', 'wythoff.svg')
def wythoff():
    n, c = 13, 26
    lose = set()
    k = 0
    while True:
        a = (k + math.isqrt(5 * k * k)) // 2
        if a >= n:
            break
        lose.add((a, a + k))
        lose.add((a + k, a))
        k += 1
    body = ''
    for a in range(n):
        for b in range(n):
            body += '<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="#fff"/>' % (
                40 + b * c, 30 + (n - 1 - a) * c, c, c, '#c0392b' if (a, b) in lose else '#eaf2f8')
    for i in range(n):
        body += text(40 + i * c + c / 2, 30 + n * c + 14, i, 10, '#555') + text(30, 30 + (n - 1 - i) * c + c / 2 + 4, i, 10, '#555')
    body += text(40 + n * c / 2, 30 + n * c + 34, 'красные клетки (a, b) — проигрышные позиции', 12)
    return svg(n * c + 60, n * c + 75, body)


@pic('hackenbush', 'hackenbush.svg')
def hackenbush():
    body = '<rect x="0" y="230" width="420" height="40" fill="#a3d977"/>'
    body += text(210, 258, 'земля (вершина 0)', 13, '#2d572c', weight='bold')
    pts = {1: (130, 170), 2: (130, 110), 3: (130, 50), 4: (300, 170)}
    par = {1: (130, 230), 2: pts[1], 3: pts[2], 4: (300, 230)}
    for v, (x, y) in pts.items():
        px, py = par[v]
        col = '#c0392b' if v == 2 else '#6e2c00'
        body += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="7" stroke-linecap="round"/>' % (
            px, py, x, y, col)
        body += '<circle cx="%d" cy="%d" r="11" fill="#1e8449"/>' % (x, y) + text(x, y + 4, v, 11, '#fff', weight='bold')
    body += text(205, 112, 'отрезать ветку 2', 12, '#c0392b', 'start', 'bold')
    return svg(420, 270, body, bg='#eaf6fb')


@pic('discretelog', 'discretelog.svg')
def discretelog():
    m, a = 16, 3
    body = ''
    cx, cy, R = 190, 150, 105
    for r in range(m):
        ang = -math.pi / 2 + 2 * math.pi * r / m
        body += '<circle cx="%.1f" cy="%.1f" r="13" fill="#fdebd0" stroke="#d68910"/>' % (cx + R * math.cos(ang), cy + R * math.sin(ang))
        body += text(cx + R * math.cos(ang), cy + R * math.sin(ang) + 4, r, 11)
    body += ARROW
    v = 1
    for step in range(4):
        w = v * a % m
        a1 = -math.pi / 2 + 2 * math.pi * v / m
        a2 = -math.pi / 2 + 2 * math.pi * w / m
        body += curve(cx + R * math.cos(a1), cy + R * math.sin(a1), cx + R * math.cos(a2), cy + R * math.sin(a2), 25,
                      None, '#1f618d', 14)
        v = w
    body += text(cx, cy - 4, 'степени 3', 13, '#1f618d', weight='bold') + text(cx, cy + 14, 'по модулю 16', 13, '#1f618d')
    body += text(cx, 290, '1 → 3 → 9 → 11 → 1 → …', 13)
    return svg(380, 305, body)


@pic('sqrtcount', 'sqrtcount.svg')
def sqrtcount():
    m = 15
    body = ''
    for x in range(m):
        r = x * x % m
        X = 30 + x * 25
        body += node(X, 50, str(x), '#2e86c1', 11)
        body += '<line x1="%d" y1="62" x2="%d" y2="148" stroke="%s" stroke-width="%s"/>' % (
            X, 30 + r * 25, '#c0392b' if r == 4 else '#bdc3c7', 2.5 if r == 4 else 1)
    for r in range(m):
        body += node(30 + r * 25, 160, str(r), '#c0392b' if r == 4 else '#95a5a6', 11)
    body += text(205, 20, 'x', 13, '#24364a', weight='bold') + text(205, 195, 'x² mod 15', 13, '#24364a', weight='bold')
    return svg(410, 210, body)


@pic('prufer', 'prufer.svg')
def prufer():
    pos = {'1': (210, 110), '2': (90, 50), '3': (90, 170), '4': (330, 110), '5': (420, 50), '6': (420, 170)}
    E = [('1', '2'), ('1', '3'), ('1', '4'), ('4', '5'), ('4', '6')]
    extra = text(255, 225, 'n = 6, к насосу 1 подходят d = 3 арыка, концевых деревьев c = 4', 12)
    extra += text(255, 245, 'код Прюфера: 1 1 4 4', 12, '#7d3c98', weight='bold')
    return graph(510, 260, pos, E, colors={'1': '#d68910', '2': '#27ae60', '3': '#27ae60', '5': '#27ae60', '6': '#27ae60'},
                 extra=extra)


@pic('dicesum', 'dicesum.svg')
def dicesum():
    dist = [1]
    for faces in ([0, 1], [1, 2, 3, 4, 5, 6], [0, 0, 2, 5]):
        nd = [0.0] * (len(dist) + max(faces))
        for s_, p in enumerate(dist):
            for v in faces:
                nd[s_ + v] += p / len(faces)
        dist = nd
    W, H = 440, 220
    bw = (W - 60) / len(dist)
    mx = max(dist)
    body = ''
    for i, p in enumerate(dist):
        h = p / mx * 150
        body += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#2e86c1"/>' % (40 + i * bw + 1, 180 - h, bw - 2, h)
        body += text(40 + i * bw + bw / 2, 196, i, 10, '#555')
    body += text(W / 2, 20, 'распределение суммы: монета {0, 1}, кубик 1…6, кость {0, 0, 2, 5}', 12)
    return svg(W, H, body)


@pic('erdosgallai', 'erdosgallai.svg')
def erdosgallai():
    import random as R
    R.seed(4)
    pos = {str(i): (210 + 140 * math.cos(2 * math.pi * i / 7), 125 + 95 * math.sin(2 * math.pi * i / 7)) for i in range(7)}
    E = [('0', '1'), ('1', '2'), ('2', '3'), ('3', '4'), ('4', '5'), ('5', '6'), ('6', '0'), ('0', '3'), ('1', '5')]
    deg = {v: 0 for v in pos}
    for a, b in E:
        deg[a] += 1
        deg[b] += 1
    extra = ''.join(text(x, y + 30 if y > 125 else y - 22, 'd = %d' % deg[v], 11, '#7d3c98') for v, (x, y) in pos.items())
    return graph(420, 260, {v: p for v, p in pos.items()}, E, extra=extra)


@pic('bm', 'bm.svg')
def bm():
    seq, P = [3, 1], 998244353
    for i in range(10):
        seq.append((2 * seq[-1] + seq[-2]) % 50)
    W, H = 460, 200
    body = ''
    for i, v in enumerate(seq):
        h = v / 50 * 120
        x = 30 + i * 34
        body += '<rect x="%d" y="%.1f" width="24" height="%.1f" rx="3" fill="%s"/>' % (x, 150 - h, h, '#e67e22' if i < 6 else '#f5cba7')
        body += text(x + 12, 168, 'a[%d]' % i, 10, '#555')
    body += text(W / 2, 22, 'известны первые 2k записей (тёмные), остальные нужно предсказать', 12)
    body += text(W / 2, 190, 'a[i] = c[1]·a[i−1] + … + c[L]·a[i−L]', 13, '#24364a', weight='bold')
    return svg(W, H, body)


@pic('xorpow', 'xorpow.svg')
def xorpow():
    body = ''
    codes = [5, 3, 6, 5]
    for i, c in enumerate(codes):
        x = 40 + i * 95
        body += '<path d="M%d 40 L%d 40 L%d 100 L%d 100 Z" fill="#d5dbdb" stroke="#7f8c8d" stroke-width="2"/>' % (
            x, x + 70, x + 55, x + 15)
        body += '<polygon points="%d,100 %d,100 %d,135" fill="#bfc9ca" stroke="#7f8c8d" stroke-width="2"/>' % (
            x + 15, x + 55, x + 35)
        body += text(x + 35, 65, c, 15, '#24364a', weight='bold') + text(x + 35, 86, format(c, '03b'), 12, '#7d3c98')
        if i:
            body += text(x - 12, 75, '⊕', 18, '#c0392b', weight='bold')
    body += text(220, 170, '5 ⊕ 3 ⊕ 6 ⊕ 5 = 101 ⊕ 011 ⊕ 110 ⊕ 101 = 101 = 5', 13)
    return svg(440, 190, body)


@pic('menage', 'menage.svg')
def menage():
    n = 4
    cx, cy, R = 200, 150, 105
    body = '<circle cx="%d" cy="%d" r="70" fill="#e9dcc3" stroke="#8a6d3b" stroke-width="2"/>' % (cx, cy)
    body += text(cx, cy + 5, 'дастархан', 13, '#5b3a29', weight='bold')
    women = [0, 1, 2, 3]
    men = [2, 3, 0, 1]
    cols = ['#c0392b', '#2e86c1', '#27ae60', '#8e44ad']
    for i in range(2 * n):
        a = -math.pi / 2 + 2 * math.pi * i / (2 * n)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        couple = women[i // 2] if i % 2 == 0 else men[i // 2]
        shape = ('<circle cx="%.1f" cy="%.1f" r="16" fill="%s"/>' % (x, y, cols[couple]) if i % 2 == 0 else
                 '<rect x="%.1f" y="%.1f" width="30" height="30" rx="4" fill="%s"/>' % (x - 15, y - 15, cols[couple]))
        body += shape + text(x, y + 4, ('Ж' if i % 2 == 0 else 'М') + str(couple + 1), 11, '#fff', weight='bold')
    body += text(cx, 290, 'одинаковый цвет — супруги; они не сидят рядом', 12)
    return svg(400, 305, body)


def yurt(x, y, w=70, color='#e9dcc3'):
    h = w * 0.55
    return ('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Q%.1f %.1f %.1f %.1f Z" fill="%s" stroke="#8a6d3b" stroke-width="2"/>' % (
        x - w / 2, y, x - w / 2, y - h * 0.55, x - w / 4, y - h, x, y - h * 1.35, x + w / 4, y - h, color) +
        '<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="#8a6d3b" stroke-width="2"/>' % (
        x + w / 4, y - h, x + w / 2, y - h * 0.55, x + w / 2, y, color) +
        '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#8a6d3b"/>' % (x - 7, y - 22, 14, 22))


@pic('stirling', 'stirling.svg')
def stirling():
    groups = [['1', '2', '3'], ['4']], [['1', '4'], ['2', '3']]
    body = ''
    for row, g in enumerate(groups):
        for i, members in enumerate(g):
            x = 70 + i * 120 + row * 230
            body += yurt(x, 120)
            for j, mbr in enumerate(members):
                body += node(x - 25 + j * 25, 150, mbr, '#2e86c1', 11)
        body += text(130 + row * 230, 190, 'вариант %d' % (row + 1), 12)
    return svg(470, 210, body)


@pic('josephus', 'josephus.svg')
def josephus():
    n, k = 7, 3
    order = []
    people = list(range(1, n + 1))
    i = 0
    while len(people) > 1:
        i = (i + k - 1) % len(people)
        order.append(people.pop(i))
    rank = {v: t + 1 for t, v in enumerate(order)}
    cx, cy, R = 190, 140, 95
    body = '<circle cx="%d" cy="%d" r="28" fill="#f39c12"/>' % (cx, cy) + text(cx, cy + 5, 'костёр', 11, '#fff', weight='bold')
    for v in range(1, n + 1):
        a = -math.pi / 2 + 2 * math.pi * (v - 1) / n
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        body += node(x, y, str(v), '#27ae60' if v not in rank else '#95a5a6', 16)
        if v in rank:
            body += text(cx + (R + 30) * math.cos(a), cy + (R + 30) * math.sin(a) + 4, '%d-й' % rank[v], 11, '#c0392b')
    body += text(cx, 272, 'n = 7, k = 3: порядок выбывания и победитель 4', 12)
    return svg(380, 290, body)


@pic('bandpaths', 'bandpaths.svg')
def bandpaths():
    h, N = 2, 4
    body = '<rect x="30" y="20" width="400" height="22" fill="#ecf0f1"/>' + text(230, 36, 'снег', 12, '#7f8c8d')
    body += '<rect x="30" y="198" width="400" height="22" fill="#aed6f1"/>' + text(230, 214, 'река', 12, '#1f618d')
    sx, sy = 90, 64
    for lvl in range(h + 1):
        y = 180 - lvl * sy
        body += '<line x1="40" y1="%d" x2="420" y2="%d" stroke="#d5d8dc" stroke-dasharray="4 4"/>' % (y, y)
        body += text(32, y + 4, lvl, 11, '#555', 'end')
    for path, col in (([0, 1, 0, 1, 0], '#c0392b'), ([0, 1, 2, 1, 0], '#1e8449')):
        pts = ' '.join('%d,%d' % (60 + t * sx, 180 - v * sy) for t, v in enumerate(path))
        body += '<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (pts, col)
    for t in range(N + 1):
        body += text(60 + t * sx, 236, 't = %d' % t, 11, '#555')
    return svg(460, 245, body)


@pic('connprob', 'connprob.svg')
def connprob():
    pos = {'1': (80, 170), '2': (210, 50), '3': (340, 170)}
    E = [('1', '2', '1/2', '#2e86c1'), ('2', '3', '1/2', '#2e86c1'), ('1', '3', '1/2', '#bdc3c7')]
    extra = text(210, 215, 'дорога 1 – 3 разрушена, но сёла по-прежнему связаны', 12)
    return graph(420, 235, pos, E, extra=extra)


@pic('latticeline', 'latticeline.svg')
def latticeline():
    a, b, c, u = 2, 3, 12, 50
    ox, oy = 50, 230
    body = '<polygon points="%d,%d %d,%d %d,%d" fill="#fdebd0" stroke="#d68910" stroke-width="2"/>' % (
        ox, oy, ox + c / a * u, oy, ox, oy - c / b * u)
    body += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#333"/>' % (ox, oy, ox + 330, oy)
    body += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#333"/>' % (ox, oy, ox, oy - 215)
    for x in range(0, 7):
        for y in range(0, 5):
            ok = x >= 1 and y >= 1 and a * x + b * y <= c
            body += '<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (ox + x * u, oy - y * u, 6 if ok else 3, '#c0392b' if ok else '#aab7b8')
    body += text(ox + 320, oy + 18, 'дыни x', 12, '#555', 'end') + text(ox - 8, 20, 'арбузы y', 12, '#555', 'start')
    body += text(ox + 175, 60, '2x + 3y ≤ 12', 14, '#d68910', weight='bold')
    return svg(400, 255, body)


# ---------------------------------------------------------------- geometry

@pic('cableway', 'cableway.svg')
def cableway():
    xs = [0, 2, 4, 5, 8]
    st = {0, 2, 4}
    body = '<path d="M20 230 L440 60 L440 250 L20 250 Z" fill="#eaf2f8"/>'
    body += '<path d="M20 230 L440 60" stroke="#7f8c8d" stroke-width="3"/>'
    pts = []
    for i, x in enumerate(xs):
        X = 40 + x * 48
        Y = 222 - x * 19.5
        pts.append((X, Y - 60))
        body += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#555" stroke-width="4"/>' % (X, Y, X, Y - 60)
        body += text(X, Y + 18, 'x=%d' % x, 11, '#555')
        if i in st:
            body += '<rect x="%d" y="%d" width="22" height="14" rx="3" fill="#c0392b"/>' % (X - 11, Y - 74)
    sel = [pts[i] for i in sorted(st)]
    body += '<polyline points="%s" fill="none" stroke="#1f618d" stroke-width="2.5"/>' % ' '.join('%d,%d' % p for p in sel)
    body += text(330, 235, 'красные — станции', 12, '#c0392b')
    return svg(460, 260, body)


@pic('diameter', 'diameter.svg')
def diameter():
    P = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 5)]
    u, ox, oy = 55, 90, 330
    body = ''
    for a, b in (((0, 0), (4, 4)), ((0, 4), (4, 0))):
        body += '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="#c0392b" stroke-width="2.5" stroke-dasharray="7 4"/>' % (
            ox + a[0] * u, oy - a[1] * u, ox + b[0] * u, oy - b[1] * u)
    hull = [(0, 0), (4, 0), (4, 4), (2, 5), (0, 4)]
    body += '<polygon points="%s" fill="none" stroke="#95a5a6" stroke-width="1.5"/>' % ' '.join(
        '%d,%d' % (ox + x * u, oy - y * u) for x, y in hull)
    for x, y in P:
        body += yurt(ox + x * u, oy - y * u + 14, 34)
    body += text(210, 360, 'две самые далёкие пары: расстояние √32', 12)
    return svg(420, 375, body)


@pic('origintri', 'origintri.svg')
def origintri():
    P = [(2, 1), (-1, 2), (-2, -3), (3, -3)]
    u, ox, oy = 40, 190, 175
    body = '<rect x="0" y="0" width="380" height="350" rx="10" fill="#0b1d3a"/>'
    body += '<polygon points="%s" fill="#f1c40f" fill-opacity="0.18" stroke="#f1c40f" stroke-width="2"/>' % ' '.join(
        '%d,%d' % (ox + x * u, oy - y * u) for x, y in (P[0], P[1], P[2]))
    for x, y in P:
        body += '<circle cx="%d" cy="%d" r="6" fill="#fff"/>' % (ox + x * u, oy - y * u)
    body += '<circle cx="%d" cy="%d" r="8" fill="#e74c3c"/>' % (ox, oy) + text(ox + 14, oy - 10, '(0, 0)', 12, '#fff', 'start')
    return svg(380, 350, body)


@pic('isosceles', 'isosceles.svg')
def isosceles():
    P = [(0, 0), (2, 0), (2, 2), (0, 2), (1, 1)]
    u, ox, oy = 120, 70, 300
    body = '<polygon points="%d,%d %d,%d %d,%d" fill="#abebc6" stroke="#1e8449" stroke-width="2"/>' % (
        ox, oy, ox + 2 * u, oy, ox + u, oy - u)
    body += '<polygon points="%d,%d %d,%d %d,%d" fill="#f9e79f" fill-opacity="0.7" stroke="#b7950b" stroke-width="2"/>' % (
        ox + 2 * u, oy, ox + 2 * u, oy - 2 * u, ox, oy - 2 * u)
    for x, y in P:
        body += '<rect x="%d" y="%d" width="10" height="26" fill="#6e2c00"/>' % (ox + x * u - 5, oy - y * u - 20)
    return svg(380, 330, body, bg='#eafaf1')


@pic('chords', 'chords.svg')
def chords():
    cx, cy, R = 190, 180, 140
    pos = {}
    for k in range(1, 9):
        a = -math.pi / 2 + 2 * math.pi * (k - 1) / 8
        pos[k] = (cx + R * math.cos(a), cy + R * math.sin(a))
    body = '<circle cx="%d" cy="%d" r="%d" fill="#fdf2e9" stroke="#8a6d3b" stroke-width="4"/>' % (cx, cy, R)
    for (a, b), col in (((1, 5), '#c0392b'), ((3, 7), '#2e86c1'), ((1, 3), '#27ae60'), ((8, 6), '#8e44ad')):
        body += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3"/>' % (*pos[a], *pos[b], col)
    for k, (x, y) in pos.items():
        body += '<circle cx="%.1f" cy="%.1f" r="5" fill="#333"/>' % (x, y)
        body += text(cx + (R + 18) * (x - cx) / R, cy + (R + 18) * (y - cy) / R + 4, k, 12, '#333', weight='bold')
    return svg(380, 360, body)


# ---------------------------------------------------------------- strings and digits

@pic('aho', 'aho.svg')
def aho():
    pos = {'ε': (50, 120), 'a': (150, 60), 'aa': (250, 30), 'b': (150, 180), 'ba': (250, 180), 'bab': (350, 180)}
    E = [('ε', 'a', 'a'), ('a', 'aa', 'a'), ('ε', 'b', 'b'), ('b', 'ba', 'a'), ('ba', 'bab', 'b')]
    body = ARROW
    for a, b, l in E:
        body += edge(*pos[a], *pos[b], l, '#555', 2, True, 20)
    for v, (x, y) in pos.items():
        bad = v in ('aa', 'bab')
        body += '<circle cx="%d" cy="%d" r="20" fill="%s" stroke="#1b4f72" stroke-width="1.5"/>' % (x, y, '#c0392b' if bad else '#2e86c1')
        body += text(x, y + 5, v, 13, '#fff', weight='bold')
    body += text(220, 235, 'бор слов aa и bab: красные вершины запрещены', 12)
    return svg(440, 250, body)


@pic('eertree', 'eertree.svg')
def eertree():
    s = 'abacaba'
    body = ''
    for i, ch in enumerate(s):
        body += '<rect x="%d" y="30" width="44" height="44" rx="6" fill="#d6eaf8" stroke="#2e86c1"/>' % (60 + i * 46)
        body += text(82 + i * 46, 60, ch, 20, '#1b4f72', weight='bold')
    arcs = [(0, 2, '#e67e22'), (4, 6, '#e67e22'), (1, 5, '#27ae60'), (0, 6, '#8e44ad')]
    for k, (a, b, col) in enumerate(arcs):
        x1, x2 = 62 + a * 46, 102 + b * 46
        y = 84 + 18 * k
        body += '<path d="M%d 78 L%d %d L%d %d L%d 78" fill="none" stroke="%s" stroke-width="2.5"/>' % (x1, x1, y, x2, y, x2, col)
    body += text(220, 175, 'палиндромы aba (дважды), bacab и abacaba', 12)
    return svg(440, 190, body)


@pic('lyndon', 'lyndon.svg')
def lyndon():
    s = 'cabcab'
    cx, cy, R = 190, 150, 95
    body = '<circle cx="%d" cy="%d" r="%d" fill="#f5cba7" stroke="#6e2c00" stroke-width="10"/>' % (cx, cy, R + 20)
    body += '<circle cx="%d" cy="%d" r="%d" fill="#fdebd0"/>' % (cx, cy, R - 25)
    for i, ch in enumerate(s):
        a = -math.pi / 2 + 2 * math.pi * i / len(s)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        body += '<circle cx="%.1f" cy="%.1f" r="18" fill="#6e2c00"/>' % (x, y) + text(x, y + 6, ch, 17, '#fff', weight='bold')
        body += text(cx + (R + 40) * math.cos(a), cy + (R + 40) * math.sin(a) + 4, i + 1, 11, '#555')
    body += text(cx, cy + 5, 'cabcab', 15, '#6e2c00', weight='bold')
    return svg(380, 300, body)


@pic('hash2d', 'hash2d.svg')
def hash2d():
    g = ['abac', 'bcab', 'aaab']
    cols = {'a': '#c0392b', 'b': '#f4d03f', 'c': '#2e86c1'}
    c, ox, oy = 48, 30, 30
    body = ''
    for i, row in enumerate(g):
        for j, ch in enumerate(row):
            body += '<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="#fff" stroke-width="2"/>' % (
                ox + j * c, oy + i * c, c, c, cols[ch])
            body += text(ox + j * c + c / 2, oy + i * c + c / 2 + 5, ch, 14, '#fff', weight='bold')
    for (i, j, r, w) in ((0, 0, 1, 2), (1, 2, 1, 2), (2, 2, 1, 2), (0, 1, 1, 2), (0, 0, 2, 1), (1, 0, 2, 1)):
        body += '<rect x="%d" y="%d" width="%d" height="%d" fill="none" stroke="#1d1d1d" stroke-width="2.5" stroke-dasharray="5 3" rx="4"/>' % (
            ox + j * c + 3, oy + i * c + 3, w * c - 6, r * c - 6)
    body += '<rect x="290" y="70" width="%d" height="%d" fill="%s"/><rect x="%d" y="70" width="%d" height="%d" fill="%s"/>' % (
        c, c, cols['a'], 290 + c, c, c, cols['b'])
    body += text(290 + c, 60, 'образец', 12) + text(290 + c / 2, 99, 'a', 14, '#fff', weight='bold') + text(290 + 1.5 * c, 99, 'b', 14, '#fff', weight='bold')
    return svg(420, 200, body)


@pic('digitsum', 'digitsum.svg')
def digitsum():
    body = '<rect x="20" y="20" width="340" height="120" rx="12" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/>'
    body += text(190, 50, 'БИЛЕТ  №', 14, '#7d6608', weight='bold')
    body += text(190, 100, '0 0 0 1 3 2', 34, '#1d1d1d', weight='bold')
    body += text(190, 128, '1 + 3 + 2 = 6,  132 = 6 · 22', 13, '#1e8449')
    return svg(380, 160, body)


# ---------------------------------------------------------------- data structures, DP

def bars(values, color, W=440, H=200, labels=True, caption=None, marks=None):
    mx = max(abs(v) for v in values) or 1
    bw = (W - 40) / len(values)
    body = ''
    for i, v in enumerate(values):
        h = v / mx * (H - 70)
        col = (marks or {}).get(i, color)
        body += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s"/>' % (20 + i * bw + 2, H - 40 - h, bw - 4, h, col)
        if labels:
            body += text(20 + i * bw + bw / 2, H - 25, v, 11, '#555')
    if caption:
        body += text(W / 2, H - 6, caption, 12)
    return body


@pic('beats', 'beats.svg')
def beats():
    a = [1, 5, 3, 2, 4]
    body = ''
    for i, v in enumerate(a):
        x = 40 + i * 80
        body += '<polygon points="%d,170 %d,%d %d,170" fill="#7b7d7d"/>' % (x - 34, x, 170 - 22 * v, x + 34)
        cut = min(v, 3)
        body += '<polygon points="%d,%d %d,%d %d,%d" fill="#fdfefe" stroke="#aab7b8"/>' % (
            x - 34 * (cut / v) * 0.45, 170 - 22 * v + 22 * v * 0.45, x, 170 - 22 * v, x + 34 * (cut / v) * 0.45, 170 - 22 * v + 22 * v * 0.45)
    body += '<line x1="0" y1="%d" x2="440" y2="%d" stroke="#e74c3c" stroke-width="2" stroke-dasharray="6 4"/>' % (170 - 66, 170 - 66)
    body += text(400, 170 - 72, 'x = 3', 12, '#e74c3c', weight='bold')
    body += text(220, 195, 'оттепель 1 1 5 3: снег выше уровня 3 тает', 12)
    return svg(440, 205, body, bg='#eaf2f8')


@pic('mo', 'mo.svg')
def mo():
    c = [1, 2, 1, 1, 3]
    cols = {1: '#c0392b', 2: '#2e86c1', 3: '#f1c40f'}
    body = ''
    for i, v in enumerate(c):
        body += '<rect x="%d" y="30" width="70" height="120" fill="%s" stroke="#fff" stroke-width="3"/>' % (40 + i * 74, cols[v])
        body += text(75 + i * 74, 170, v, 13, '#333', weight='bold')
    body += text(225, 195, 'цвета 1, 2, 1, 1, 3: пёстрость 3² + 1² + 1² = 11', 12)
    return svg(460, 210, body)


@pic('kth', 'kth.svg')
def kth():
    return svg(440, 200, bars([5, 1, 4, 2, 3], '#85c1e9', caption='оценки депутатов; 3-я по величине на 1…5 — это 3',
                              marks={4: '#1f618d'}))


@pic('treap', 'treap.svg')
def treap():
    a = [3, 1, 4, 1, 5]
    body = ''
    for row, arr, title in ((0, a, 'до'), (1, [4, 1, 3, 1, 5], 'после «1 1 3»')):
        for i, v in enumerate(arr):
            x, y = 110 + i * 62, 50 + row * 90
            col = '#d68910' if i < 3 else '#2e86c1'
            body += '<circle cx="%d" cy="%d" r="22" fill="%s"/>' % (x, y, col) + text(x, y + 5, v, 14, '#fff', weight='bold')
        body += text(20, 55 + row * 90, title, 12, '#333', 'start')
    return svg(460, 190, body)


@pic('sos', 'sos.svg')
def sos():
    masks = [3, 5, 7]
    names = ['зира', 'барбарис', 'кориандр']
    body = ''
    for i, mk in enumerate(masks):
        x = 60 + i * 130
        body += '<rect x="%d" y="30" width="90" height="110" rx="12" fill="#fdebd0" stroke="#a04000" stroke-width="2"/>' % (x - 45)
        body += text(x, 55, 'маска %d' % mk, 12, '#6e2c00', weight='bold')
        for b in range(3):
            on = mk >> b & 1
            body += text(x, 80 + b * 18, names[b] if on else '—', 11, '#1e8449' if on else '#aab7b8')
    body += text(220, 170, '3 AND 5 = 1: в плове останется только зира', 12)
    return svg(440, 185, body)


@pic('reroot', 'reroot.svg')
def reroot():
    pos = {'1': (50, 100), '2': (150, 100), '3': (260, 100), '4': (390, 100)}
    E = [('1', '2', 1), ('2', '3', 2), ('3', '4', 3)]
    extra = text(220, 160, 'S(3) = 3² + 2² + 3² = 22 — наименьшая сумма', 12)
    return graph(440, 180, pos, E, colors={'3': '#c0392b'}, extra=extra)


@pic('domino', 'domino.svg')
def domino():
    tilings = [[(0, 0, 0, 1), (1, 0, 1, 1), (0, 2, 1, 2)], [(0, 0, 1, 0), (0, 1, 0, 2), (1, 1, 1, 2)],
               [(0, 0, 1, 0), (0, 1, 1, 1), (0, 2, 1, 2)]]
    c = 40
    body = ''
    cols = ['#c0392b', '#2e86c1', '#27ae60']
    for t, til in enumerate(tilings):
        ox = 20 + t * 140
        for k, (r1, c1, r2, c2) in enumerate(til):
            x, y = ox + min(c1, c2) * c, 30 + min(r1, r2) * c
            w, h = (abs(c2 - c1) + 1) * c, (abs(r2 - r1) + 1) * c
            body += '<rect x="%d" y="%d" width="%d" height="%d" rx="5" fill="%s" stroke="#fff" stroke-width="3"/>' % (x, y, w, h, cols[k])
    return svg(440, 130, body)


@pic('knuth', 'knuth.svg')
def knuth():
    cx, cy, R = 190, 140, 90
    body = '<circle cx="%d" cy="%d" r="%d" fill="none" stroke="#a04000" stroke-width="26" stroke-opacity="0.25"/>' % (cx, cy, R)
    for i, v in enumerate([1, 2, 3, 4]):
        a = -math.pi / 2 + 2 * math.pi * i / 4
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        body += '<rect x="%.1f" y="%.1f" width="54" height="34" rx="6" fill="#a04000"/>' % (x - 27, y - 17)
        body += text(x, y + 5, '%d кг' % v, 12, '#fff', weight='bold')
    body += yurt(cx, cy + 25, 70)
    return svg(380, 280, body)


@pic('postman', 'postman.svg')
def postman():
    pos = {'1': (70, 60), '2': (330, 60), '3': (330, 210), '4': (70, 210)}
    E = [('1', '2', 4), ('2', '3', 1), ('3', '4', 2), ('4', '1', 3), ('1', '3', 4, '#c0392b')]
    extra = text(200, 255, 'улицу 1 – 3 машина проедет дважды', 12, '#c0392b')
    return graph(420, 270, pos, E, colors={'1': '#d68910', '3': '#d68910'}, extra=extra)


@pic('bridgepath', 'bridgepath.svg')
def bridgepath():
    pos = {'1': (60, 60), '2': (60, 190), '3': (180, 125), '4': (310, 125), '5': (410, 125)}
    body = '<path d="M240 0 C 225 80, 260 170, 240 260" stroke="#5dade2" stroke-width="26" fill="none" opacity="0.6"/>'
    E = [('1', '2'), ('2', '3'), ('3', '1'), ('3', '4', None, '#c0392b')]
    g = graph(440, 250, pos, E, extra=curve(310, 125, 410, 125, 18, None, '#7f8c8d') + curve(410, 125, 310, 125, 18, None, '#7f8c8d'))
    return g.replace('<rect width="440" height="250" rx="10" fill="#f6f8fb"/>', '<rect width="440" height="250" rx="10" fill="#f6f8fb"/>' + body + ARROW)


def main():
    names = sys.argv[1:] or sorted(PICS)
    for problem in names:
        for name, fn in PICS.get(problem, []):
            folder = os.path.join(ROOT, problem, 'img')
            os.makedirs(folder, exist_ok=True)
            with open(os.path.join(folder, name), 'w', encoding='utf-8', newline='\n') as f:
                f.write(fn())
            print('drew', problem, name)


if __name__ == '__main__':
    main()
