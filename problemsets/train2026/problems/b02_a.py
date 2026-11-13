import bisect
from collections import Counter
from itertools import product
from lib import prob, size, nums, ints


def vals(r, n, lo, hi):
    return [r.randint(lo, hi) for _ in range(n)]


def hi_of(lv, n, small=5):
    return small if lv < 3 else max(small, n // 2)


def pairs(c):
    return c * (c - 1) // 2


@prob('b02_a_two_sum_idx', 'Два подарка на сумму', 'training', ['Массивы', 'Структуры данных'], 12,
      r"Бакыт хочет купить в Оше два подарка на ровно $t$ сомов. Цены подарков в ряду лавок равны $a_1,\dots,a_n$. Найдите пару $i<j$ с $a_i+a_j=t$ с наименьшим $i$, а при равных $i$ — с наименьшим $j$.",
      r"В первой строке $n$ и $t$ ($2 \le n \le 2\cdot10^5$, $|t| \le 2\cdot10^9$). Во второй — $n$ целых чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Два числа $i$ и $j$ или $-1$, если такой пары нет.", ['5 9\n2 7 11 4 5\n', '3 100\n1 2 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); h = hi_of(lv, n)
        a = vals(r, n, -h, h)
        if r.random() < 0.7:
            i, j = r.sample(range(n), 2); t = a[i] + a[j]
        else:
            t = r.randint(-2 * h, 2 * h) + (7 * h if lv % 2 else 0)
        return '%d %d\n%s\n' % (n, t, nums(a))

    def solve(d):
        x = ints(d); n, t = x[0], x[1]; a = x[2:2 + n]; pos = {}
        for i, v in enumerate(a): pos.setdefault(v, []).append(i)
        for i in range(n):
            l = pos.get(t - a[i])
            if l:
                k = bisect.bisect_right(l, i)
                if k < len(l): return '%d %d' % (i + 1, l[k] + 1)
        return '-1'

    def brute(d):
        x = ints(d); n, t = x[0], x[1]; a = x[2:2 + n]
        for i in range(n):
            for j in range(i + 1, n):
                if a[i] + a[j] == t: return '%d %d' % (i + 1, j + 1)
        return '-1'


@prob('b02_a_count_sum_pairs', 'Пары вёдер у родника', 'training', ['Массивы', 'Структуры данных'], 15,
      r"У родника в Нарыне стоят $n$ вёдер, в $i$-м налито $a_i$ литров. Айгуль хочет сливать воду из двух вёдер в бочку на $s$ литров. Сколько существует пар вёдер $i<j$ с $a_i+a_j=s$?",
      r"В первой строке $n$ и $s$ ($1 \le n \le 2\cdot10^5$, $0 \le s \le 2\cdot10^9$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Количество пар.", ['5 6\n1 5 3 3 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); h = hi_of(lv, n, 4)
        a = vals(r, n, 0, h)
        return '%d %d\n%s\n' % (n, r.randint(0, 2 * h), nums(a))

    def solve(d):
        x = ints(d); n, s = x[0], x[1]; c = Counter(); res = 0
        for v in x[2:2 + n]:
            res += c[s - v]; c[v] += 1
        return str(res)

    def brute(d):
        x = ints(d); n, s = x[0], x[1]; a = x[2:2 + n]
        return str(sum(1 for i in range(n) for j in range(i + 1, n) if a[i] + a[j] == s))


@prob('b02_a_diff_pairs', 'Лошади с разницей в возрасте', 'training', ['Массивы', 'Структуры данных'], 18,
      r"В табуне Чолпон-Аты $n$ лошадей, возраст $i$-й равен $a_i$ месяцам. Нурлан ищет пары лошадей $i<j$, возраст которых отличается ровно на $k$ месяцев. Сколько таких пар?",
      r"В первой строке $n$ и $k$ ($1 \le n \le 2\cdot10^5$, $1 \le k \le 10^9$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Количество пар.", ['5 2\n1 3 1 5 4\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); h = hi_of(lv, n)
        return '%d %d\n%s\n' % (n, r.randint(1, 3 + lv), nums(vals(r, n, 0, h)))

    def solve(d):
        x = ints(d); n, k = x[0], x[1]; c = Counter(x[2:2 + n])
        return str(sum(v * c.get(u + k, 0) for u, v in c.items()))

    def brute(d):
        x = ints(d); n, k = x[0], x[1]; a = x[2:2 + n]
        return str(sum(1 for i in range(n) for j in range(i + 1, n) if abs(a[i] - a[j]) == k))


@prob('b02_a_distinct_sum_pairs', 'Разные цены в паре', 'training', ['Массивы', 'Структуры данных'], 20,
      r"На базаре в Караколе выставлены товары с ценами $a_1,\dots,a_n$. Сколько существует различных пар цен $\{x,y\}$ (порядок не важен), для которых есть два разных товара с ценами $x$ и $y$ и $x+y=t$? Пары с одинаковыми значениями считаются одной.",
      r"В первой строке $n$ и $t$ ($1 \le n \le 2\cdot10^5$, $0 \le t \le 2\cdot10^9$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Количество различных пар.", ['6 8\n4 4 3 5 5 1\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); h = hi_of(lv, n, 6)
        return '%d %d\n%s\n' % (n, r.randint(0, 2 * h), nums(vals(r, n, 0, h)))

    def solve(d):
        x = ints(d); n, t = x[0], x[1]; c = Counter(x[2:2 + n]); res = 0
        for u in c:
            w = t - u
            if u < w and w in c: res += 1
            elif u == w and c[u] > 1: res += 1
        return str(res)

    def brute(d):
        x = ints(d); n, t = x[0], x[1]; a = x[2:2 + n]; s = set()
        for i in range(n):
            for j in range(i + 1, n):
                if a[i] + a[j] == t: s.add((min(a[i], a[j]), max(a[i], a[j])))
        return str(len(s))


@prob('b02_a_longest_run', 'Подряд идущие номера бегунов', 'training', ['Массивы', 'Структуры данных'], 25,
      r"На забеге в Оше у $n$ бегунов номера $a_1,\dots,a_n$ (могут повторяться). Бакыт хочет выбрать как можно больше разных номеров так, чтобы они шли подряд: $x, x+1, \dots, x+m-1$. Чему равно наибольшее $m$?",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Число $m$.", ['6\n100 4 200 1 3 2\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); h = hi_of(lv, n, 6)
        a = vals(r, n, -h, h)
        if lv > 5: a = [v * 3 if r.random() < 0.3 else v for v in a]
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        x = ints(d); s = set(x[1:1 + x[0]]); best = 0
        for v in s:
            if v - 1 not in s:
                m = 1
                while v + m in s: m += 1
                best = max(best, m)
        return str(best)

    def brute(d):
        x = ints(d); s = sorted(set(x[1:1 + x[0]])); best = cur = 1
        for i in range(1, len(s)):
            cur = cur + 1 if s[i] == s[i - 1] + 1 else 1
            best = max(best, cur)
        return str(best)


@prob('b02_a_first_unique', 'Первый одиночка', 'training', ['Массивы', 'Структуры данных'], 10,
      r"Участники нарынского фестиваля выходят на сцену по очереди, у $i$-го номер команды $a_i$. Найдите позицию первого участника, чья команда выходит ровно один раз.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Позиция (с 1) или $-1$.", ['6\n3 3 2 5 2 7\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000)
        return '%d\n%s\n' % (n, nums(vals(r, n, 1, max(2, n // 2 if lv > 2 else 3))))

    def solve(d):
        x = ints(d); a = x[1:1 + x[0]]; c = Counter(a)
        for i, v in enumerate(a):
            if c[v] == 1: return str(i + 1)
        return '-1'

    def brute(d):
        x = ints(d); a = x[1:1 + x[0]]
        for i, v in enumerate(a):
            if a.count(v) == 1: return str(i + 1)
        return '-1'


@prob('b02_a_top_voice', 'Самый частый крик', 'training', ['Массивы', 'Структуры данных'], 10,
      r"Судья в Ак-Суу записал $n$ номеров болельщиков, выкрикнувших приветствие. Какой номер встречается чаще всех и сколько раз? Если таких несколько, выведите наименьший.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Два числа: номер и число его появлений.", ['7\n4 2 4 2 9 2 4\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000)
        return '%d\n%s\n' % (n, nums(vals(r, n, 1, 3 if lv < 3 else max(3, n // 3))))

    def solve(d):
        x = ints(d); c = Counter(x[1:1 + x[0]])
        m = max(c.values()); return '%d %d' % (min(k for k in c if c[k] == m), m)

    def brute(d):
        x = ints(d); a = x[1:1 + x[0]]; best = None
        for v in sorted(set(a)):
            if best is None or a.count(v) > best[1]: best = (v, a.count(v))
        return '%d %d' % best


@prob('b02_a_anagram_groups', 'Анаграммы в песне', 'training', ['Строки', 'Сортировка', 'Структуры данных'], 22,
      r"Манасчи записал $n$ слов. Два слова называются родственными, если из букв одного можно получить другое перестановкой. Слова делятся на группы родственных. Сколько получилось групп и каков размер самой большой?",
      r"В первой строке $n$ ($1 \le n \le 5\cdot10^4$). Далее $n$ слов из строчных латинских букв, суммарная длина не более $2\cdot10^5$.",
      r"Два числа: число групп и наибольший размер группы.", ['5\nabc bca cab xyz zyx\n'])
class _:
    def gen(r, lv):
        n = size(lv, 50000); al = 'abc' if lv < 5 else 'abcd'
        return '%d\n%s\n' % (n, ' '.join(''.join(r.choice(al) for _ in range(r.randint(1, 4))) for _ in range(n)))

    def solve(d):
        w = d.split()[1:]; c = Counter(''.join(sorted(s)) for s in w)
        return '%d %d' % (len(c), max(c.values()))

    def brute(d):
        w = d.split()[1:]; groups = []
        for s in w:
            for g in groups:
                if sorted(g[0]) == sorted(s): g.append(s); break
            else: groups.append([s])
        return '%d %d' % (len(groups), max(map(len, groups)))


@prob('b02_a_missing_numbers', 'Пропавшие участники', 'training', ['Массивы', 'Структуры данных'], 12,
      r"В Оше на турнир зарегистрировалось $n$ человек с номерами от 1 до $n$. В списке пришедших $n$ записей, но номера могут повторяться. Выведите номера, которых в списке нет.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le n$).",
      r"В первой строке количество $k$ пропавших, во второй — их номера по возрастанию.", ['6\n1 1 3 3 6 6\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000)
        return '%d\n%s\n' % (n, nums(vals(r, n, 1, n if lv % 2 else max(1, n * 3 // 4))))

    def solve(d):
        x = ints(d); n = x[0]; s = set(x[1:1 + n]); m = [v for v in range(1, n + 1) if v not in s]
        return '%d\n%s' % (len(m), nums(m))

    def brute(d):
        x = ints(d); n = x[0]; a = x[1:1 + n]; m = [v for v in range(1, n + 1) if v not in a]
        return '%d\n%s' % (len(m), nums(m))


@prob('b02_a_near_twins', 'Близнецы в очереди', 'training', ['Массивы', 'Структуры данных'], 14,
      r"В очереди за лепёшками в Таласе стоят $n$ человек, у $i$-го возраст $a_i$. Найдите две ближайшие позиции с равным возрастом: наименьшее $j-i$ при $i<j$ и $a_i=a_j$.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Наименьшее расстояние или $-1$.", ['6\n5 1 5 2 1 9\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000)
        return '%d\n%s\n' % (n, nums(vals(r, n, 1, n * 2 if lv % 3 == 0 and lv > 2 else max(3, n // 2))))

    def solve(d):
        x = ints(d); last = {}; best = -1
        for i, v in enumerate(x[1:1 + x[0]]):
            if v in last and (best < 0 or i - last[v] < best): best = i - last[v]
            last[v] = i
        return str(best)

    def brute(d):
        x = ints(d); a = x[1:1 + x[0]]; best = -1
        for i in range(len(a)):
            for j in range(i + 1, len(a)):
                if a[i] == a[j] and (best < 0 or j - i < best): best = j - i
        return str(best)


@prob('b02_a_alt_parity', 'Чередование удоев', 'training', ['Массивы'], 20,
      r"Доярка Айзада записывает удой $a_i$ литров за каждый из $n$ дней. Найдите длину самого длинного отрезка подряд идущих дней, в котором чётные и нечётные удои строго чередуются (соседние числа имеют разную чётность).",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ целых чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Одно число — наибольшую длину.", ['6\n2 3 4 4 5 6\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000)
        hi = 9 if lv < 3 else 10 ** 9
        pc = r.choice([0.1, 0.5, 0.9])
        a = []; par = r.randint(0, 1)
        for _ in range(n):
            par = par ^ 1 if r.random() > pc / 5 else par
            a.append(r.randint(0, hi // 2) * 2 + par if hi > 9 else r.randint(0, 4) * 2 + par)
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        x = ints(d); n = x[0]; a = x[1:1 + n]; best = cur = 1
        for i in range(1, n):
            cur = cur + 1 if (a[i] - a[i - 1]) % 2 else 1
            best = max(best, cur)
        return str(best)

    def brute(d):
        x = ints(d); n = x[0]; a = x[1:1 + n]; best = 1
        for i in range(n):
            for j in range(i, n):
                if all((a[k] + a[k + 1]) % 2 for k in range(i, j)):
                    best = max(best, j - i + 1)
        return str(best)


@prob('b02_a_zero_balance', 'Нулевой баланс лавки', 'training', ['Массивы', 'Структуры данных'], 28,
      r"Лавка в Чолпон-Ате за каждый день фиксирует прибыль или убыток $a_i$ сомов. Какова наибольшая длина отрезка подряд идущих дней с нулевым суммарным результатом? Если такого нет, выведите 0.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Наибольшая длина.", ['6\n3 -1 -2 4 -4 5\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000)
        return '%d\n%s\n' % (n, nums(vals(r, n, -4, 4)))

    def solve(d):
        x = ints(d); first = {0: 0}; s = best = 0
        for i, v in enumerate(x[1:1 + x[0]], 1):
            s += v
            if s in first: best = max(best, i - first[s])
            else: first[s] = i
        return str(best)

    def brute(d):
        x = ints(d); a = x[1:1 + x[0]]; best = 0
        for i in range(len(a)):
            s = 0
            for j in range(i, len(a)):
                s += a[j]
                if s == 0: best = max(best, j - i + 1)
        return str(best)


@prob('b02_a_div_subarrays', 'Кратные отрезки пути', 'training', ['Математика', 'Массивы', 'Структуры данных'], 35,
      r"Караван идёт по трассе Бишкек — Ош, и за $i$-й день проходит $a_i$ километров. Сколько существует отрезков подряд идущих дней, суммарный путь за которые кратен $m$?",
      r"В первой строке $n$ и $m$ ($1 \le n \le 2\cdot10^5$, $1 \le m \le 10^9$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Количество отрезков.", ['5 3\n1 2 3 4 5\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); m = r.choice([1, 2, 3, 5, 7, 10, 997, 10 ** 9])
        return '%d %d\n%s\n' % (n, m, nums(vals(r, n, 0, 10 ** 9 if lv > 4 else 20)))

    def solve(d):
        x = ints(d); n, m = x[0], x[1]; c = Counter({0: 1}); s = res = 0
        for v in x[2:2 + n]:
            s = (s + v) % m; res += c[s]; c[s] += 1
        return str(res)

    def brute(d):
        x = ints(d); n, m = x[0], x[1]; a = x[2:2 + n]; res = 0
        for i in range(n):
            s = 0
            for j in range(i, n):
                s += a[j]; res += s % m == 0
        return str(res)


@prob('b02_a_window_distinct', 'Разные породы в окне', 'training', ['Массивы', 'Структуры данных'], 24,
      r"Вдоль дороги в Нарыне пасутся $n$ коров, у $i$-й порода с номером $a_i$. Айгуль смотрит в окно автобуса и видит подряд $k$ коров. Для каждой позиции окна, слева направо, выведите число разных пород в нём.",
      r"В первой строке $n$ и $k$ ($1 \le k \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"$n-k+1$ чисел через пробел.", ['6 3\n1 2 1 3 3 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000)
        return '%d %d\n%s\n' % (n, r.randint(1, n), nums(vals(r, n, 1, 3 if lv < 3 else max(3, n // 4))))

    def solve(d):
        x = ints(d); n, k = x[0], x[1]; a = x[2:2 + n]; c = {}; res = []
        for i in range(n):
            c[a[i]] = c.get(a[i], 0) + 1
            if i >= k:
                o = a[i - k]; c[o] -= 1
                if not c[o]: del c[o]
            if i >= k - 1: res.append(len(c))
        return nums(res)

    def brute(d):
        x = ints(d); n, k = x[0], x[1]; a = x[2:2 + n]
        return nums([len(set(a[i:i + k])) for i in range(n - k + 1)])


@prob('b02_a_same_shape_words', 'Слова одного узора', 'training', ['Строки', 'Структуры данных'], 32,
      r"Два слова называются однотипными, если их длины равны и буквы первого можно взаимно однозначно заменить буквами второго (одинаковые на одинаковые, разные на разные). Например, abab и cdcd однотипны, а abab и abcb — нет. Сколько пар слов $i<j$ из списка однотипны?",
      r"В первой строке $n$ ($1 \le n \le 4\cdot10^4$). Далее $n$ слов из строчных латинских букв, длина каждого не более 5.",
      r"Количество пар.", ['4\nabab cdcd abca xyzx\n'])
class _:
    def gen(r, lv):
        n = size(lv, 40000); al = 'abc' if lv < 5 else 'abcdef'
        return '%d\n%s\n' % (n, ' '.join(''.join(r.choice(al) for _ in range(r.randint(1, 5))) for _ in range(n)))

    def solve(d):
        c = Counter()
        for s in d.split()[1:]:
            m = {}; c[tuple(m.setdefault(ch, len(m)) for ch in s)] += 1
        return str(sum(pairs(v) for v in c.values()))

    def brute(d):
        w = d.split()[1:]; res = 0
        for i in range(len(w)):
            for j in range(i + 1, len(w)):
                a, b = w[i], w[j]
                if len(a) == len(b) and len(set(a)) == len(set(b)) == len(set(zip(a, b))): res += 1
        return str(res)


@prob('b02_a_exact_k_kinds', 'Ровно k видов трав', 'training', ['Массивы', 'Структуры данных'], 50,
      r"Вдоль тропы к Сон-Кулю растут травы, на $i$-м участке — трава вида $a_i$. Скольким отрезкам подряд идущих участков соответствует ровно $k$ различных видов трав?",
      r"В первой строке $n$ и $k$ ($1 \le k \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Количество отрезков.", ['5 2\n1 2 1 2 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); h = 3 if lv < 3 else r.randint(3, 8)
        return '%d %d\n%s\n' % (n, r.randint(1, min(n, h)), nums(vals(r, n, 1, h)))

    def solve(d):
        x = ints(d); n, k = x[0], x[1]; a = x[2:2 + n]

        def atmost(k):
            if k <= 0: return 0
            c = {}; l = res = 0
            for i, v in enumerate(a):
                c[v] = c.get(v, 0) + 1
                while len(c) > k:
                    c[a[l]] -= 1
                    if not c[a[l]]: del c[a[l]]
                    l += 1
                res += i - l + 1
            return res
        return str(atmost(k) - atmost(k - 1))

    def brute(d):
        x = ints(d); n, k = x[0], x[1]; a = x[2:2 + n]
        return str(sum(1 for i in range(n) for j in range(i, n) if len(set(a[i:j + 1])) == k))


@prob('b02_a_third_voters', 'Больше трети голосов', 'training', ['Массивы', 'Структуры данных'], 20,
      r"В айыл окмоту голосовали за кандидатов с номерами $a_1,\dots,a_n$ (по одному голосу в записи). Выведите по возрастанию номера кандидатов, получивших строго больше трети всех голосов.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Номера через пробел или $-1$, если таких нет.", ['7\n5 3 5 3 8 5 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); a = vals(r, n, 1, 4 if lv < 5 else n)
        if lv % 2:
            for _ in range(n // 2): a[r.randrange(n)] = r.choice([7, 9])
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        x = ints(d); n = x[0]; c = Counter(x[1:1 + n])
        res = sorted(v for v in c if c[v] * 3 > n)
        return nums(res) if res else '-1'

    def brute(d):
        x = ints(d); n = x[0]; a = x[1:1 + n]
        res = [v for v in sorted(set(a)) if a.count(v) * 3 > n]
        return nums(res) if res else '-1'


@prob('b02_a_four_zero', 'Четыре мешка в ноль', 'training', ['Массивы', 'Структуры данных'], 45,
      r"На четырёх складах в Оше лежат по $n$ мешков, веса записаны в четырёх списках $A,B,C,D$ (вес может быть отрицательным — это поправка). Сколько существует четвёрок индексов $(i,j,k,l)$, для которых $A_i+B_j+C_k+D_l=0$?",
      r"В первой строке $n$ ($1 \le n \le 1000$). Следующие 4 строки — списки $A,B,C,D$ по $n$ чисел, $|\cdot| \le 10^9$.",
      r"Количество четвёрок.", ['2\n1 2\n-2 -1\n-1 2\n0 2\n'])
class _:
    def gen(r, lv):
        n = size(lv, 1000); h = 4 if lv < 5 else 40
        return '%d\n%s\n' % (n, '\n'.join(nums(vals(r, n, -h, h)) for _ in range(4)))

    def solve(d):
        x = ints(d); n = x[0]; A, B, C, D = (Counter(x[1 + n * q:1 + n * (q + 1)]) for q in range(4))
        ab = Counter()
        for u, p in A.items():
            for v, q in B.items(): ab[u + v] += p * q
        res = 0
        for u, p in C.items():
            for v, q in D.items(): res += p * q * ab.get(-u - v, 0)
        return str(res)

    def brute(d):
        x = ints(d); n = x[0]; L = [x[1 + n * q:1 + n * (q + 1)] for q in range(4)]
        return str(sum(1 for t in product(*L) if sum(t) == 0))


@prob('b02_a_shifted_equal', 'Ровные ступени', 'training', ['Массивы', 'Структуры данных', 'Математика'], 26,
      r"На склоне у Ала-Арчи $n$ ступеней, высота $i$-й равна $a_i$. Пара ступеней $i<j$ называется ровной, если подъём от $i$ до $j$ равен числу пройденных шагов: $a_j-a_i=j-i$. Сколько ровных пар?",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Количество пар.", ['5\n1 2 5 4 5\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); a = [i + r.randint(0, 3 if lv < 6 else 40) + 5 for i in range(n)]
        for i in range(n):
            if r.random() < 0.2: a[i] = r.randint(-n, 2 * n)
        return '%d\n%s\n' % (n, nums(a))

    def solve(d):
        x = ints(d); c = Counter(v - i for i, v in enumerate(x[1:1 + x[0]]))
        return str(sum(pairs(v) for v in c.values()))

    def brute(d):
        x = ints(d); a = x[1:1 + x[0]]
        return str(sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[j] - a[i] == j - i))


@prob('b02_a_palin_substrings', 'Напевы-перевёртыши', 'training', ['Строки', 'Структуры данных', 'Математика'], 58,
      r"Манасчи записал напев строкой из букв $a$–$j$. Назовём подстроку удачной, если её буквы можно переставить так, чтобы получился палиндром. Сколько в записи удачных подстрок (подстроки с разными позициями считаются разными)?",
      r"Одна строка длиной $n$ ($1 \le n \le 10^5$) из букв от $a$ до $j$.",
      r"Количество удачных подстрок.", ['aab\n'])
class _:
    def gen(r, lv):
        n = size(lv, 100000); al = 'abcdefghij'[:min(10, 2 + lv)]
        return ''.join(r.choice(al) for _ in range(n)) + '\n'

    def solve(d):
        s = d.split()[0]; c = Counter({0: 1}); m = res = 0
        for ch in s:
            m ^= 1 << (ord(ch) - 97)
            res += c[m]
            for b in range(10): res += c.get(m ^ (1 << b), 0)
            c[m] += 1
        return str(res)

    def brute(d):
        s = d.split()[0]; res = 0
        for i in range(len(s)):
            for j in range(i + 1, len(s) + 1):
                res += sum(v % 2 for v in Counter(s[i:j]).values()) <= 1
        return str(res)


@prob('b02_a_no_repeat_str', 'Лента без повторов', 'training', ['Строки', 'Структуры данных'], 16,
      r"Айгуль плетёт ленту из цветных нитей, цвет каждой нити — буква. Нужно вырезать кусок подряд идущих нитей, где все цвета различны. Какова наибольшая длина такого куска?",
      r"Одна строка из строчных латинских букв длиной $n$ ($1 \le n \le 2\cdot10^5$).",
      r"Наибольшая длина.", ['abcabcbb\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); k = min(26, 2 + lv * 3)
        return ''.join(chr(97 + r.randrange(k)) for _ in range(n)) + '\n'

    def solve(d):
        s = d.split()[0]; last = {}; l = best = 0
        for i, ch in enumerate(s):
            if ch in last and last[ch] >= l: l = last[ch] + 1
            last[ch] = i; best = max(best, i - l + 1)
        return str(best)

    def brute(d):
        s = d.split()[0]; best = 0
        for i in range(len(s)):
            for j in range(i + 1, len(s) + 1):
                if len(set(s[i:j])) == j - i: best = max(best, j - i)
        return str(best)


@prob('b02_a_unique_counts', 'Разные частоты', 'training', ['Жадные', 'Массивы', 'Структуры данных'], 40,
      r"На ярмарке в Караколе $n$ банок с мёдом, у $i$-й банки номер сорта $a_i$. Организатор хочет, чтобы число банок каждого присутствующего сорта было различным (сорта, которых не осталось, не учитываются). Какое наименьшее число банок придётся убрать?",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"Наименьшее число убранных банок.", ['6\n1 1 2 2 3 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); h = 3 if lv < 3 else max(3, int(n ** 0.5))
        return '%d\n%s\n' % (n, nums([min(r.randint(1, h), r.randint(1, h)) for _ in range(n)]))

    def solve(d):
        x = ints(d); fs = sorted(Counter(x[1:1 + x[0]]).values(), reverse=True); prev = 10 ** 9; res = 0
        for f in fs:
            nf = min(f, prev - 1)
            if nf <= 0: res += f; prev = 0
            else: res += f - nf; prev = nf
        return str(res)

    def brute(d):
        x = ints(d); fs = list(Counter(x[1:1 + x[0]]).values()); best = sum(fs)
        for ch in product(*[range(f + 1) for f in fs]):
            k = [c for c in ch if c]
            if len(set(k)) == len(k): best = min(best, sum(fs) - sum(k))
        return str(best)


@prob('b02_a_sort_by_freq', 'Порядок по популярности', 'training', ['Сортировка', 'Массивы', 'Структуры данных'], 18,
      r"Чайхана в Оше записала номера $n$ заказанных блюд. Перепишите список так, чтобы сначала шли блюда, заказанные чаще, а при равной частоте — с меньшим номером. Одинаковые номера идут подряд.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($1 \le a_i \le 10^9$).",
      r"$n$ чисел через пробел.", ['6\n4 5 6 5 4 5\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000)
        return '%d\n%s\n' % (n, nums(vals(r, n, 1, 4 if lv < 3 else max(4, n // 5))))

    def solve(d):
        x = ints(d); c = Counter(x[1:1 + x[0]]); res = []
        for v in sorted(c, key=lambda v: (-c[v], v)): res += [v] * c[v]
        return nums(res)

    def brute(d):
        x = ints(d); a = x[1:1 + x[0]]
        return nums(sorted(a, key=lambda v: (-a.count(v), v)))


@prob('b02_a_div_pairs', 'Пары с кратной суммой', 'training', ['Математика', 'Массивы', 'Структуры данных'], 27,
      r"Бакыт выбирает пары коробок с орехами: в $i$-й коробке $a_i$ орехов, и две коробки $i<j$ подходят, если сумма орехов $a_i+a_j$ делится на $m$. Сколько существует подходящих пар?",
      r"В первой строке $n$ и $m$ ($1 \le n \le 2\cdot10^5$, $1 \le m \le 10^9$). Во второй — $n$ чисел $a_i$ ($0 \le a_i \le 10^9$).",
      r"Количество пар.", ['5 4\n1 3 2 2 6\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); m = r.choice([1, 2, 4, 6, 10, 13, 1000, 10 ** 9])
        return '%d %d\n%s\n' % (n, m, nums(vals(r, n, 0, 30 if lv < 5 else 10 ** 9)))

    def solve(d):
        x = ints(d); n, m = x[0], x[1]; c = Counter(v % m for v in x[2:2 + n]); res = 0
        for u, p in c.items():
            w = (-u) % m
            if u < w: res += p * c.get(w, 0)
            elif u == w: res += pairs(p)
        return str(res)

    def brute(d):
        x = ints(d); n, m = x[0], x[1]; a = x[2:2 + n]
        return str(sum(1 for i in range(n) for j in range(i + 1, n) if (a[i] + a[j]) % m == 0))


@prob('b02_a_neighbor_set', 'Дружная связка товаров', 'training', ['Массивы', 'Структуры данных'], 17,
      r"На базаре в Нарыне у $n$ товаров целые коды $a_i$. Связка — набор товаров (подпоследовательность), где наибольший код ровно на 1 больше наименьшего. Какова наибольшая возможная связка? Если связок нет, выведите 0.",
      r"В первой строке $n$ ($1 \le n \le 2\cdot10^5$). Во второй — $n$ чисел $a_i$ ($|a_i| \le 10^9$).",
      r"Наибольший размер связки.", ['7\n1 3 2 2 5 2 3\n'])
class _:
    def gen(r, lv):
        n = size(lv, 200000); h = hi_of(lv, n, 5)
        return '%d\n%s\n' % (n, nums(vals(r, n, -h, h * (1 if lv < 7 else 3))))

    def solve(d):
        x = ints(d); c = Counter(x[1:1 + x[0]])
        return str(max([p + c[u + 1] for u, p in c.items() if u + 1 in c] or [0]))

    def brute(d):
        x = ints(d); a = x[1:1 + x[0]]
        return str(max([a.count(v) + a.count(v + 1) for v in set(a) if v + 1 in a] or [0]))
