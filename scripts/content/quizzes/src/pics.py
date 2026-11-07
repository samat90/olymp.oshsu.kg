"""All quiz pictures, drawn as SVG by hand (no third-party images). 800x450 canvas."""
import math

W, H = 800, 450
FONT = "DejaVu Sans"
INK = "#1f2937"
BLUE = "#2563eb"
RED = "#dc2626"
GREEN = "#16a34a"
ORANGE = "#ea580c"
YELLOW = "#facc15"
GREY = "#9ca3af"


def svg(body, bg="#ffffff"):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" '
            'font-family="%s">' % (W, H, W, H, FONT) +
            '<rect width="%d" height="%d" fill="%s"/>' % (W, H, bg) + body + '</svg>')


def text(x, y, s, size=28, fill=INK, anchor="middle", weight="normal", family=None, italic=False):
    fam = ' font-family="%s"' % family if family else ''
    st = ' font-style="italic"' if italic else ''
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return ('<text x="%g" y="%g" font-size="%g" fill="%s" text-anchor="%s" font-weight="%s"%s%s>%s</text>'
            % (x, y, size, fill, anchor, weight, fam, st, s))


def line(x1, y1, x2, y2, stroke=INK, w=3, dash=None, cap="round"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g" stroke-linecap="%s"%s/>'
            % (x1, y1, x2, y2, stroke, w, cap, d))


def rect(x, y, w, h, fill="none", stroke=INK, sw=3, rx=0):
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="%s" stroke="%s" stroke-width="%g"/>'
            % (x, y, w, h, rx, fill, stroke, sw))


def circle(cx, cy, r, fill="none", stroke=INK, sw=3):
    return '<circle cx="%g" cy="%g" r="%g" fill="%s" stroke="%s" stroke-width="%g"/>' % (cx, cy, r, fill, stroke, sw)


def path(d, fill="none", stroke=INK, sw=3, extra=""):
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round" %s/>' % (d, fill, stroke, sw, extra)


def poly(points, fill="none", stroke=INK, sw=3):
    pts = ' '.join('%g,%g' % p for p in points)
    return '<polygon points="%s" fill="%s" stroke="%s" stroke-width="%g" stroke-linejoin="round"/>' % (pts, fill, stroke, sw)


def arrow(x1, y1, x2, y2, stroke=INK, w=3, head=14):
    a = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(a - 0.4), y2 - head * math.sin(a - 0.4))
    p2 = (x2 - head * math.cos(a + 0.4), y2 - head * math.sin(a + 0.4))
    bx, by = x2 - head * 0.8 * math.cos(a), y2 - head * 0.8 * math.sin(a)
    return line(x1, y1, bx, by, stroke, w) + poly([(x2, y2), p1, p2], fill=stroke, stroke=stroke, sw=1)


def arc(cx, cy, r, a1, a2, stroke=INK, w=3):
    """Arc from angle a1 to a2 (degrees, math orientation: counter-clockwise, y up)."""
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy - r * math.sin(math.radians(a1))
    x2, y2 = cx + r * math.cos(math.radians(a2)), cy - r * math.sin(math.radians(a2))
    large = 1 if (a2 - a1) % 360 > 180 else 0
    return path('M %g %g A %g %g 0 %d 0 %g %g' % (x1, y1, r, r, large, x2, y2), stroke=stroke, sw=w)


# ----------------------------------------------------------------- covers

COVERS = {
    'informatika': ('Информатика', '#1d4ed8', '#38bdf8', 'inf'),
    'matematika': ('Математика', '#7c3aed', '#c084fc', 'math'),
    'fizika': ('Физика', '#0f766e', '#2dd4bf', 'phys'),
    'himiya': ('Химия', '#b45309', '#fbbf24', 'chem'),
    'biologiya': ('Биология', '#15803d', '#86efac', 'bio'),
    'istoriya': ('История', '#9f1239', '#fb7185', 'hist'),
    'geografiya': ('География', '#0369a1', '#7dd3fc', 'geo'),
    'literatura': ('Литература', '#6b21a8', '#f0abfc', 'lit'),
    'english50': ('English', '#be123c', '#fda4af', 'eng'),
    'python50': ('Python', '#166534', '#65a30d', 'code:py'),
    'cpp50': ('C++', '#1e40af', '#60a5fa', 'code:C++'),
    'java50': ('Java', '#9a3412', '#fb923c', 'code:java'),
    'csharp50': ('C#', '#5b21b6', '#a78bfa', 'code:C#'),
    'js50': ('JavaScript', '#a16207', '#fde047', 'code:JS'),
}


def cover_icon(kind):
    w = '#ffffff'
    if kind == 'inf':
        return (rect(520, 120, 200, 130, stroke=w, sw=8, rx=10) + line(620, 250, 620, 290, w, 8) +
                line(570, 295, 670, 295, w, 8) + text(620, 205, '01', 60, w, weight='bold', family='DejaVu Sans Mono'))
    if kind == 'math':
        return (text(620, 230, 'π', 150, w, weight='bold') + text(540, 330, '√x', 54, w) + text(700, 330, 'Σ', 60, w))
    if kind == 'phys':
        s = circle(620, 220, 18, fill=w, stroke=w)
        for ang in (0, 60, 120):
            s += ('<ellipse cx="620" cy="220" rx="110" ry="38" fill="none" stroke="%s" stroke-width="7" '
                  'transform="rotate(%d 620 220)"/>' % (w, ang))
        return s
    if kind == 'chem':
        return (path('M 590 110 L 590 190 L 530 320 Q 525 340 545 340 L 695 340 Q 715 340 710 320 L 650 190 L 650 110',
                     stroke=w, sw=8) + line(575, 110, 665, 110, w, 8) +
                path('M 552 290 L 688 290 L 705 325 Q 708 335 695 335 L 545 335 Q 532 335 536 325 Z', fill=w, stroke=w, sw=2) +
                circle(600, 265, 9, fill=w, stroke=w) + circle(640, 245, 6, fill=w, stroke=w))
    if kind == 'bio':
        return (path('M 540 330 C 540 200 640 120 720 110 C 720 230 650 320 540 330 Z', stroke=w, sw=8) +
                path('M 540 330 C 600 260 650 200 700 140', stroke=w, sw=6))
    if kind == 'hist':
        s = ''
        for i, x in enumerate((540, 600, 660)):
            s += rect(x - 14, 160, 28, 150, stroke=w, sw=6)
        return s + poly([(510, 160), (620, 100), (730, 160)], stroke=w, sw=7) + line(505, 320, 735, 320, w, 8)
    if kind == 'geo':
        s = circle(620, 220, 110, stroke=w, sw=8)
        s += '<ellipse cx="620" cy="220" rx="45" ry="110" fill="none" stroke="%s" stroke-width="5"/>' % w
        s += line(510, 220, 730, 220, w, 5) + line(525, 165, 715, 165, w, 4) + line(525, 275, 715, 275, w, 4)
        return s
    if kind == 'lit':
        return (path('M 620 150 C 580 120 530 120 500 130 L 500 320 C 530 310 580 310 620 340 Z', stroke=w, sw=7) +
                path('M 620 150 C 660 120 710 120 740 130 L 740 320 C 710 310 660 310 620 340 Z', stroke=w, sw=7))
    if kind == 'eng':
        return (rect(510, 120, 220, 150, stroke=w, sw=8, rx=24) + poly([(560, 268), (545, 320), (610, 268)], fill=w, stroke=w) +
                text(620, 220, 'ABC', 64, w, weight='bold'))
    if kind.startswith('code:'):
        mono = 'DejaVu Sans Mono'
        return (rect(500, 110, 240, 220, fill='rgba(0,0,0,0.3)', stroke=w, sw=7, rx=16) + line(500, 160, 740, 160, w, 5) +
                circle(530, 135, 8, fill=w, stroke=w) + circle(556, 135, 8, fill=w, stroke=w) +
                circle(582, 135, 8, fill=w, stroke=w) + text(620, 250, kind[5:], 58, w, weight='bold', family=mono) +
                text(522, 310, '>_', 30, w, 'start', family=mono))
    return ''


