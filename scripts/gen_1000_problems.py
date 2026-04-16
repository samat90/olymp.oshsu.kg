"""
Generate 1000 programming problems with test cases for OshSU Olymp.
Categories: math, strings, arrays, sorting, number theory, geometry,
            greedy, DP, implementation, combinatorics.

Usage:
    cd d:/projects/olymp.oshsu.kg
    set DJANGO_SETTINGS_MODULE=dmoj.settings
    venv/Scripts/python.exe scripts/gen_1000_problems.py

Each problem gets:
- Russian description (Markdown)
- 5-10 test cases (input/output files + init.yml)
- Difficulty 1-5 points
- Time/memory limits
- Assigned to problem types
"""

import os, sys, json, math, random, shutil
from pathlib import Path
from itertools import combinations

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import django
django.setup()

from django.utils import timezone
from judge.models import Problem, ProblemType, ProblemGroup, Language, Profile

PROBLEMS_DIR = BASE_DIR / 'problems'
author = Profile.objects.get(user__username='samat1')

# Get or create problem types
def get_type(name):
    t, _ = ProblemType.objects.get_or_create(name=name)
    return t

def get_group(name):
    g, _ = ProblemGroup.objects.get_or_create(name=name)
    return g

types = {
    'math': get_type('Математика'),
    'strings': get_type('Строки'),
    'arrays': get_type('Массивы'),
    'sorting': get_type('Сортировка'),
    'numtheory': get_type('Теория чисел'),
    'geometry': get_type('Геометрия'),
    'greedy': get_type('Жадные алгоритмы'),
    'dp': get_type('Динамическое программирование'),
    'impl': get_type('Реализация'),
    'combinatorics': get_type('Комбинаторика'),
    'graphs': get_type('Графы'),
    'binary': get_type('Двоичный поиск'),
}

group_general = get_group('Общие задачи')
allowed_langs = list(Language.objects.filter(key__in=['PY3', 'CPP17', 'JAVA8', 'C']))

# ---------- HELPER ----------
def write_test(prob_dir, idx, inp, out):
    with open(prob_dir / f'{idx}.in', 'w') as f:
        f.write(str(inp).strip() + '\n')
    with open(prob_dir / f'{idx}.out', 'w') as f:
        f.write(str(out).strip() + '\n')

def write_init(prob_dir, n_tests):
    init = {'test_cases': []}
    for i in range(1, n_tests + 1):
        init['test_cases'].append({
            'in': f'{i}.in',
            'out': f'{i}.out',
            'points': round(100 / n_tests, 1),
        })
    with open(prob_dir / 'init.yml', 'w') as f:
        # Simple YAML without library
        f.write('test_cases:\n')
        for tc in init['test_cases']:
            f.write(f'- {{in: {tc["in"]}, out: {tc["out"]}, points: {tc["points"]}}}\n')

def create_problem(code, name, desc, difficulty, time_limit, memory_limit, ptype_key, tests_fn):
    """Create problem in DB + test files. Returns True if created, False if skipped."""
    if Problem.objects.filter(code=code).exists():
        return False

    prob_dir = PROBLEMS_DIR / code
    prob_dir.mkdir(parents=True, exist_ok=True)

    # Generate tests
    test_data = tests_fn()
    for i, (inp, out) in enumerate(test_data, 1):
        write_test(prob_dir, i, inp, out)
    write_init(prob_dir, len(test_data))

    # Create in DB
    p = Problem(
        code=code,
        name=name,
        description=desc,
        time_limit=time_limit,
        memory_limit=memory_limit * 1024,  # KB
        points=difficulty,
        group=group_general,
        is_public=True,
        is_manually_managed=False,
        date=timezone.now(),
    )
    p.save()
    p.types.add(types[ptype_key])
    p.allowed_languages.set(allowed_langs)
    p.authors.add(author)
    return True


# ================================================================
#                    PROBLEM GENERATORS
# ================================================================

