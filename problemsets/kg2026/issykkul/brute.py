# Rebuilds the hull from scratch for every question (small tests only).
import sys


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def hull(pts):
    pts = sorted(set(pts))
    if len(pts) <= 2:
        return pts
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def on_segment(a, b, p):
    return cross(a, b, p) == 0 and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and \
        min(a[1], b[1]) <= p[1] <= max(a[1], b[1])


def inside(h, p):
    if not h:
        return False
    if len(h) == 1:
        return h[0] == p
    if len(h) == 2:
        return on_segment(h[0], h[1], p)
    return all(cross(h[i], h[(i + 1) % len(h)], p) >= 0 for i in range(len(h)))


def main():
    d = sys.stdin.read().split()
    q = int(d[0])
    p = 1
    pts = []
    out = []
    h = []
    dirty = False
    for _ in range(q):
        c = d[p]
        p += 1
        if c == 'A':
            if dirty:
                h, dirty = hull(pts), False
            area = 0
            if len(h) >= 3:
                for i in range(len(h)):
                    a, b = h[i], h[(i + 1) % len(h)]
                    area += a[0] * b[1] - a[1] * b[0]
            out.append(str(abs(area)))
            continue
        x, y = int(d[p]), int(d[p + 1])
        p += 2
        if c == '+':
            pts.append((x, y))
            dirty = True
        else:
            if dirty:
                h, dirty = hull(pts), False
            out.append('YES' if inside(h, (x, y)) else 'NO')
    print('\n'.join(out))


main()
