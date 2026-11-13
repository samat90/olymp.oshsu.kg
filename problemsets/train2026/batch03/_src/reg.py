TASKS = []
LIN = [3, 8, 15, 100, 1000, 10000, 50000, 100000, 200000, 200000]
MID = [3, 8, 15, 100, 1000, 5000, 20000, 50000, 100000, 100000]
QUAD = [3, 8, 15, 50, 100, 300, 500, 800, 1000, 1000]
SMALLQ = [3, 8, 15, 30, 60, 150, 300, 500, 800, 1000]

def task(slug, title, stmt, samples, sizes=LIN, tl=1.0, diff=40):
    def deco(f):
        TASKS.append(dict(slug=slug, title=title, stmt=stmt.strip('\n'), samples=samples,
                          sizes=sizes, tl=tl, diff=diff, fn=f))
        return f
    return deco
