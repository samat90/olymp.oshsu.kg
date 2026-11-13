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
    n = sz(L, 200000); k = R.randint(1, min(n, 4 if L == 0 else n)); v = vl(L, 10**9)
    if R.random() < 0.5 and k <= n:
        m = max(1, n//k); base = R.randint(1, max(2, v//2 if L else 6)); a = []
        for _ in range(m):
            s0 = base + R.randint(0, 3); a += list(range(s0, s0+k))
        a += arr(n-len(a), 1, max(2, v)) if len(a) < n else []
        a = a[:n]; R.shuffle(a)
    else: a = arr(n, 1, v if L > 3 else 6)
    return f"{len(a)} {k}\n{line(a)}\n"

if __name__ == "__main__":
    R.seed(int(sys.argv[1]))
    sys.stdout.write(gen(int(sys.argv[2])))