def cover(slug, subtitle):
    title, c1, c2, kind = COVERS[slug]
    body = ('<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/>'
            '<stop offset="1" stop-color="%s"/></linearGradient></defs>' % (c1, c2))
    body += '<rect width="800" height="450" fill="url(#g)"/>'
    body += text(60, 210, title, 62 if len(title) < 11 else 54, '#ffffff', 'start', 'bold')
    body += text(62, 262, subtitle, 28, '#ffffffdd', 'start')
    body += cover_icon(kind)
    return svg(body, c1)


# ----------------------------------------------------------------- informatics

def flowchart():
    b = ''
    cx = 330
    b += '<ellipse cx="%d" cy="34" rx="70" ry="22" fill="#e0f2fe" stroke="%s" stroke-width="3"/>' % (cx, INK)
    b += text(cx, 44, 'Начало', 24)
    b += arrow(cx, 56, cx, 82)
    b += rect(cx - 80, 84, 160, 46, fill="#fef9c3") + text(cx, 116, 'x := 5', 26, family='DejaVu Sans Mono')
    b += arrow(cx, 130, cx, 158)
    b += poly([(cx, 160), (cx + 100, 205), (cx, 250), (cx - 100, 205)], fill="#fee2e2") + text(cx, 215, 'x > 3 ?', 26)
    # yes to the right, no to the left
    b += line(cx + 100, 205, 560, 205) + arrow(560, 205, 560, 268) + text(470, 195, 'да', 22, GREEN, weight='bold')
    b += line(cx - 100, 205, 100, 205) + arrow(100, 205, 100, 268) + text(190, 195, 'нет', 22, RED, weight='bold')
    b += rect(480, 270, 160, 46, fill="#fef9c3") + text(560, 302, 'x := x * 2', 24, family='DejaVu Sans Mono')
    b += rect(20, 270, 160, 46, fill="#fef9c3") + text(100, 302, 'x := x + 1', 24, family='DejaVu Sans Mono')
    b += line(560, 316, 560, 345) + line(100, 316, 100, 345) + line(100, 345, 560, 345) + arrow(cx, 345, cx, 365)
    b += poly([(cx - 70, 367), (cx + 90, 367), (cx + 70, 410), (cx - 90, 410)], fill="#dcfce7") + text(cx, 398, 'вывод x', 24)
    b += text(720, 230, '?', 120, BLUE, weight='bold')
    return svg(b)


def spreadsheet():
    b = ''
    x0, y0, cw, ch = 110, 90, 180, 70
    cols = ['', 'A', 'B', 'C']
    widths = [60, cw, cw, cw]
    xs = [x0]
    for wv in widths:
        xs.append(xs[-1] + wv)
    b += rect(x0, 30, sum(widths), 46, fill="#f3f4f6", sw=2)
    b += text(x0 + 12, 62, 'fx', 24, GREY, 'start', italic=True)
    b += text(x0 + 60, 62, '=A1*2+B1', 26, INK, 'start', family='DejaVu Sans Mono')
    rows = [['', 'A', 'B', 'C'], ['1', '5', '7', '=A1*2+B1'], ['2', '', '', '']]
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            hdr = r == 0 or c == 0
            fill = "#e5e7eb" if hdr else "#ffffff"
            if r == 1 and c == 3:
                fill = "#dbeafe"
            b += rect(xs[c], y0 + r * ch, widths[c], ch, fill=fill, stroke="#6b7280", sw=2)
            if val:
                mono = val.startswith('=')
                b += text(xs[c] + widths[c] / 2, y0 + r * ch + 46, val, 26 if not mono else 24,
                          INK, weight='bold' if hdr else 'normal', family='DejaVu Sans Mono' if mono else None)
    b += rect(xs[3], y0 + ch, widths[3], ch, stroke=BLUE, sw=5)
    b += text(400, 380, 'Какое число появится в ячейке C1?', 28, INK)
    return svg(b)


def truth_table():
    b = ''
    rows = [('A', 'B', 'F'), ('0', '0', '0'), ('0', '1', '0'), ('1', '0', '0'), ('1', '1', '1')]
    x0, y0, cw, ch = 250, 40, 100, 70
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            fill = "#e5e7eb" if r == 0 else ("#dcfce7" if c == 2 else "#ffffff")
            b += rect(x0 + c * cw, y0 + r * ch, cw, ch, fill=fill, stroke="#6b7280", sw=2)
            b += text(x0 + c * cw + cw / 2, y0 + r * ch + 47, v, 32, weight='bold' if r == 0 else 'normal',
                      family='DejaVu Sans Mono')
    return svg(b)


def star_topology():
    b = ''
    cx, cy = 400, 225
    b += rect(cx - 55, cy - 30, 110, 60, fill="#dbeafe", rx=8) + text(cx, cy + 9, 'хаб', 24)
    for i in range(6):
        a = math.radians(90 + i * 60)
        x, y = cx + 200 * math.cos(a), cy - 170 * math.sin(a)
        b += line(cx + 50 * math.cos(a), cy - 28 * math.sin(a), x - 40 * math.cos(a), y + 30 * math.sin(a), INK, 3)
        b += rect(x - 40, y - 28, 80, 50, fill="#f3f4f6", rx=6) + rect(x - 30, y - 20, 60, 34, fill="#93c5fd", sw=1)
        b += line(x - 18, y + 30, x + 18, y + 30, INK, 4)
    return svg(b)


def robot_grid():
    """5x4 grid; robot starts at bottom-left cell; letters in some cells."""
    b = ''
    cols, rows, s = 6, 4, 80
    x0, y0 = 160, 40
    for r in range(rows):
        for c in range(cols):
            b += rect(x0 + c * s, y0 + r * s, s, s, fill="#ffffff", stroke="#9ca3af", sw=2)
    # robot at column 0, row 3 (bottom-left)
    rx, ry = x0 + 0 * s + s / 2, y0 + 3 * s + s / 2
    b += rect(rx - 24, ry - 22, 48, 40, fill="#60a5fa", rx=8) + circle(rx - 10, ry - 6, 5, fill=INK, stroke=INK, sw=1)
    b += circle(rx + 10, ry - 6, 5, fill=INK, stroke=INK, sw=1) + line(rx, ry - 22, rx, ry - 32, INK, 3)
    b += circle(rx, ry - 34, 4, fill=RED, stroke=RED, sw=1)
    letters = {(3, 1): 'А', (2, 1): 'Б', (3, 2): 'В', (2, 0): 'Г'}
    for (c, r), ch in letters.items():
        b += text(x0 + c * s + s / 2, y0 + r * s + 54, ch, 40, ORANGE, weight='bold')
    b += text(400, 400, 'вправо 3  •  вверх 2  •  влево 1', 28, INK, family='DejaVu Sans Mono')
    return svg(b)


