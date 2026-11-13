import random, sys
R = random.Random()
NAMES = ["Айбек","Нурлан","Эрлан","Азамат","Данияр","Бекзат","Тилек","Манас","Улан","Асан","Кубат","Мирлан","Айгерим","Айжан","Мээрим","Айдай","Нургуль","Жамиля","Салтанат","Бермет"]
PLACES = ["Ош","Бишкек","Нарын","Каракол","Талас","Токтогул","Баткен","Джалал-Абад","Кант","Токмок","Кара-Суу","Узген"]
def sz(L, hi, lo=1):
    if L == 0:
        return R.randint(lo, max(lo, min(hi, 6)))
    if L >= 10:
        return hi
    return max(lo, min(hi, int(hi ** (0.45 + 0.055 * L))))
def vl(L, hi):
    if L == 0:
        return min(hi, 8)
    if L < 4:
        return min(hi, 10 * 10 ** L)
    return hi
def arr(n, lo, hi):
    return [R.randint(lo, hi) for _ in range(n)]
def line(a):
    return ' '.join(map(str, a))
def st(n, alpha):
    return ''.join(R.choice(alpha) for _ in range(n))

def gen(L):
    n = sz(L, 100000); v = vl(L, 10**4)
    g = arr(n, 0, v); c = arr(n, 0, v)
    if R.random() < 0.7:
        for i in range(n): g[i] = c[i] + R.randint(-v//10 - 1, v//10 + 1)
        g = [max(0, x) for x in g]; 
        if R.random() < 0.7: g[R.randrange(n)] += sum(max(0, c[i]-g[i]) for i in range(n)) + 1
    return f"{n}\n{line(g)}\n{line(c)}\n"

if __name__ == "__main__":
    R.seed(int(sys.argv[1]))
    sys.stdout.write(gen(int(sys.argv[2])))