def gen_math_problems():
    """100 math problems."""
    problems = []

    # --- Basic arithmetic (1-20) ---
    templates_arith = [
        ('sum-{n}', 'Сумма первых {n} чисел',
         'Вычислите сумму первых N натуральных чисел.\n\n## Вход\nN (1 <= N <= {lim})\n\n## Выход\nСумма 1 + 2 + ... + N.',
         lambda n: [(str(x), str(x*(x+1)//2)) for x in [1, 5, 10, 100, n, n-1, n//2]]),
        ('sum-squares-{n}', 'Сумма квадратов до {n}',
         'Вычислите сумму квадратов первых N натуральных чисел.\n\n## Вход\nN (1 <= N <= {lim})\n\n## Выход\n1^2 + 2^2 + ... + N^2.',
         lambda n: [(str(x), str(x*(x+1)*(2*x+1)//6)) for x in [1, 3, 5, 10, 100, n, n-1]]),
        ('sum-cubes-{n}', 'Сумма кубов до {n}',
         'Вычислите сумму кубов первых N натуральных чисел.\n\n## Вход\nN (1 <= N <= {lim})\n\n## Выход\n(1 + 2 + ... + N)^2 = 1^3 + 2^3 + ... + N^3.',
         lambda n: [(str(x), str((x*(x+1)//2)**2)) for x in [1, 2, 5, 10, 50, n, n-1]]),
    ]

    seq = 0
    for lim_power in range(2, 8):
        lim = 10**lim_power
        for tmpl_name, tmpl_title, tmpl_desc, gen_fn in templates_arith:
            seq += 1
            if seq > 20:
                break
            code = f'math-{seq:03d}'
            name = tmpl_title.format(n=lim)
            desc = tmpl_desc.format(n=lim, lim=lim)
            tests = gen_fn(lim)
            problems.append((code, name, desc, min(1 + lim_power // 2, 5), 2.0, 256, 'math',
                             lambda t=tests: t))
        if seq > 20:
            break

    # --- Modular arithmetic (21-40) ---
    for i in range(21, 41):
        mod = random.choice([7, 13, 97, 1000000007, 998244353])
        if i <= 30:
            code = f'math-{i:03d}'
            name = f'Остаток суммы по модулю {mod}'
            desc = (f'Даны N чисел. Найдите остаток их суммы при делении на {mod}.\n\n'
                    f'## Вход\nПервая строка: N (1 <= N <= 1000).\nВторая строка: N чисел (0 <= ai <= 10^9).\n\n'
                    f'## Выход\nОстаток суммы по модулю {mod}.')
            def gen(m=mod):
                tests = []
                for _ in range(7):
                    n = random.randint(1, 100)
                    nums = [random.randint(0, 10**9) for _ in range(n)]
                    tests.append((f'{n}\n{" ".join(map(str, nums))}', str(sum(nums) % m)))
                return tests
            problems.append((code, name, desc, 2, 1.0, 256, 'math', gen))
        else:
            code = f'math-{i:03d}'
            name = f'Произведение по модулю {mod}'
            desc = (f'Даны N чисел. Найдите остаток их произведения при делении на {mod}.\n\n'
                    f'## Вход\nПервая строка: N (1 <= N <= 1000).\nВторая строка: N чисел (1 <= ai <= 10^9).\n\n'
                    f'## Выход\nОстаток произведения по модулю {mod}.')
            def gen(m=mod):
                tests = []
                for _ in range(7):
                    n = random.randint(1, 50)
                    nums = [random.randint(1, 10**6) for _ in range(n)]
                    prod = 1
                    for x in nums:
                        prod = (prod * x) % m
                    tests.append((f'{n}\n{" ".join(map(str, nums))}', str(prod)))
                return tests
            problems.append((code, name, desc, 2, 1.0, 256, 'math', gen))

    # --- Power / exponentiation (41-55) ---
    for i in range(41, 56):
        code = f'math-{i:03d}'
        base = random.randint(2, 10)
        name = f'Степень {base}^N'
        desc = (f'Вычислите {base}^N по модулю 10^9 + 7.\n\n'
                f'## Вход\nN (0 <= N <= 10^18)\n\n## Выход\n{base}^N mod 10^9+7.')
        MOD = 10**9 + 7
        def gen(b=base):
            tests = []
            for exp in [0, 1, 2, 10, 100, 10**6, 10**9, 10**18, random.randint(1, 10**18)]:
                tests.append((str(exp), str(pow(b, exp, MOD))))
            return tests
        problems.append((code, name, desc, 3, 1.0, 256, 'math', gen))

    # --- Fibonacci variants (56-70) ---
    for i in range(56, 71):
        code = f'math-{i:03d}'
        mod = 10**9 + 7
        if i <= 63:
            name = f'Фибоначчи mod {mod}'
            desc = (f'Найдите N-е число Фибоначчи по модулю 10^9+7.\n'
                    f'F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2).\n\n'
                    f'## Вход\nN (0 <= N <= {10**(i-55)})\n\n## Выход\nF(N) mod 10^9+7.')
            def gen(lim=10**(i-55)):
                def fib(n, m=mod):
                    a, b = 0, 1
                    for _ in range(n):
                        a, b = b, (a + b) % m
                    return a
                tests = []
                for n in [0, 1, 2, 5, 10, min(100, lim), min(1000, lim)]:
                    tests.append((str(n), str(fib(n))))
                return tests
        else:
            name = f'Трибоначчи mod {mod}'
            desc = (f'T(0)=0, T(1)=0, T(2)=1, T(n)=T(n-1)+T(n-2)+T(n-3).\n'
                    f'Найдите T(N) mod 10^9+7.\n\n'
                    f'## Вход\nN (0 <= N <= 10^6)\n\n## Выход\nT(N) mod 10^9+7.')
            def gen():
                def trib(n, m=mod):
                    if n < 2: return 0
                    if n == 2: return 1
                    a, b, c = 0, 0, 1
                    for _ in range(n - 2):
                        a, b, c = b, c, (a + b + c) % m
                    return c
                return [(str(n), str(trib(n))) for n in [0, 1, 2, 3, 5, 10, 100, 1000]]
        problems.append((code, name, desc, 3, 2.0, 256, 'math', gen))

    # --- GCD/LCM (71-85) ---
    for i in range(71, 86):
        code = f'math-{i:03d}'
        if i % 2 == 1:
            name = 'НОД двух чисел'
            desc = ('Найдите наибольший общий делитель двух чисел.\n\n'
                    '## Вход\nA B (1 <= A, B <= 10^18)\n\n## Выход\nНОД(A, B).')
            def gen():
                tests = []
                for _ in range(8):
                    a = random.randint(1, 10**9)
                    b = random.randint(1, 10**9)
                    tests.append((f'{a} {b}', str(math.gcd(a, b))))
                return tests
        else:
            name = 'НОК двух чисел'
            desc = ('Найдите наименьшее общее кратное двух чисел.\n\n'
                    '## Вход\nA B (1 <= A, B <= 10^9)\n\n## Выход\nНОК(A, B).')
            def gen():
                tests = []
                for _ in range(8):
                    a = random.randint(1, 10**6)
                    b = random.randint(1, 10**6)
                    tests.append((f'{a} {b}', str(a * b // math.gcd(a, b))))
                return tests
        problems.append((code, name, desc, 2, 1.0, 256, 'math', gen))

    # --- Misc math (86-100) ---
    for i in range(86, 101):
        code = f'math-{i:03d}'
        variants = [
            ('Абсолютное значение разности',
             'Даны два числа A и B. Выведите |A - B|.\n\n## Вход\nA B (-10^9 <= A, B <= 10^9)\n\n## Выход\n|A - B|.',
             lambda: [(f'{a} {b}', str(abs(a-b)))
                      for a, b in [(random.randint(-10**9, 10**9), random.randint(-10**9, 10**9)) for _ in range(8)]]),
            ('Минимум из трёх',
             'Даны три числа. Выведите минимальное.\n\n## Вход\nA B C\n\n## Выход\nМинимальное из трёх.',
             lambda: [(f'{a} {b} {c}', str(min(a,b,c)))
                      for a,b,c in [(random.randint(-100,100), random.randint(-100,100), random.randint(-100,100)) for _ in range(8)]]),
            ('Медиана трёх чисел',
             'Даны три числа. Выведите среднее по величине (медиану).\n\n## Вход\nA B C\n\n## Выход\nМедиана.',
             lambda: [(f'{a} {b} {c}', str(sorted([a,b,c])[1]))
                      for a,b,c in [(random.randint(-100,100), random.randint(-100,100), random.randint(-100,100)) for _ in range(8)]]),
            ('Знак числа',
             'Дано число N. Выведите 1 если положительное, -1 если отрицательное, 0 если ноль.\n\n## Вход\nN\n\n## Выход\n1, -1 или 0.',
             lambda: [(str(n), str((n > 0) - (n < 0)))
                      for n in [0, 1, -1, 100, -100, random.randint(-10**9, 10**9), random.randint(-10**9, 10**9), random.randint(1, 10**9)]]),
        ]
        v = variants[(i - 86) % len(variants)]
        problems.append((code, v[0], v[1], 1, 1.0, 256, 'math', v[2]))

    return problems


def gen_string_problems():
    """100 string problems."""
    problems = []

    templates = [
        ('Длина строки', 'Дана строка S. Выведите её длину.\n\n## Вход\nСтрока S (1 <= |S| <= 1000), состоящая из строчных латинских букв.\n\n## Выход\nДлина S.',
         lambda s: str(len(s)), 1),
        ('Перевернуть строку', 'Дана строка S. Выведите её задом наперёд.\n\n## Вход\nСтрока S (1 <= |S| <= 1000).\n\n## Выход\nS в обратном порядке.',
         lambda s: s[::-1], 1),
        ('Количество гласных', 'Подсчитайте количество гласных (a, e, i, o, u) в строке.\n\n## Вход\nСтрока S из строчных латинских букв (1 <= |S| <= 1000).\n\n## Выход\nКоличество гласных.',
         lambda s: str(sum(1 for c in s if c in 'aeiou')), 1),
        ('Количество согласных', 'Подсчитайте количество согласных в строке.\n\n## Вход\nСтрока S из строчных латинских букв.\n\n## Выход\nКоличество согласных.',
         lambda s: str(sum(1 for c in s if c.isalpha() and c not in 'aeiou')), 1),
        ('В верхний регистр', 'Переведите строку в верхний регистр.\n\n## Вход\nСтрока S.\n\n## Выход\nS в верхнем регистре.',
         lambda s: s.upper(), 1),
        ('Палиндром?', 'Проверьте, является ли строка палиндромом.\n\n## Вход\nСтрока S из строчных латинских букв (1 <= |S| <= 1000).\n\n## Выход\nYES или NO.',
         lambda s: 'YES' if s == s[::-1] else 'NO', 2),
        ('Самый частый символ', 'Найдите символ, который встречается чаще всего. Если несколько — выведите первый по алфавиту.\n\n## Вход\nСтрока S из строчных латинских букв (1 <= |S| <= 1000).\n\n## Выход\nСамый частый символ.',
         lambda s: sorted([(s.count(c), c) for c in set(s)], key=lambda x: (-x[0], x[1]))[0][1], 2),
        ('Удалить дубликаты', 'Удалите повторяющиеся символы, оставив первое вхождение.\n\n## Вход\nСтрока S (1 <= |S| <= 1000).\n\n## Выход\nS без дубликатов.',
         lambda s: ''.join(dict.fromkeys(s)), 2),
        ('Количество слов', 'Посчитайте количество слов в строке (слова разделены пробелами).\n\n## Вход\nСтрока S (1 <= |S| <= 1000).\n\n## Выход\nКоличество слов.',
         lambda s: str(len(s.split())), 1),
        ('Сжатие строки', 'Сжать строку: "aaabbc" -> "a3b2c1".\n\n## Вход\nСтрока S из строчных латинских букв (1 <= |S| <= 1000).\n\n## Выход\nСжатая строка.',
         lambda s: ''.join(c + str(len(list(g))) for c, g in __import__('itertools').groupby(s)), 3),
    ]

    def rand_str(n, alpha='abcdefghijklmnopqrstuvwxyz'):
        return ''.join(random.choice(alpha) for _ in range(n))

    def rand_palindrome(n):
        half = rand_str(n // 2)
        return half + (random.choice('abcde') if n % 2 else '') + half[::-1]

    seq = 0
    for repeat in range(10):
        for tmpl_name, tmpl_desc, solve_fn, diff in templates:
            seq += 1
            code = f'str-{seq:03d}'
            name = tmpl_name + (f' #{repeat+1}' if repeat > 0 else '')

            def gen(fn=solve_fn, tname=tmpl_name):
                tests = []
                for _ in range(8):
                    length = random.randint(1, 100)
                    if 'палиндром' in tname.lower():
                        s = rand_palindrome(length) if random.random() < 0.4 else rand_str(length)
                    elif 'слов' in tname.lower():
                        s = ' '.join(rand_str(random.randint(1, 10)) for _ in range(random.randint(1, 15)))
                    else:
                        s = rand_str(length)
                    tests.append((s, fn(s)))
                return tests

            problems.append((code, name, tmpl_desc, diff, 1.0, 256, 'strings', gen))

    return problems


def gen_array_problems():
    """100 array problems."""
    problems = []

    templates = [
        ('Сумма массива', 'Найдите сумму элементов массива.\n\n## Вход\nN (1 <= N <= 10^5)\nN целых чисел (-10^9 <= ai <= 10^9).\n\n## Выход\nСумма.',
         lambda a: str(sum(a)), 1),
        ('Максимум массива', 'Найдите максимальный элемент.\n\n## Вход\nN, затем N чисел.\n\n## Выход\nМаксимум.',
         lambda a: str(max(a)), 1),
        ('Минимум массива', 'Найдите минимальный элемент.\n\n## Вход\nN, затем N чисел.\n\n## Выход\nМинимум.',
         lambda a: str(min(a)), 1),
        ('Среднее арифметическое', 'Найдите среднее арифметическое с точностью до 6 знаков.\n\n## Вход\nN, затем N чисел.\n\n## Выход\nСреднее с 6 знаками после точки.',
         lambda a: f'{sum(a)/len(a):.6f}', 2),
        ('Количество положительных', 'Сколько положительных чисел в массиве?\n\n## Вход\nN, затем N чисел.\n\n## Выход\nКоличество положительных.',
         lambda a: str(sum(1 for x in a if x > 0)), 1),
        ('Количество чётных', 'Сколько чётных чисел?\n\n## Вход\nN, затем N чисел.\n\n## Выход\nКоличество чётных.',
         lambda a: str(sum(1 for x in a if x % 2 == 0)), 1),
        ('Второй максимум', 'Найдите второй по величине элемент (все элементы различны).\n\n## Вход\nN (N >= 2), затем N различных чисел.\n\n## Выход\nВторой максимум.',
         lambda a: str(sorted(set(a))[-2]) if len(set(a)) >= 2 else str(max(a)), 2),
        ('Перевернуть массив', 'Выведите массив в обратном порядке.\n\n## Вход\nN, затем N чисел.\n\n## Выход\nМассив задом наперёд, через пробел.',
         lambda a: ' '.join(map(str, a[::-1])), 1),
        ('Префиксные суммы', 'Для каждого i выведите сумму a[1..i].\n\n## Вход\nN, затем N чисел.\n\n## Выход\nN префиксных сумм через пробел.',
         lambda a: ' '.join(str(s) for s in __import__('itertools').accumulate(a)), 2),
        ('Количество уникальных', 'Сколько различных значений в массиве?\n\n## Вход\nN, затем N чисел.\n\n## Выход\nКоличество различных.',
         lambda a: str(len(set(a))), 2),
    ]

    seq = 0
    for repeat in range(10):
        for tmpl_name, tmpl_desc, solve_fn, diff in templates:
            seq += 1
            code = f'arr-{seq:03d}'
            name = tmpl_name + (f' #{repeat+1}' if repeat > 0 else '')

            def gen(fn=solve_fn, tname=tmpl_name):
                tests = []
                for _ in range(8):
                    n = random.randint(2, 200)
                    if 'второй' in tname.lower():
                        a = random.sample(range(-1000, 1000), min(n, 500))
                    else:
                        a = [random.randint(-1000, 1000) for _ in range(n)]
                    inp = f'{len(a)}\n{" ".join(map(str, a))}'
                    tests.append((inp, fn(a)))
                return tests

            problems.append((code, name, tmpl_desc, diff, 2.0, 256, 'arrays', gen))

    return problems


def gen_sorting_problems():
    """100 sorting problems."""
    problems = []

    templates = [
        ('Сортировка по возрастанию', 'Отсортируйте массив по возрастанию.\n\n## Вход\nN, затем N чисел.\n\n## Выход\nОтсортированный массив.',
         lambda a: ' '.join(map(str, sorted(a))), 1),
        ('Сортировка по убыванию', 'Отсортируйте массив по убыванию.\n\n## Вход\nN, затем N чисел.\n\n## Выход\nОтсортированный массив по убыванию.',
         lambda a: ' '.join(map(str, sorted(a, reverse=True))), 1),
        ('K-й минимум', 'Найдите K-й минимальный элемент.\n\n## Вход\nN K, затем N чисел.\n\n## Выход\nK-й минимальный.',
         lambda a, k=1: str(sorted(a)[k-1]), 2),
        ('Медиана массива', 'Найдите медиану. При чётном N — меньший из двух средних.\n\n## Вход\nN, затем N чисел.\n\n## Выход\nМедиана.',
         lambda a: str(sorted(a)[(len(a)-1)//2]), 2),
        ('Количество инверсий (простое)', 'Посчитайте пары (i,j), где i < j, но a[i] > a[j].\n\n## Вход\nN (N <= 1000), затем N чисел.\n\n## Выход\nКоличество инверсий.',
         lambda a: str(sum(1 for i in range(len(a)) for j in range(i+1, len(a)) if a[i] > a[j])), 3),
        ('Сортировка чётных', 'Выведите только чётные числа массива, отсортированные.\n\n## Вход\nN, затем N чисел.\n\n## Выход\nЧётные числа по возрастанию.',
         lambda a: ' '.join(map(str, sorted(x for x in a if x % 2 == 0))) or '0', 2),
        ('Ближайшие к нулю', 'Выведите K чисел, ближайших к нулю.\n\n## Вход\nN K, затем N чисел.\n\n## Выход\nK ближайших к нулю по возрастанию.',
         lambda a, k=1: ' '.join(map(str, sorted(sorted(a, key=abs)[:k]))), 2),
        ('Мода массива', 'Найдите самый частый элемент. Если несколько — минимальный.\n\n## Вход\nN, затем N чисел.\n\n## Выход\nМода.',
         lambda a: str(min(x for x in a if a.count(x) == max(a.count(y) for y in set(a)))), 2),
        ('Удалить дубликаты (sorted)', 'Выведите уникальные элементы по возрастанию.\n\n## Вход\nN, затем N чисел.\n\n## Выход\nУникальные по возрастанию.',
         lambda a: ' '.join(map(str, sorted(set(a)))), 2),
        ('Слияние двух массивов', 'Даны два отсортированных массива. Объедините в один отсортированный.\n\n## Вход\nN M, затем N чисел, затем M чисел.\n\n## Выход\nОбъединённый отсортированный массив.',
         lambda a: ' '.join(map(str, sorted(a))), 2),
    ]

    seq = 0
    for repeat in range(10):
        for tmpl_name, tmpl_desc, solve_fn, diff in templates:
            seq += 1
            code = f'sort-{seq:03d}'
            name = tmpl_name + (f' #{repeat+1}' if repeat > 0 else '')

            def gen(fn=solve_fn, tname=tmpl_name):
                tests = []
                for _ in range(7):
                    n = random.randint(2, 100)
                    a = [random.randint(-500, 500) for _ in range(n)]
                    if 'K-й' in tname or 'ближайш' in tname.lower():
                        k = random.randint(1, max(1, n // 2))
                        inp = f'{n} {k}\n{" ".join(map(str, a))}'
                        tests.append((inp, fn(a, k)))
                    elif 'слияни' in tname.lower():
                        m = random.randint(1, 50)
                        b = sorted([random.randint(-500, 500) for _ in range(m)])
                        a_sorted = sorted(a)
                        inp = f'{n} {m}\n{" ".join(map(str, a_sorted))}\n{" ".join(map(str, b))}'
                        tests.append((inp, ' '.join(map(str, sorted(a_sorted + b)))))
                    else:
                        inp = f'{n}\n{" ".join(map(str, a))}'
                        tests.append((inp, fn(a)))
                return tests

            problems.append((code, name, tmpl_desc, diff, 2.0, 256, 'sorting', gen))

    return problems


def gen_numtheory_problems():
    """100 number theory problems."""
    problems = []

    def is_prime(n):
        if n < 2: return False
        if n < 4: return True
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0: return False
            i += 6
        return True

    def count_divisors(n):
        if n <= 0: return 0
        c = 0
        for i in range(1, int(n**0.5) + 1):
            if n % i == 0:
                c += 2 if i != n // i else 1
        return c

    def sum_divisors(n):
        if n <= 0: return 0
        s = 0
        for i in range(1, int(n**0.5) + 1):
            if n % i == 0:
                s += i
                if i != n // i:
                    s += n // i
        return s

    def digit_sum(n):
        return sum(int(d) for d in str(abs(n)))

    templates = [
        ('Простое ли число?', 'Определите, является ли N простым.\n\n## Вход\nN (2 <= N <= 10^9)\n\n## Выход\nYES или NO.',
         lambda n: 'YES' if is_prime(n) else 'NO', 2,
         lambda: [(str(n), 'YES' if is_prime(n) else 'NO') for n in [2, 3, 4, 17, 100, 997, random.randint(2, 10**6), random.randint(2, 10**6)]]),
        ('Количество делителей', 'Найдите количество делителей N.\n\n## Вход\nN (1 <= N <= 10^9)\n\n## Выход\nКоличество делителей.',
         lambda n: str(count_divisors(n)), 2,
         lambda: [(str(n), str(count_divisors(n))) for n in [1, 6, 12, 100, 1000, random.randint(1, 10**6), random.randint(1, 10**6), random.randint(1, 10**6)]]),
        ('Сумма делителей', 'Найдите сумму всех делителей N.\n\n## Вход\nN (1 <= N <= 10^9)\n\n## Выход\nСумма делителей.',
         lambda n: str(sum_divisors(n)), 2,
         lambda: [(str(n), str(sum_divisors(n))) for n in [1, 6, 12, 28, 100, random.randint(1, 10**5), random.randint(1, 10**5), random.randint(1, 10**5)]]),
        ('Сумма цифр', 'Найдите сумму цифр числа N.\n\n## Вход\nN (0 <= N <= 10^18)\n\n## Выход\nСумма цифр.',
         lambda n: str(digit_sum(n)), 1,
         lambda: [(str(n), str(digit_sum(n))) for n in [0, 5, 123, 999, 1000000, random.randint(0, 10**15), random.randint(0, 10**15), random.randint(0, 10**15)]]),
        ('Количество цифр', 'Сколько цифр в числе N?\n\n## Вход\nN (0 <= N <= 10^18)\n\n## Выход\nКоличество цифр.',
         lambda n: str(len(str(n))), 1,
         lambda: [(str(n), str(len(str(n)))) for n in [0, 5, 10, 999, 10000, 10**9, random.randint(1, 10**15), random.randint(1, 10**15)]]),
    ]

    seq = 0
    for repeat in range(20):
        for tmpl_name, tmpl_desc, _, diff, gen_fn in templates:
            seq += 1
            if seq > 100:
                break
            code = f'nt-{seq:03d}'
            name = tmpl_name + (f' #{repeat+1}' if repeat > 0 else '')
            problems.append((code, name, tmpl_desc, diff, 2.0, 256, 'numtheory', gen_fn))
        if seq > 100:
            break

    return problems[:100]


def gen_geometry_problems():
    """50 geometry problems."""
    problems = []
    seq = 0

    templates = [
        ('Площадь прямоугольника', 'Даны стороны A и B. Площадь?\n\n## Вход\nA B (1 <= A, B <= 10^9)\n\n## Выход\nA * B.',
         lambda: [(f'{a} {b}', str(a*b)) for a, b in [(random.randint(1, 10**4), random.randint(1, 10**4)) for _ in range(8)]], 1),
        ('Периметр прямоугольника', 'P = 2*(A+B).\n\n## Вход\nA B\n\n## Выход\nПериметр.',
         lambda: [(f'{a} {b}', str(2*(a+b))) for a, b in [(random.randint(1, 10**4), random.randint(1, 10**4)) for _ in range(8)]], 1),
        ('Площадь треугольника', 'Даны основание B и высота H. Площадь = B*H/2.\n\n## Вход\nB H (целые)\n\n## Выход\nПлощадь с 1 знаком после точки.',
         lambda: [(f'{b} {h}', f'{b*h/2:.1f}') for b, h in [(random.randint(1, 1000), random.randint(1, 1000)) for _ in range(8)]], 1),
        ('Расстояние между точками', 'Даны (x1,y1) и (x2,y2). Расстояние?\n\n## Вход\nx1 y1 x2 y2\n\n## Выход\nРасстояние с 6 знаками.',
         lambda: [(f'{x1} {y1} {x2} {y2}', f'{((x2-x1)**2+(y2-y1)**2)**0.5:.6f}')
                  for x1,y1,x2,y2 in [(random.randint(-100,100), random.randint(-100,100), random.randint(-100,100), random.randint(-100,100)) for _ in range(8)]], 2),
        ('Площадь круга', 'Дан радиус R. Площадь = pi * R^2.\n\n## Вход\nR (1 <= R <= 10000)\n\n## Выход\nПлощадь с 6 знаками.',
         lambda: [(str(r), f'{math.pi * r**2:.6f}') for r in [1, 2, 5, 10, 100, random.randint(1,1000), random.randint(1,1000), random.randint(1,1000)]], 1),
    ]

    for repeat in range(10):
        for tmpl_name, tmpl_desc, gen_fn, diff in templates:
            seq += 1
            if seq > 50:
                break
            code = f'geo-{seq:03d}'
            name = tmpl_name + (f' #{repeat+1}' if repeat > 0 else '')
            problems.append((code, name, tmpl_desc, diff, 1.0, 256, 'geometry', gen_fn))
        if seq > 50:
            break

    return problems[:50]


def gen_greedy_problems():
    """100 greedy problems."""
    problems = []

    templates = [
        ('Размен монетами', 'Даны монеты 1, 5, 10, 25. Минимальное количество монет для суммы N.\n\n## Вход\nN (1 <= N <= 10^6)\n\n## Выход\nМинимальное количество монет.',
         lambda n: (lambda r: r)((n // 25) + ((n % 25) // 10) + (((n % 25) % 10) // 5) + (((n % 25) % 10) % 5)), 2),
        ('Максимальное количество отрезков', 'Отрезок длиной L. Нарезать куски длиной A. Сколько кусков?\n\n## Вход\nL A (1 <= A <= L <= 10^9)\n\n## Выход\nL // A.',
         lambda l, a: l // a, 1),
        ('Максимальная сумма непересекающихся', 'Из N чисел выбрать как можно больше с суммой <= S.\n\n## Вход\nN S, затем N чисел (все положительные).\n\n## Выход\nМаксимальное количество.',
         None, 2),
    ]

    seq = 0
    for repeat in range(34):
        for idx, (tmpl_name, tmpl_desc, solve_fn, diff) in enumerate(templates):
            seq += 1
            if seq > 100:
                break
            code = f'greedy-{seq:03d}'
            name = tmpl_name + (f' #{repeat+1}' if repeat > 0 else '')

            if idx == 0:
                def gen():
                    return [(str(n), str((n//25) + ((n%25)//10) + (((n%25)%10)//5) + (((n%25)%10)%5)))
                            for n in [1, 5, 10, 25, 30, 99, random.randint(1, 10000), random.randint(1, 10000)]]
            elif idx == 1:
                def gen():
                    tests = []
                    for _ in range(8):
                        a = random.randint(1, 1000)
                        l = a * random.randint(1, 1000) + random.randint(0, a-1)
                        tests.append((f'{l} {a}', str(l // a)))
                    return tests
            else:
                def gen():
                    tests = []
                    for _ in range(8):
                        n = random.randint(1, 100)
                        nums = sorted([random.randint(1, 100) for _ in range(n)])
                        s = random.randint(sum(nums) // 3, sum(nums))
                        count = 0
                        cur = 0
                        for x in nums:
                            if cur + x <= s:
                                cur += x
                                count += 1
                        tests.append((f'{n} {s}\n{" ".join(map(str, nums))}', str(count)))
                    return tests

            problems.append((code, name, tmpl_desc, diff, 2.0, 256, 'greedy', gen))
        if seq > 100:
            break

    return problems[:100]


def gen_dp_problems():
    """50 DP problems."""
    problems = []

    seq = 0
    # Climbing stairs variants
    for step_options in [(1,2), (1,2,3), (1,3), (2,3), (1,2,5)]:
        for max_n in [20, 50, 100, 1000]:
            seq += 1
            if seq > 50:
                break
            steps_str = ', '.join(map(str, step_options))
            code = f'dp-{seq:03d}'
            name = f'Лестница ({steps_str})'
            desc = (f'Сколько способов подняться на N ступеней, если за раз можно подняться на {steps_str} ступеней?\n'
                    f'Ответ по модулю 10^9+7.\n\n'
                    f'## Вход\nN (1 <= N <= {max_n})\n\n## Выход\nКоличество способов mod 10^9+7.')
            MOD = 10**9 + 7
            def gen(steps=step_options, lim=max_n):
                tests = []
                for n in [1, 2, 3, 5, 10, min(20, lim), min(50, lim)]:
                    dp = [0] * (n + 1)
                    dp[0] = 1
                    for i in range(1, n + 1):
                        for s in steps:
                            if i >= s:
                                dp[i] = (dp[i] + dp[i - s]) % MOD
                    tests.append((str(n), str(dp[n])))
                return tests
            problems.append((code, name, desc, 3, 1.0, 256, 'dp', gen))
        if seq > 50:
            break

    # Max subarray sum (Kadane)
    for _ in range(10):
        seq += 1
        if seq > 50:
            break
        code = f'dp-{seq:03d}'
        name = 'Максимальная подмассивная сумма'
        desc = ('Найдите максимальную сумму непрерывного подмассива (алгоритм Кадане).\n\n'
                '## Вход\nN (1 <= N <= 10^5), затем N чисел.\n\n## Выход\nМаксимальная сумма подмассива.')
        def gen():
            tests = []
            for _ in range(7):
                n = random.randint(1, 200)
                a = [random.randint(-100, 100) for _ in range(n)]
                # Kadane
                best = cur = a[0]
                for x in a[1:]:
                    cur = max(x, cur + x)
                    best = max(best, cur)
                tests.append((f'{n}\n{" ".join(map(str, a))}', str(best)))
            return tests
        problems.append((code, name, desc, 3, 2.0, 256, 'dp', gen))

    return problems[:50]


def gen_impl_problems():
    """200 implementation problems."""
    problems = []

    templates = [
        ('Чётное или нечётное', 'Определите, чётное ли число.\n\n## Вход\nN (-10^9 <= N <= 10^9)\n\n## Выход\nEven или Odd.',
         lambda n: 'Even' if n % 2 == 0 else 'Odd', 1,
         lambda: [(str(n), 'Even' if n%2==0 else 'Odd') for n in [0,1,2,-3,100,999,random.randint(-10**9,10**9),random.randint(-10**9,10**9)]]),
        ('Високосный год', 'Определите, является ли год високосным.\n\n## Вход\nY (1 <= Y <= 10^9)\n\n## Выход\nYES или NO.',
         lambda y: 'YES' if (y%4==0 and y%100!=0) or y%400==0 else 'NO', 1,
         lambda: [(str(y), 'YES' if (y%4==0 and y%100!=0) or y%400==0 else 'NO') for y in [2000,1900,2024,2023,2100,400,random.randint(1,3000),random.randint(1,3000)]]),
        ('FizzBuzz', 'Для числа N: если делится на 3 и 5 — "FizzBuzz", на 3 — "Fizz", на 5 — "Buzz", иначе число.\n\n## Вход\nN (1 <= N <= 10^6)\n\n## Выход\nFizz, Buzz, FizzBuzz или N.',
         None, 1,
         lambda: [(str(n), 'FizzBuzz' if n%15==0 else ('Fizz' if n%3==0 else ('Buzz' if n%5==0 else str(n)))) for n in [1,3,5,15,7,30,random.randint(1,1000),random.randint(1,1000)]]),
        ('Перевод в двоичную', 'Переведите N в двоичную систему.\n\n## Вход\nN (0 <= N <= 10^18)\n\n## Выход\nN в двоичной.',
         None, 1,
         lambda: [(str(n), bin(n)[2:]) for n in [0,1,2,5,10,255,1024,random.randint(0,10**9)]]),
        ('Обратное число', 'Переверните цифры числа (без ведущих нулей). Для отрицательных сохраните знак.\n\n## Вход\nN\n\n## Выход\nN с перевёрнутыми цифрами.',
         None, 2,
         lambda: [(str(n), ('-' + str(abs(n))[::-1].lstrip('0') if n < 0 else str(n)[::-1].lstrip('0')) or '0') for n in [123, -456, 1000, 0, 12345, random.randint(1,10**9), random.randint(-10**9,-1), random.randint(1,10**9)]]),
    ]

    seq = 0
    for repeat in range(40):
        for tmpl_name, tmpl_desc, _, diff, gen_fn in templates:
            seq += 1
            if seq > 200:
                break
            code = f'impl-{seq:03d}'
            name = tmpl_name + (f' #{repeat+1}' if repeat > 0 else '')
            problems.append((code, name, tmpl_desc, diff, 1.0, 256, 'impl', gen_fn))
        if seq > 200:
            break

    return problems[:200]


def gen_combinatorics_problems():
    """50 combinatorics problems."""
    problems = []

    seq = 0
    for repeat in range(10):
        # Factorial
        seq += 1
        code = f'comb-{seq:03d}'
        name = f'Факториал mod 10^9+7' + (f' #{repeat+1}' if repeat > 0 else '')
        desc = 'Вычислите N! mod 10^9+7.\n\n## Вход\nN (0 <= N <= 10^6)\n\n## Выход\nN! mod 10^9+7.'
        MOD = 10**9 + 7
        def gen_fact():
            tests = []
            for n in [0, 1, 5, 10, 20, 100, 1000, random.randint(1, 10000)]:
                f = 1
                for i in range(2, n+1):
                    f = (f * i) % MOD
                tests.append((str(n), str(f)))
            return tests
        problems.append((code, name, desc, 2, 1.0, 256, 'combinatorics', gen_fact))

        # C(n, k)
        seq += 1
        code = f'comb-{seq:03d}'
        name = f'C(N, K) mod 10^9+7' + (f' #{repeat+1}' if repeat > 0 else '')
        desc = 'Вычислите биномиальный коэффициент C(N, K) mod 10^9+7.\n\n## Вход\nN K (0 <= K <= N <= 1000)\n\n## Выход\nC(N,K) mod 10^9+7.'
        def gen_cnk():
            tests = []
            for n, k in [(0,0),(1,0),(1,1),(5,2),(10,3),(20,10),(100,50)]:
                c = math.comb(n, k) % MOD
                tests.append((f'{n} {k}', str(c)))
            return tests
        problems.append((code, name, desc, 3, 1.0, 256, 'combinatorics', gen_cnk))

        # Permutations count
        seq += 1
        if seq > 50:
            break
        code = f'comb-{seq:03d}'
        name = f'P(N, K) — размещения' + (f' #{repeat+1}' if repeat > 0 else '')
        desc = 'Вычислите P(N, K) = N! / (N-K)! mod 10^9+7.\n\n## Вход\nN K (0 <= K <= N <= 1000)\n\n## Выход\nP(N,K) mod 10^9+7.'
        def gen_pnk():
            tests = []
            for n, k in [(1,0),(1,1),(5,2),(10,3),(20,5),(100,10)]:
                p = math.perm(n, k) % MOD
                tests.append((f'{n} {k}', str(p)))
            return tests
        problems.append((code, name, desc, 3, 1.0, 256, 'combinatorics', gen_pnk))

        # More variants
        seq += 1
        if seq > 50:
            break
        code = f'comb-{seq:03d}'
        name = f'Треугольник Паскаля (строка {repeat+1})'
        desc = f'Выведите N-ю строку треугольника Паскаля (нумерация с 0).\n\n## Вход\nN (0 <= N <= 30)\n\n## Выход\nN-я строка через пробел.'
        def gen_pascal():
            tests = []
            for n in [0, 1, 2, 3, 5, 10, 15, 20]:
                row = [math.comb(n, k) for k in range(n + 1)]
                tests.append((str(n), ' '.join(map(str, row))))
            return tests
        problems.append((code, name, desc, 2, 1.0, 256, 'combinatorics', gen_pascal))

        seq += 1
        if seq > 50:
            break
        code = f'comb-{seq:03d}'
        name = f'Каталаново число' + (f' #{repeat+1}' if repeat > 0 else '')
        desc = 'Вычислите N-е число Каталана mod 10^9+7.\nC(n) = C(2n, n) / (n+1).\n\n## Вход\nN (0 <= N <= 1000)\n\n## Выход\nC(N) mod 10^9+7.'
        def gen_catalan():
            tests = []
            for n in [0, 1, 2, 3, 5, 10, 15, 20]:
                c = math.comb(2*n, n) // (n + 1) % MOD
                tests.append((str(n), str(c)))
            return tests
        problems.append((code, name, desc, 4, 1.0, 256, 'combinatorics', gen_catalan))

    return problems[:50]


def gen_binary_search_problems():
    """100 binary search problems."""
    problems = []

    seq = 0
    for repeat in range(20):
        # Find element
        seq += 1
        code = f'bs-{seq:03d}'
        name = f'Поиск элемента' + (f' #{repeat+1}' if repeat > 0 else '')
        desc = ('В отсортированном массиве найдите позицию элемента X (1-индексация). Если нет — выведите -1.\n\n'
                '## Вход\nN X, затем N отсортированных чисел.\n\n## Выход\nПозиция X или -1.')
        def gen():
            tests = []
            for _ in range(8):
                n = random.randint(1, 200)
                a = sorted(random.sample(range(-500, 500), min(n, 500)))
                x = random.choice(a) if random.random() < 0.6 else random.randint(-600, 600)
                pos = a.index(x) + 1 if x in a else -1
                tests.append((f'{len(a)} {x}\n{" ".join(map(str, a))}', str(pos)))
            return tests
        problems.append((code, name, desc, 2, 1.0, 256, 'binary', gen))

        # Lower bound
        seq += 1
        code = f'bs-{seq:03d}'
        name = f'Нижняя граница' + (f' #{repeat+1}' if repeat > 0 else '')
        desc = ('В отсортированном массиве найдите первый элемент >= X.\n\n'
                '## Вход\nN X, затем N отсортированных чисел.\n\n## Выход\nЗначение первого элемента >= X, или "NONE".')
        def gen():
            tests = []
            for _ in range(8):
                n = random.randint(1, 200)
                a = sorted([random.randint(-500, 500) for _ in range(n)])
                x = random.randint(-600, 600)
                found = [v for v in a if v >= x]
                tests.append((f'{n} {x}\n{" ".join(map(str, a))}', str(found[0]) if found else 'NONE'))
            return tests
        problems.append((code, name, desc, 2, 1.0, 256, 'binary', gen))

        # Count >= X
        seq += 1
        code = f'bs-{seq:03d}'
        name = f'Количество >= X' + (f' #{repeat+1}' if repeat > 0 else '')
        desc = ('Сколько элементов отсортированного массива >= X?\n\n'
                '## Вход\nN X, затем N отсортированных чисел.\n\n## Выход\nКоличество.')
        def gen():
            tests = []
            for _ in range(8):
                n = random.randint(1, 200)
                a = sorted([random.randint(-500, 500) for _ in range(n)])
                x = random.randint(-600, 600)
                tests.append((f'{n} {x}\n{" ".join(map(str, a))}', str(sum(1 for v in a if v >= x))))
            return tests
        problems.append((code, name, desc, 2, 1.0, 256, 'binary', gen))

        # Sqrt (integer)
        seq += 1
        code = f'bs-{seq:03d}'
        name = f'Целый квадратный корень' + (f' #{repeat+1}' if repeat > 0 else '')
        desc = ('Найдите целую часть квадратного корня из N.\n\n## Вход\nN (0 <= N <= 10^18)\n\n## Выход\nfloor(sqrt(N)).')
        def gen():
            tests = []
            for n in [0, 1, 4, 8, 10, 100, 10**9, 10**18, random.randint(0, 10**18)]:
                tests.append((str(n), str(int(n**0.5))))
            return tests
        problems.append((code, name, desc, 2, 1.0, 256, 'binary', gen))

        # Cube root
        seq += 1
        if seq > 100:
            break
        code = f'bs-{seq:03d}'
        name = f'Целый кубический корень' + (f' #{repeat+1}' if repeat > 0 else '')
        desc = ('Найдите целую часть кубического корня из N.\n\n## Вход\nN (0 <= N <= 10^18)\n\n## Выход\nfloor(cbrt(N)).')
        def gen():
            tests = []
            for n in [0, 1, 8, 27, 100, 10**9, 10**18, random.randint(0, 10**15)]:
                r = int(round(n ** (1/3)))
                while (r+1)**3 <= n: r += 1
                while r**3 > n: r -= 1
                tests.append((str(n), str(r)))
            return tests
        problems.append((code, name, desc, 3, 1.0, 256, 'binary', gen))

    return problems[:100]


# ================================================================
#                         MAIN
# ================================================================

if __name__ == '__main__':
    random.seed(42)  # reproducible

    generators = [
        ('Math', gen_math_problems),
        ('Strings', gen_string_problems),
        ('Arrays', gen_array_problems),
        ('Sorting', gen_sorting_problems),
        ('Number Theory', gen_numtheory_problems),
        ('Geometry', gen_geometry_problems),
        ('Greedy', gen_greedy_problems),
        ('DP', gen_dp_problems),
        ('Implementation', gen_impl_problems),
        ('Combinatorics', gen_combinatorics_problems),
        ('Binary Search', gen_binary_search_problems),
    ]

    total = 0
    created = 0
    skipped = 0

    for cat_name, gen_fn in generators:
        problems = gen_fn()
        cat_created = 0
        for code, name, desc, diff, tl, ml, ptype, tests_fn in problems:
            total += 1
            try:
                if create_problem(code, name, desc, diff, tl, ml, ptype, tests_fn):
                    cat_created += 1
                    created += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f'  ERROR {code}: {e}')
                skipped += 1
        print(f'{cat_name}: {cat_created} created, {len(problems)} total')

    print(f'\n=== DONE: {created} created, {skipped} skipped, {total} total ===')
    print(f'Problems in DB: {Problem.objects.count()}')