def pixel_smile():
    grid = ["00111100",
            "01000010",
            "10100101",
            "10000001",
            "10100101",
            "10011001",
            "01000010",
            "00111100"]
    b = ''
    s = 44
    x0, y0 = 400 - 4 * s, 225 - 4 * s
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            b += rect(x0 + c * s, y0 + r * s, s, s, fill=INK if v == '1' else "#ffffff", stroke="#9ca3af", sw=1)
    b += text(120, 225, '8 px', 30, BLUE, weight='bold') + text(680, 225, '8 px', 30, BLUE, weight='bold')
    return svg(b)


def file_tree():
    b = ''
    items = [(0, 'D:', True), (1, 'Учёба', True), (2, 'Python', True), (3, 'задача.py', False),
             (2, 'Фото', True), (3, 'класс.jpg', False), (1, 'Игры', True)]
    y = 50
    prev = {}
    for depth, name, folder in items:
        x = 80 + depth * 110
        if depth > 0:
            px, py = prev[depth - 1]
            b += line(px + 20, py + 18, px + 20, y, "#6b7280", 2) + line(px + 20, y, x - 6, y, "#6b7280", 2)
        if folder:
            b += path('M %g %g h 16 l 6 7 h 22 v 24 h -44 z' % (x, y - 16), fill="#fcd34d", stroke="#b45309", sw=2)
        else:
            b += path('M %g %g h 26 l 10 10 v 26 h -36 z' % (x + 4, y - 18), fill="#e0f2fe", stroke="#0369a1", sw=2)
        b += text(x + 56, y + 9, name, 26, INK, 'start', weight='bold' if name == 'задача.py' else 'normal')
        prev[depth] = (x, y)
        y += 56
    return svg(b)


# ----------------------------------------------------------------- math

def right_triangle():
    b = ''
    A, B, C = (150, 380), (550, 380), (150, 80)   # legs: AB horizontal (4), AC vertical (3)
    b += poly([A, B, C], fill="#ede9fe", stroke=INK, sw=4)
    b += rect(150, 350, 30, 30, sw=3)
    b += text(350, 420, '4', 36, weight='bold') + text(115, 245, '3', 36, weight='bold')
    b += text(380, 215, '?', 44, RED, weight='bold')
    return svg(b)


def circle_r():
    b = circle(400, 225, 170, fill="#ede9fe", stroke=INK, sw=4)
    b += circle(400, 225, 6, fill=INK, stroke=INK) + line(400, 225, 570, 225, BLUE, 4)
    b += text(485, 212, 'r = 3', 32, BLUE, weight='bold')
    b += text(400, 330, 'S = ?', 40, RED, weight='bold')
    return svg(b)


def parabola():
    b = ''
    ox, oy, s = 400, 250, 40   # origin and scale (1 unit = 40 px)
    for i in range(-9, 10):
        b += line(ox + i * s, 20, ox + i * s, 430, "#e5e7eb", 1)
    for j in range(-5, 6):
        b += line(20, oy + j * s, 780, oy + j * s, "#e5e7eb", 1)
    b += arrow(20, oy, 780, oy, INK, 2) + arrow(ox, 440, ox, 12, INK, 2)
    b += text(770, oy - 10, 'x', 24, INK, 'end', italic=True) + text(ox + 12, 30, 'y', 24, INK, 'start', italic=True)
    for i in (-2, -1, 1, 2, 3, 4):
        b += text(ox + i * s, oy + 24, str(i), 18, "#6b7280")
    for j in (-4, -2, 2, 4):
        b += text(ox - 8, oy - j * s + 6, str(j), 18, "#6b7280", 'end')
    pts = []
    x = -2.3
    while x <= 4.3:
        y = x * x - 2 * x - 3
        pts.append('%g,%g' % (ox + x * s, oy - y * s))
        x += 0.05
    b += '<polyline points="%s" fill="none" stroke="%s" stroke-width="4"/>' % (' '.join(pts), "#7c3aed")
    for px, py in ((-1, 0), (3, 0), (1, -4), (0, -3)):
        b += circle(ox + px * s, oy - py * s, 6, fill=RED, stroke=RED)
    return svg(b)


def cube():
    b = ''
    f = [(250, 170), (450, 170), (450, 370), (250, 370)]
    d = (90, -70)
    back = [(x + d[0], y + d[1]) for x, y in f]
    b += poly(f, fill="#ddd6fe", sw=4)
    b += poly([f[0], back[0], back[1], f[1]], fill="#ede9fe", sw=4)
    b += poly([f[1], back[1], back[2], f[2]], fill="#c4b5fd", sw=4)
    b += text(350, 405, '3 см', 30, weight='bold') + text(495, 300, '3 см', 30, weight='bold', anchor='start')
    b += text(250, 130, '3 см', 30, weight='bold', anchor='end')
    b += text(660, 240, 'V = ?', 40, RED, weight='bold')
    return svg(b)


def parallel_lines():
    b = ''
    ya, yb = 140, 320
    b += line(60, ya, 740, ya, INK, 4) + line(60, yb, 740, yb, INK, 4)
    b += text(750, ya + 8, 'a', 30, INK, 'start', italic=True) + text(750, yb + 8, 'b', 30, INK, 'start', italic=True)
    t = math.radians(65)
    # transversal through Q (bottom) and P (top) at 65 degrees to the horizontal
    qx = 320
    px = qx + (yb - ya) / math.tan(t)
    ext = 90
    x1, y1 = qx - ext * math.cos(t), yb + ext * math.sin(t)
    x2, y2 = px + ext * math.cos(t), ya - ext * math.sin(t)
    b += line(x1, y1, x2, y2, BLUE, 4)
    # angle at Q between ray right (0 deg) and ray to P (65 deg)
    b += arc(qx, yb, 46, 0, 65, RED, 4) + text(qx + 78, yb - 18, '65°', 30, RED, 'start', weight='bold')
    # alternate interior angle at P between ray left (180) and ray to Q (245)
    b += arc(px, ya, 46, 180, 245, GREEN, 4) + text(px - 74, ya + 40, 'x', 34, GREEN, 'end', weight='bold', italic=True)
    b += text(400, 420, 'a ∥ b', 28, INK)
    return svg(b)


def pie_chart():
    b = ''
    cx, cy, r = 280, 225, 170
    sectors = [('Математика', 0, 180, '#8b5cf6'), ('Физика', 180, 270, '#38bdf8'), ('Химия', 270, 360, '#fbbf24')]
    for name, a1, a2, col in sectors:
        x1, y1 = cx + r * math.cos(math.radians(a1 - 90)), cy + r * math.sin(math.radians(a1 - 90))
        x2, y2 = cx + r * math.cos(math.radians(a2 - 90)), cy + r * math.sin(math.radians(a2 - 90))
        large = 1 if a2 - a1 > 180 else 0
        b += path('M %g %g L %g %g A %g %g 0 %d 1 %g %g Z' % (cx, cy, x1, y1, r, r, large, x2, y2), fill=col, stroke='#fff', sw=3)
    y = 140
    for name, a1, a2, col in sectors:
        b += rect(520, y - 24, 30, 30, fill=col, stroke=col) + text(565, y, name, 28, INK, 'start')
        y += 60
    b += text(600, 360, 'Всего 40 учеников', 26, INK)
    return svg(b)


