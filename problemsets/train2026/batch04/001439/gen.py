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
    n = sz(L, 200000); v = vl(L, 10**9)
    a = sorted(arr(n, 1, v))
    for _ in range(R.choice([0, 1, 2, 3, n // 3 + 1]) if L else R.randint(0, 3)):
        i = R.randrange(n); j = R.randrange(n); a[i], a[j] = a[j], a[i]
    return f"{n}\n{line(a)}\n"

if __name__ == "__main__":
    R.seed(int(sys.argv[1]))
    sys.stdout.write(gen(int(sys.argv[2])))
