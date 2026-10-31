"""Default avatar: a Kyrgyz shyrdak ornament ("кочкор мүйүз") drawn from the username.

The same name always gives the same picture. The algorithm matches the preview
page shown to the site owner (FNV-1a hash + mulberry32), so keep it stable.
"""
import math

_M = 0xFFFFFFFF

_PALETTES = (
    ('#B3262E', '#F6E7C8', '#1F3A68'),
    ('#1F3A68', '#E9B949', '#B3262E'),
    ('#6E1A27', '#EBC27E', '#2E6B57'),
    ('#1E6B52', '#F3DCA8', '#B3262E'),
    ('#2B2340', '#F2A541', '#D9483B'),
    ('#F3E3C3', '#8E1F2A', '#1F3A68'),
    ('#0F4C5C', '#F4D58D', '#E36414'),
    ('#5A2A82', '#F2C14E', '#F6E7C8'),
)
_CORNER = 'M50 50L32 32M32 32C24 24 12 27 13 37C14 45 25 44 25 37M32 32C24 24 27 12 37 13C45 14 44 25 37 25'
_AXIS = 'M50 50L50 31C50 21 39 16 35 23C32 29 39 33 43 29M50 31C50 21 61 16 65 23C68 29 61 33 57 29'


def _imul(a, b):
    return (a * b) & _M


def _fnv(s):
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = _imul(h, 0x01000193)
    return h


def _rng(seed):
    state = [seed & _M]

    def next_float():
        s = state[0] = (state[0] + 0x6D2B79F5) & _M
        t = _imul(s ^ (s >> 15), 1 | s)
        t = ((t + _imul(t ^ (t >> 7), 61 | t)) & _M) ^ t
        return ((t ^ (t >> 14)) & _M) / 4294967296
    return next_float


def _f(n):
    v = math.floor(n * 10 + 0.5) / 10
    return str(int(v)) if v == int(v) else repr(v)


def ornament_svg(name):
    r = _rng(_fnv('oyu:' + (name or '')))
    bg, fg, acc = _PALETTES[int(r() * len(_PALETTES))]
    sw = _f(5 + r() * 2.5)
    mode = ('corner', 'axis', 'both')[int(r() * 3)]
    thin = _f(float(sw) * 0.75) if mode == 'both' else sw
    q = ''
    if mode != 'axis':
        q += '<path d="%s" stroke-width="%s"/>' % (_CORNER, thin)
    if mode != 'corner':
        q += '<path d="%s" stroke-width="%s"/>' % (_AXIS, thin)
    g = ''.join('<g transform="rotate(%d 50 50)">%s</g>' % (a, q) for a in (0, 90, 180, 270))
    d = _f(7 + r() * 5)
    s = '<rect width="100" height="100" fill="%s"/>' % bg
    if r() < 0.6:
        s += '<rect x="4" y="4" width="92" height="92" fill="none" stroke="%s" stroke-width="3"/>' % acc
    s += '<g fill="none" stroke="%s" stroke-linecap="round" stroke-linejoin="round">%s</g>' % (fg, g)
    dv = float(d)
    s += '<path d="M50 %sL%s 50L50 %sL%s 50Z" fill="%s" stroke="%s" stroke-width="2"/>' % (
        _f(50 - dv), _f(50 + dv), _f(50 + dv), _f(50 - dv), acc, fg)
    if r() < 0.5:
        for x, y in ((12, 12), (88, 12), (12, 88), (88, 88)):
            s += '<circle cx="%d" cy="%d" r="3" fill="%s"/>' % (x, y, fg)
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">%s</svg>' % s