def number_line():
    b = ''
    ox, s, y = 400, 110, 220
    b += arrow(40, y, 770, y, INK, 3)
    for i in range(-3, 4):
        b += line(ox + i * s, y - 14, ox + i * s, y + 14, INK, 3) + text(ox + i * s, y + 50, str(i).replace('-', '−'), 28)
    for i in range(-6, 7):
        b += line(ox + i * s / 2, y - 7, ox + i * s / 2, y + 7, INK, 2)
    ax = ox - 2.5 * s
    b += circle(ax, y, 10, fill=RED, stroke=RED) + text(ax, y - 30, 'A', 34, RED, weight='bold')
    return svg(b)


def hexagon():
    pts = [(400 + 170 * math.cos(math.radians(60 * i)), 225 + 170 * math.sin(math.radians(60 * i))) for i in range(6)]
    b = poly(pts, fill="#ede9fe", stroke=INK, sw=4)
    b += text(400, 238, 'Σ углов = ?', 36, RED, weight='bold')
    return svg(b)


# ----------------------------------------------------------------- physics

def resistor(x, y, label):
    return rect(x, y - 18, 100, 36, fill="#fff7ed", sw=3) + text(x + 50, y - 30, label, 26, weight='bold')


def circuit_series():
    b = ''
    # battery left side, two resistors on top
    b += line(100, 120, 230, 120) + resistor(230, 120, '2 Ом') + line(330, 120, 450, 120)
    b += resistor(450, 120, '4 Ом') + line(550, 120, 700, 120)
    b += line(700, 120, 700, 340) + line(700, 340, 430, 340)
    b += line(430, 305, 430, 375, INK, 4) + line(400, 320, 400, 360, INK, 8)
    b += text(445, 300, '+', 26, RED, 'start', weight='bold') + text(385, 300, '−', 26, BLUE, 'end', weight='bold')
    b += line(400, 340, 100, 340) + line(100, 340, 100, 120)
    b += text(400, 225, 'R общ = ?', 34, RED, weight='bold')
    return svg(b)


def speed_graph():
    b = ''
    ox, oy = 110, 370
    sx, sy = 110, 10  # 1 s = 110 px, 1 m/s = 10 px
    b += arrow(ox, oy, 740, oy, INK, 3) + arrow(ox, oy, ox, 40, INK, 3)
    b += text(735, oy + 40, 't, с', 24, INK, 'end') + text(ox - 10, 50, 'v, м/с', 24, INK, 'end')
    for i in range(1, 6):
        b += line(ox + i * sx, oy - 6, ox + i * sx, oy + 6, INK, 2) + text(ox + i * sx, oy + 32, str(i), 22)
    for j in (10, 20, 30):
        b += line(ox - 6, oy - j * sy, ox + 6, oy - j * sy, INK, 2) + text(ox - 14, oy - j * sy + 8, str(j), 22, INK, 'end')
        b += line(ox, oy - j * sy, 700, oy - j * sy, "#e5e7eb", 1)
    b += rect(ox, oy - 20 * sy, 5 * sx, 20 * sy, fill="#ccfbf1", stroke="none", sw=0)
    b += line(ox, oy - 20 * sy, ox + 5 * sx, oy - 20 * sy, "#0f766e", 5)
    b += line(ox + 5 * sx, oy - 20 * sy, ox + 5 * sx, oy, "#0f766e", 2, dash="8 6")
    return svg(b)


def lever():
    b = ''
    b += poly([(400, 300), (370, 360), (430, 360)], fill="#9ca3af", sw=3)
    b += line(100, 300, 700, 300, "#78350f", 10)
    s = 100  # 1 m = 100 px
    # left: 2 kg at 3 m, right: ? at 2 m
    lx, rx = 400 - 3 * s, 400 + 2 * s
    b += line(lx, 300, lx, 230, INK, 2) + rect(lx - 40, 170, 80, 60, fill="#0f766e", stroke=INK) + text(lx, 210, '2 кг', 24, '#fff', weight='bold')
    b += line(rx, 300, rx, 230, INK, 2) + rect(rx - 40, 170, 80, 60, fill="#f97316", stroke=INK) + text(rx, 212, '?', 34, '#fff', weight='bold')
    b += line(lx, 395, 400, 395, BLUE, 2) + text((lx + 400) / 2, 425, '3 м', 26, BLUE, weight='bold')
    b += line(400, 395, rx, 395, BLUE, 2) + text((400 + rx) / 2, 425, '2 м', 26, BLUE, weight='bold')
    b += line(lx, 385, lx, 405, BLUE, 2) + line(400, 385, 400, 405, BLUE, 2) + line(rx, 385, rx, 405, BLUE, 2)
    b += text(400, 70, 'Рычаг в равновесии', 30)
    return svg(b)


def magnets():
    b = ''
    b += rect(80, 180, 130, 90, fill="#ef4444", stroke=INK) + rect(210, 180, 130, 90, fill="#3b82f6", stroke=INK)
    b += text(145, 240, 'S', 44, '#fff', weight='bold') + text(275, 240, 'N', 44, '#fff', weight='bold')
    b += rect(460, 180, 130, 90, fill="#3b82f6", stroke=INK) + rect(590, 180, 130, 90, fill="#ef4444", stroke=INK)
    b += text(525, 240, 'N', 44, '#fff', weight='bold') + text(655, 240, 'S', 44, '#fff', weight='bold')
    b += text(400, 240, '?', 60, INK, weight='bold')
    return svg(b)


def lens():
    b = ''
    b += line(40, 225, 760, 225, "#9ca3af", 2, dash="10 8")
    b += path('M 400 70 Q 450 225 400 380 Q 350 225 400 70 Z', fill="#bae6fd", stroke="#0369a1", sw=3)
    fx = 600
    for y in (120, 175, 275, 330):
        b += arrow(60, y, 398, y, ORANGE, 3, 0.1)
        b += line(398, y, fx, 225, ORANGE, 3)
        # continue a bit beyond focus
        b += line(fx, 225, fx + (fx - 398) * 0.35, 225 + (225 - y) * 0.35, ORANGE, 2, dash="6 6")
    b += circle(fx, 225, 7, fill=INK, stroke=INK) + text(fx, 265, 'F', 30, INK, weight='bold')
    return svg(b)


def thermometer():
    b = ''
    x = 400
    top, bottom = 40, 360   # 0..40 degrees
    def ypos(t):
        return bottom - (t / 40) * (bottom - top)
    b += rect(x - 18, top - 15, 36, bottom - top + 30, fill="#f9fafb", stroke=INK, sw=3, rx=18)
    b += circle(x, bottom + 40, 34, fill=RED, stroke=INK, sw=3)
    b += rect(x - 8, ypos(26), 16, bottom + 20 - ypos(26), fill=RED, stroke="none", sw=0)
    for t in range(0, 41, 2):
        long_ = t % 10 == 0
        b += line(x + 22, ypos(t), x + (52 if long_ else 36), ypos(t), INK, 3 if long_ else 2)
        if long_:
            b += text(x + 64, ypos(t) + 9, str(t), 26, INK, 'start', weight='bold')
    b += text(x - 60, 120, '°C', 34, INK, 'end', weight='bold')
    return svg(b)


