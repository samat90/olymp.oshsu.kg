"""Helpers for problem modules."""


def P(slug, name, group, types, diff, text, samples, gen, solve, brute, time=1):
    assert group in ('training', 'olympiad')
    return dict(slug=slug, name=name, group=group, types=types, diff=diff, text=text.strip() + '\n{{samples}}',
                samples=samples, gen=gen, solve=solve, brute=brute, time=time)


def size(level, big, small=8):
    big = min(big, 100000)
    """Levels 0-2 are tiny (brute force checks them), then geometric growth up to `big`."""
    if level < 3:
        return [2, 4, small][level]
    lo = max(small + 1, 10)
    return int(lo * (big / lo) ** ((level - 3) / 6))


def lines(*rows):
    return ''.join(rows)


def nums(a):
    return ' '.join(map(str, a))


REG = []


def ints(d):
    return list(map(int, d.split()))


def prob(slug, name, group, types, diff, story, inp, out, samples, time=1):
    """Decorator for a class with static gen(r, level), solve(data), brute(data)."""
    def deco(c):
        nn = chr(10) * 2
        text = nn.join(['# ' + name, story.strip(), '## Формат ввода', inp.strip(), '## Формат вывода', out.strip()]) + chr(10)
        REG.append(P(slug, name, group, types, diff, text, samples, c.gen, c.solve, c.brute, time))
        return c
    return deco
