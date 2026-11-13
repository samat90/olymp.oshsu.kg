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
    n = sz(L, 1000); m = sz(L, 1000); q = sz(L, 100000); v = n*m*3
    p = sorted(R.sample(range(1, v+1), n*m))
    rows = [line(p[i*m:(i+1)*m]) for i in range(n)]
    return f"{n} {m}\n" + '\n'.join(rows) + f"\n{q}\n{line(arr(q, 1, v))}\n"

if __name__ == "__main__":
    R.seed(int(sys.argv[1]))
    sys.stdout.write(gen(int(sys.argv[2])))