def forces():
    b = ''
    ox, oy, s = 300, 340, 55
    b += circle(ox, oy, 12, fill=INK, stroke=INK)
    b += arrow(ox, oy, ox + 4 * s, oy, RED, 5, 18) + text(ox + 2 * s, oy + 40, 'F₁ = 4 Н', 28, RED, weight='bold')
    b += arrow(ox, oy, ox, oy - 3 * s, BLUE, 5, 18) + text(ox - 20, oy - 1.5 * s, 'F₂ = 3 Н', 28, BLUE, 'end', weight='bold')
    b += rect(ox, oy - 28, 28, 28, stroke=INK, sw=2)
    b += line(ox + 4 * s, oy, ox + 4 * s, oy - 3 * s, "#9ca3af", 2, dash="8 6")
    b += line(ox, oy - 3 * s, ox + 4 * s, oy - 3 * s, "#9ca3af", 2, dash="8 6")
    b += arrow(ox, oy, ox + 4 * s, oy - 3 * s, GREEN, 5, 18) + text(ox + 4 * s + 20, oy - 3 * s - 10, 'F = ?', 32, GREEN, 'start', weight='bold')
    return svg(b)


# ----------------------------------------------------------------- chemistry

def water():
    b = ''
    ox, oy = 400, 190
    ang = math.radians(104.5 / 2)
    L = 150
    h1 = (ox - L * math.sin(ang), oy + L * math.cos(ang))
    h2 = (ox + L * math.sin(ang), oy + L * math.cos(ang))
    for h in (h1, h2):
        b += line(ox, oy, h[0], h[1], "#6b7280", 14)
    b += circle(ox, oy, 80, fill="#ef4444", stroke="#991b1b", sw=3) + text(ox, oy + 16, 'O', 50, '#fff', weight='bold')
    for h in (h1, h2):
        b += circle(h[0], h[1], 52, fill="#f3f4f6", stroke="#6b7280", sw=3) + text(h[0], h[1] + 14, 'H', 40, INK, weight='bold')
    return svg(b)


def element_cell():
    b = rect(260, 50, 280, 340, fill="#e0f2fe", stroke="#0369a1", sw=5, rx=12)
    b += text(300, 110, '8', 48, INK, 'start', weight='bold')
    b += text(400, 250, 'O', 140, "#0369a1", weight='bold')
    b += text(400, 310, 'Кислород', 34, INK)
    b += text(400, 360, '15,999', 30, "#475569")
    return svg(b)


def ph_scale():
    b = ''
    cols = ['#dc2626', '#ef4444', '#f97316', '#fb923c', '#facc15', '#fde047', '#a3e635', '#22c55e',
            '#14b8a6', '#06b6d4', '#3b82f6', '#4f46e5', '#7c3aed', '#9333ea', '#6b21a8']
    x0, w = 40, 48
    for i in range(15):
        b += rect(x0 + i * w, 160, w, 80, fill=cols[i], stroke='#fff', sw=2) + text(x0 + i * w + w / 2, 275, str(i), 22)
    mx = x0 + 2 * w + w / 2
    b += poly([(mx, 150), (mx - 18, 110), (mx + 18, 110)], fill=INK, stroke=INK) + text(mx, 95, 'раствор', 26, INK, weight='bold')
    b += text(400, 340, 'шкала pH', 30, INK)
    return svg(b)


def methane():
    b = ''
    cx, cy = 400, 225
    b += text(cx, cy + 20, 'C', 60, INK, weight='bold')
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        b += line(cx + dx * 45, cy + dy * 45, cx + dx * 115, cy + dy * 115, INK, 5)
        b += text(cx + dx * 150, cy + dy * 150 + 20, 'H', 56, INK, weight='bold')
    return svg(b)


def ethanol():
    b = ''
    y = 225
    xs = [170, 330, 470]
    b += text(xs[0], y + 20, 'C', 56, INK, weight='bold') + text(xs[1], y + 20, 'C', 56, INK, weight='bold')
    b += text(xs[2], y + 20, 'O', 56, RED, weight='bold') + text(600, y + 20, 'H', 56, INK, weight='bold')
    b += line(xs[0] + 35, y, xs[1] - 35, y, INK, 5) + line(xs[1] + 35, y, xs[2] - 35, y, INK, 5) + line(xs[2] + 35, y, 600 - 35, y, INK, 5)
    for x in xs[:2]:
        b += line(x, y - 45, x, y - 105, INK, 5) + text(x, y - 115, 'H', 56, INK, weight='bold')
        b += line(x, y + 40, x, y + 100, INK, 5) + text(x, y + 155, 'H', 56, INK, weight='bold')
    b += line(xs[0] - 35, y, 75, y, INK, 5) + text(50, y + 20, 'H', 56, INK, weight='bold')
    return svg(b)


def shells_na():
    b = ''
    cx, cy = 400, 225
    b += circle(cx, cy, 34, fill="#f97316", stroke="#9a3412") + text(cx, cy + 10, '+11', 26, '#fff', weight='bold')
    for r, n in ((80, 2), (135, 8), (190, 1)):
        b += circle(cx, cy, r, stroke="#9ca3af", sw=2)
        for k in range(n):
            a = math.radians(90 + 360 * k / n)
            b += circle(cx + r * math.cos(a), cy - r * math.sin(a), 11, fill=BLUE, stroke="#1e3a8a", sw=2)
    return svg(b)


def flask():
    b = path('M 360 60 L 360 170 L 240 380 Q 232 400 255 400 L 545 400 Q 568 400 560 380 L 440 170 L 440 60',
             fill="#f0f9ff", stroke=INK, sw=5)
    b += line(345, 60, 455, 60, INK, 6)
    b += path('M 285 320 L 515 320 L 555 385 Q 560 395 545 395 L 255 395 Q 240 395 245 385 Z', fill="#a5f3fc", stroke="none", sw=0)
    for y, l in ((280, 40), (320, 60), (240, 30)):
        b += line(400 - l, y, 400 - l + 20, y, "#64748b", 2)
    return svg(b)


# ----------------------------------------------------------------- biology

def plant_cell():
    b = ''
    b += rect(150, 60, 500, 320, fill="#dcfce7", stroke="#166534", sw=10, rx=30)        # 1 cell wall
    b += rect(165, 75, 470, 290, fill="#f0fdf4", stroke="#4ade80", sw=3, rx=24)
    b += '<ellipse cx="460" cy="230" rx="140" ry="95" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="3"/>'  # 4 vacuole
    b += circle(270, 160, 45, fill="#c4b5fd", stroke="#5b21b6", sw=3) + circle(270, 160, 14, fill="#5b21b6", stroke="#5b21b6")  # 3 nucleus
    for cx, cy in ((240, 300), (330, 330), (560, 110), (290, 240)):
        b += ('<ellipse cx="%d" cy="%d" rx="34" ry="16" fill="#22c55e" stroke="#14532d" stroke-width="3"/>' % (cx, cy))
        b += line(cx - 22, cy, cx + 22, cy, "#14532d", 2)
    labels = [('1', 150, 60, 80, 30), ('2', 240, 300, 80, 410), ('3', 270, 160, 90, 170), ('4', 520, 230, 720, 300)]
    for n, tx, ty, lx, ly in labels:
        b += line(tx, ty, lx, ly, INK, 2) + circle(lx, ly, 20, fill="#fff", stroke=INK, sw=2) + text(lx, ly + 9, n, 26, INK, weight='bold')
    return svg(b)


def food_chain():
    b = ''
    items = [('Трава', '#bbf7d0'), ('Заяц', '#fde68a'), ('Лиса', '#fdba74'), ('Беркут', '#fca5a5')]
    x = 40
    for i, (name, col) in enumerate(items):
        b += rect(x, 185, 150, 80, fill=col, rx=14) + text(x + 75, 236, name, 30, INK, weight='bold')
        if i < 3:
            b += arrow(x + 152, 225, x + 200, 225, INK, 4)
        x += 195
    return svg(b)


def punnett():
    b = ''
    x0, y0, s = 260, 90, 120
    b += text(x0 - 40, 70, '♀ \\ ♂', 22, INK)
    for i, g in enumerate(('A', 'a')):
        b += text(x0 + s * i + s / 2, y0 - 10, g, 40, BLUE, weight='bold')
        b += text(x0 - 30, y0 + s * i + s / 2 + 14, g, 40, RED, weight='bold')
    cells = [['AA', 'Aa'], ['Aa', '?']]
    for r in range(2):
        for c in range(2):
            b += rect(x0 + c * s, y0 + r * s, s, s, fill="#f0fdf4", stroke="#166534", sw=3)
            b += text(x0 + c * s + s / 2, y0 + r * s + s / 2 + 14, cells[r][c], 38, RED if cells[r][c] == '?' else INK, weight='bold')
    b += text(400, 420, 'Aa × Aa', 30, INK)
    return svg(b)


def insect():
    b = ''
    # head, thorax, abdomen
    b += circle(230, 225, 45, fill="#78350f", stroke=INK) + '<ellipse cx="350" cy="225" rx="70" ry="55" fill="#92400e" stroke="#1f2937" stroke-width="3"/>'
    b += '<ellipse cx="540" cy="225" rx="125" ry="70" fill="#b45309" stroke="#1f2937" stroke-width="3"/>'
    for x in (320, 350, 380):
        b += path('M %d 270 L %d 330 L %d 380' % (x, x - 30, x - 60 + (x - 350)), stroke=INK, sw=5)
        b += path('M %d 180 L %d 120 L %d 70' % (x, x - 30, x - 60 + (x - 350)), stroke=INK, sw=5)
    b += path('M 205 190 Q 160 110 120 100', stroke=INK, sw=4) + path('M 225 182 Q 200 100 170 70', stroke=INK, sw=4)
    b += circle(212, 215, 8, fill="#fff", stroke="#fff")
    for x in (490, 540, 590):
        b += line(x, 165, x, 285, "#78350f", 3)
    return svg(b)


def dna():
    b = ''
    cols = ['#ef4444', '#3b82f6', '#22c55e', '#f59e0b']
    pts1, pts2 = [], []
    for i in range(0, 701, 5):
        x = 50 + i
        y1 = 225 + 110 * math.sin(i / 700 * 4 * math.pi)
        y2 = 225 - 110 * math.sin(i / 700 * 4 * math.pi)
        pts1.append('%g,%g' % (x, y1))
        pts2.append('%g,%g' % (x, y2))
    k = 0
    for i in range(10, 700, 28):
        x = 50 + i
        s = math.sin(i / 700 * 4 * math.pi)
        if abs(s) < 0.15:
            continue
        b += line(x, 225 + 110 * s, x, 225, cols[k % 4], 6, cap='butt') + line(x, 225, x, 225 - 110 * s, cols[(k + 1) % 4], 6, cap='butt')
        k += 1
    b += '<polyline points="%s" fill="none" stroke="#1e3a8a" stroke-width="9"/>' % ' '.join(pts1)
    b += '<polyline points="%s" fill="none" stroke="#7c2d12" stroke-width="9"/>' % ' '.join(pts2)
    return svg(b)


# ----------------------------------------------------------------- history

def kg_flag():
    b = rect(100, 45, 600, 360, fill="#e8112d", stroke="none", sw=0)
    cx, cy = 400, 225
    rays = ''
    for i in range(40):
        a = math.radians(i * 9)
        rays += line(cx + 64 * math.cos(a), cy + 64 * math.sin(a), cx + 118 * math.cos(a), cy + 118 * math.sin(a), "#ffef00", 5, cap='butt')
    b += rays + circle(cx, cy, 66, fill="#ffef00", stroke="none", sw=0)
    b += circle(cx, cy, 46, fill="#e8112d", stroke="none", sw=0) + circle(cx, cy, 44, stroke="#ffef00", sw=5)
    # tunduk: three crossing lines each way, the outer ones bowed away from the centre
    b += '<clipPath id="tk"><circle cx="%g" cy="%g" r="42"/></clipPath><g clip-path="url(#tk)">' % (cx, cy)
    for off in (-17, 0, 17):
        bow = 0 if off == 0 else (8 if off > 0 else -8)
        b += path('M %g %g Q %g %g %g %g' % (cx - 50, cy + off, cx, cy + off + bow, cx + 50, cy + off), stroke="#ffef00", sw=5)
        b += path('M %g %g Q %g %g %g %g' % (cx + off, cy - 50, cx + off + bow, cy, cx + off, cy + 50), stroke="#ffef00", sw=5)
    b += '</g>'
    return svg(b, "#f8fafc")


def pyramids():
    b = '<rect width="800" height="300" fill="#bae6fd"/>' + circle(660, 90, 45, fill="#fde047", stroke="none", sw=0)
    b += '<rect y="300" width="800" height="150" fill="#fcd34d"/>'
    for (cx, base, h) in ((250, 330, 230), (520, 260, 170), (690, 150, 100)):
        b += poly([(cx - base / 2, 320), (cx, 320 - h), (cx + base / 2, 320)], fill="#d97706", stroke="#92400e", sw=3)
        b += poly([(cx, 320 - h), (cx + base / 2, 320), (cx + base / 6, 320)], fill="#b45309", stroke="#92400e", sw=2)
    return svg(b)


def roman_tablet():
    b = rect(110, 110, 580, 230, fill="#d6d3d1", stroke="#57534e", sw=6, rx=8)
    b += rect(130, 130, 540, 190, fill="#e7e5e4", stroke="#a8a29e", sw=2, rx=4)
    b += text(400, 262, 'MCMXCI', 104, "#44403c", weight='bold', family='DejaVu Serif')
    return svg(b)


def yurt():
    b = '<rect width="800" height="320" fill="#bfdbfe"/><rect y="320" width="800" height="130" fill="#86efac"/>'
    b += poly([(80, 320), (260, 170), (420, 320)], fill="#94a3b8", stroke="none", sw=0)
    b += poly([(500, 320), (690, 140), (800, 260), (800, 320)], fill="#94a3b8", stroke="none", sw=0)
    b += poly([(600, 230), (690, 140), (740, 190)], fill="#f8fafc", stroke="none", sw=0)
    b += rect(250, 230, 300, 120, fill="#f5f5f4", stroke="#57534e", sw=4)
    b += path('M 240 232 Q 400 90 560 232 Z', fill="#fafaf9", stroke="#57534e", sw=4)
    b += rect(372, 120, 56, 14, fill="#a16207", stroke="#57534e", sw=2)
    for x in range(270, 540, 40):
        b += line(x, 255, x + 20, 255, "#b91c1c", 6)
    b += rect(372, 270, 56, 80, fill="#b91c1c", stroke="#57534e", sw=3)
    b += path('M 252 232 L 548 232', stroke="#b91c1c", sw=6)
    return svg(b)


def colosseum():
    b = '<rect width="800" height="450" fill="#e0f2fe"/><rect y="380" width="800" height="70" fill="#d6d3d1"/>'
    # broken top outline
    top = 'M 80 380 L 80 110 L 260 110 L 300 70 L 720 70 L 720 380 Z'
    b += path(top, fill="#e7c9a0", stroke="#92400e", sw=3)
    rows = [(320, 380), (230, 300), (150, 220)]
    for (y1, y2) in rows:
        b += line(80, y2, 720, y2, "#92400e", 4)
        for i in range(10):
            x = 100 + i * 62
            if y1 == 150 and x < 260:
                continue
            b += path('M %d %d L %d %d A 20 20 0 0 1 %d %d L %d %d Z' % (x, y2 - 6, x, y1 + 20, x + 40, y1 + 20, x + 40, y2 - 6),
                      fill="#7c2d12", stroke="#92400e", sw=2)
    b += line(80, 150, 720, 150, "#92400e", 4)
    return svg(b)


# ----------------------------------------------------------------- geography

def compass():
    b = ''
    cx, cy = 400, 225
    b += circle(cx, cy, 170, fill="#f8fafc", stroke=INK, sw=3)
    b += poly([(cx, cy - 150), (cx - 20, cy), (cx + 20, cy)], fill=RED, stroke=INK, sw=2)
    b += poly([(cx, cy + 150), (cx - 20, cy), (cx + 20, cy)], fill="#cbd5e1", stroke=INK, sw=2)
    b += poly([(cx + 150, cy), (cx, cy - 20), (cx, cy + 20)], fill="#facc15", stroke=INK, sw=2)
    b += poly([(cx - 150, cy), (cx, cy - 20), (cx, cy + 20)], fill="#cbd5e1", stroke=INK, sw=2)
    b += text(cx, cy - 180, 'С', 36, RED, weight='bold') + text(cx + 210, cy + 18, '?', 54, BLUE, weight='bold')
    return svg(b)


def globe_equator():
    b = circle(400, 225, 190, fill="#bfdbfe", stroke="#1e3a8a", sw=4)
    for lat in (-60, -30, 30, 60):
        y = 225 - 190 * math.sin(math.radians(lat))
        rx = 190 * math.cos(math.radians(lat))
        b += '<ellipse cx="400" cy="%g" rx="%g" ry="%g" fill="none" stroke="#60a5fa" stroke-width="2"/>' % (y, rx, rx * 0.12)
    for k in (0.35, 0.75):
        b += '<ellipse cx="400" cy="225" rx="%g" ry="190" fill="none" stroke="#60a5fa" stroke-width="2"/>' % (190 * k)
    b += line(400, 35, 400, 415, "#60a5fa", 2)
    b += '<ellipse cx="400" cy="225" rx="190" ry="23" fill="none" stroke="#dc2626" stroke-width="6"/>'
    b += arrow(690, 120, 595, 215, RED, 4) + text(700, 112, '?', 50, RED, 'start', weight='bold')
    return svg(b)


def mountain_temp():
    b = '<rect width="800" height="450" fill="#e0f2fe"/>'
    b += poly([(120, 400), (430, 70), (720, 400)], fill="#a8a29e", stroke="#57534e", sw=3)
    b += poly([(360, 145), (430, 70), (500, 145), (465, 135), (430, 155), (395, 135)], fill="#ffffff", stroke="#57534e", sw=2)
    b += line(0, 400, 800, 400, "#57534e", 3)
    b += line(150, 400, 150, 110, BLUE, 2) + arrow(150, 400, 150, 110, BLUE, 2)
    b += text(160, 120, '3 км', 28, BLUE, 'start', weight='bold')
    b += line(140, 110, 560, 110, BLUE, 2, dash="8 6")
    b += text(330, 385, '+24 °C', 32, RED, weight='bold') + text(600, 120, '? °C', 34, RED, 'start', weight='bold')
    return svg(b)


def two_clocks(h1, m1, h2, m2, l1, l2, unknown_second=True):
    b = ''
    for i, (h, m, lab) in enumerate(((h1, m1, l1), (h2, m2, l2))):
        cx, cy = 220 + i * 360, 200
        b += clock_face(cx, cy, 140, h, m, hide=(unknown_second and i == 1))
        b += text(cx, 395, lab, 30, INK, weight='bold')
    return svg(b)


def clock_face(cx, cy, r, h, m, hide=False):
    b = circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=6)
    for k in range(60):
        a = math.radians(k * 6)
        l1 = r - (18 if k % 5 == 0 else 8)
        b += line(cx + l1 * math.sin(a), cy - l1 * math.cos(a), cx + (r - 4) * math.sin(a), cy - (r - 4) * math.cos(a),
                  INK, 4 if k % 5 == 0 else 1.5)
    for n in range(1, 13):
        a = math.radians(n * 30)
        b += text(cx + (r - 40) * math.sin(a), cy - (r - 40) * math.cos(a) + 10, str(n), r * 0.2, INK, weight='bold')
    if hide:
        b += text(cx, cy + 30, '?', r * 0.8, BLUE, weight='bold')
        return b
    ha = math.radians((h % 12) * 30 + m * 0.5)
    ma = math.radians(m * 6)
    b += line(cx, cy, cx + r * 0.5 * math.sin(ha), cy - r * 0.5 * math.cos(ha), INK, 10)
    b += line(cx, cy, cx + r * 0.78 * math.sin(ma), cy - r * 0.78 * math.cos(ma), INK, 6)
    b += circle(cx, cy, 9, fill=RED, stroke=RED)
    return b


def one_clock(h, m):
    return svg(clock_face(400, 225, 190, h, m))


def coord_grid():
    b = ''
    x0, y0, s = 140, 380, 130  # 10 degrees = 130 px; origin at (0 lat, 0 lon)
    for i in range(0, 5):
        b += line(x0 + i * s, 40, x0 + i * s, y0, "#93c5fd" if i else "#1d4ed8", 2 if i else 4)
        b += text(x0 + i * s, y0 + 34, '%d°' % (i * 10), 24, INK)
    for j in range(0, 3):
        b += line(x0, y0 - j * s, x0 + 4 * s, y0 - j * s, "#93c5fd" if j else "#dc2626", 2 if j else 4)
        b += text(x0 - 14, y0 - j * s + 8, '%d°' % (j * 10), 24, INK, 'end')
    b += text(x0 + 4 * s + 12, y0 + 8, 'экватор', 22, RED, 'start')
    b += text(x0 + 6, 32, 'нулевой меридиан', 22, "#1d4ed8", 'start')
    px, py = x0 + 3 * s, y0 - 2 * s
    b += circle(px, py, 13, fill=ORANGE, stroke=INK, sw=2) + text(px + 22, py - 14, 'M', 34, ORANGE, 'start', weight='bold')
    b += text(x0 + 2 * s, 440, 'восточная долгота →', 22, "#475569")
    b += '<text x="60" y="230" font-size="22" fill="#475569" transform="rotate(-90 60 230)" text-anchor="middle">северная широта →</text>'
    return svg(b)


def map_scale():
    b = '<rect width="800" height="450" fill="#ecfccb"/>'
    s = 120  # 1 cm on the map = 120 px
    ax, bx, y = 160, 160 + 4 * s, 200
    b += path('M 60 330 C 200 280 300 360 420 320 S 650 260 760 300', stroke="#38bdf8", sw=10)
    b += circle(ax, y, 14, fill=RED, stroke=INK, sw=2) + text(ax, y - 26, 'село А', 26, INK, weight='bold')
    b += circle(bx, y, 14, fill=RED, stroke=INK, sw=2) + text(bx, y - 26, 'село Б', 26, INK, weight='bold')
    b += line(ax, y + 40, bx, y + 40, INK, 2)
    for k in range(5):
        b += line(ax + k * s, y + 30, ax + k * s, y + 50, INK, 2) + text(ax + k * s, y + 76, '%d см' % k, 20, INK)
    b += rect(560, 380, 220, 50, fill="#ffffff", stroke=INK, sw=2) + text(670, 414, '1 см : 5 км', 26, INK, weight='bold')
    return svg(b)


# ----------------------------------------------------------------- literature

def steamboat():
    b = '<rect width="800" height="300" fill="#bfdbfe"/><rect y="300" width="800" height="150" fill="#1d4ed8"/>'
    b += poly([(400, 60), (250, 95), (440, 95)], fill="#fde68a", stroke="none", sw=0)
    b += path('M 150 270 L 650 270 L 600 330 L 200 330 Z', fill="#ffffff", stroke="#334155", sw=4)
    b += rect(230, 210, 340, 60, fill="#ffffff", stroke="#334155", sw=4)
    b += rect(300, 170, 200, 40, fill="#ffffff", stroke="#334155", sw=4)
    for x in range(250, 560, 45):
        b += circle(x + 15, 240, 10, fill="#93c5fd", stroke="#334155", sw=2)
    b += rect(430, 110, 40, 60, fill="#ffffff", stroke="#334155", sw=4) + rect(430, 110, 40, 14, fill="#dc2626", stroke="#334155", sw=2)
    b += path('M 450 105 C 470 80 430 60 460 40', stroke="#94a3b8", sw=8)
    for x in range(40, 800, 120):
        b += path('M %d 360 q 30 -16 60 0' % x, stroke="#93c5fd", sw=3)
    return svg(b)


def quill():
    b = '<rect width="800" height="450" fill="#fffbeb"/>'
    b += path('M 600 40 C 470 90 360 210 300 340 L 320 345 C 400 230 500 140 610 60 Z', fill="#f8fafc", stroke="#334155", sw=3)
    b += path('M 610 50 C 520 120 420 220 315 342', stroke="#334155", sw=2)
    for k in range(8):
        t = k / 8
        x = 600 - t * 270
        y = 50 + t * 280
        b += line(x, y, x - 40 + k * 3, y - 20 + k * 2, "#94a3b8", 2)
    b += line(300, 340, 285, 380, INK, 4)
    b += path('M 160 400 Q 260 380 330 400', stroke=INK, sw=3)
    b += rect(470, 330, 120, 80, fill="#1e293b", stroke=INK, sw=3, rx=10) + rect(500, 315, 60, 20, fill="#334155", stroke=INK, sw=2)
    return svg(b)


# ----------------------------------------------------------------- English

def ball(cx, cy, r=36):
    return (circle(cx, cy, r, fill="#ef4444", stroke="#7f1d1d", sw=3) +
            path('M %g %g Q %g %g %g %g' % (cx - r, cy, cx, cy - r * 0.6, cx + r, cy), stroke="#fff", sw=4))


def box(x, y, w=180, h=130, open_top=False):
    s = rect(x, y, w, h, fill="#d97706", stroke="#78350f", sw=4)
    s += line(x, y + 20, x + w, y + 20, "#78350f", 2)
    return s


def ball_on_box():
    return svg(box(310, 250) + ball(400, 212) + line(100, 380, 700, 380, "#57534e", 3))


def ball_under_table():
    b = rect(220, 170, 360, 26, fill="#92400e", stroke="#78350f", sw=3)
    b += rect(240, 196, 22, 184, fill="#92400e", stroke="#78350f", sw=3) + rect(538, 196, 22, 184, fill="#92400e", stroke="#78350f", sw=3)
    b += ball(400, 344) + line(100, 380, 700, 380, "#57534e", 3)
    return svg(b)


def ball_between():
    return svg(box(130, 250) + box(490, 250) + ball(400, 344) + line(60, 380, 740, 380, "#57534e", 3))


def ball_in_box():
    b = ball(400, 300, 46)
    b += path('M 290 230 L 290 380 L 510 380 L 510 230', fill="none", stroke="#78350f", sw=5)
    b += poly([(290, 230), (290, 380), (510, 380), (510, 230), (440, 230), (440, 236), (360, 236), (360, 230)], fill="#d97706cc", stroke="#78350f", sw=4)
    b = ball(400, 262, 46) + poly([(290, 260), (510, 260), (510, 380), (290, 380)], fill="#d97706", stroke="#78350f", sw=4)
    b += path('M 290 260 L 250 200 M 510 260 L 550 200', stroke="#78350f", sw=5)
    b += line(100, 380, 700, 380, "#57534e", 3)
    return svg(b)


def sun():
    b = '<rect width="800" height="450" fill="#e0f2fe"/>'
    for i in range(12):
        a = math.radians(i * 30)
        b += line(400 + 110 * math.cos(a), 225 + 110 * math.sin(a), 400 + 170 * math.cos(a), 225 + 170 * math.sin(a), "#f59e0b", 12)
    b += circle(400, 225, 90, fill="#facc15", stroke="#f59e0b", sw=6)
    return svg(b)


def rain():
    b = '<rect width="800" height="450" fill="#e2e8f0"/>'
    b += path('M 230 220 C 190 220 180 150 240 145 C 250 85 340 70 370 120 C 400 70 500 80 510 140 C 580 135 590 220 530 220 Z',
              fill="#94a3b8", stroke="#475569", sw=4)
    for i, x in enumerate(range(250, 540, 45)):
        y = 260 + (i % 2) * 40
        b += line(x, y, x - 14, y + 44, "#2563eb", 6)
    return svg(b)


def triangle_shape():
    return svg(poly([(400, 70), (600, 380), (200, 380)], fill="#a78bfa", stroke="#5b21b6", sw=6))


def apples():
    b = ''
    for i in range(5):
        cx = 120 + i * 140
        cy = 240
        b += path('M %g %g C %g %g %g %g %g %g C %g %g %g %g %g %g' % (
            cx, cy - 40, cx - 80, cy - 80, cx - 70, cy + 60, cx, cy + 55,
            cx + 70, cy + 60, cx + 80, cy - 80, cx, cy - 40), fill="#dc2626", stroke="#7f1d1d", sw=3)
        b += path('M %g %g q 4 -26 14 -36' % (cx, cy - 40), stroke="#78350f", sw=5)
        b += path('M %g %g q 26 -20 44 -4 q -24 14 -44 4 z' % (cx + 6, cy - 58), fill="#22c55e", stroke="#14532d", sw=2)
    return svg(b)


def banana():
    b = path('M 180 200 C 260 390 560 390 650 170 C 660 150 690 160 680 185 C 600 450 220 430 160 215 C 155 195 175 185 180 200 Z',
             fill="#facc15", stroke="#a16207", sw=5)
    b += path('M 650 170 l 18 -40 l 18 8 l -10 40', fill="#65a30d", stroke="#3f6212", sw=3)
    b += path('M 200 230 C 290 380 540 380 640 200', stroke="#ca8a04", sw=3)
    return svg(b)


def face():
    b = circle(400, 225, 170, fill="#fde68a", stroke="#92400e", sw=5)
    b += circle(335, 175, 18, fill=INK, stroke=INK) + circle(465, 175, 18, fill=INK, stroke=INK)
    b += path('M 400 190 L 375 265 L 415 265', stroke="#92400e", sw=6)
    b += path('M 320 300 Q 400 360 480 300', stroke="#b91c1c", sw=7)
    b += path('M 228 200 C 200 200 200 260 230 262', fill="#fde68a", stroke="#92400e", sw=5)
    b += path('M 572 200 C 600 200 600 260 570 262', fill="#fde68a", stroke="#92400e", sw=5)
    b += arrow(690, 330, 425, 255, BLUE, 5, 20) + text(700, 350, '?', 50, BLUE, 'start', weight='bold')
    return svg(b)
