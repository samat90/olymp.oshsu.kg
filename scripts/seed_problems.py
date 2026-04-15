#!/usr/bin/env python
"""Seed 25 varied-difficulty problems for OshSU Olymp.
Run: venv/Scripts/python.exe scripts/seed_problems.py
"""
import os
import sys
import django

# Ensure UTF-8 stdout on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
django.setup()

from django.conf import settings
from judge.models import Problem, ProblemGroup, ProblemType, Language, Judge
from django.contrib.auth.models import User


PROBLEMS_DIR = settings.DMOJ_PROBLEM_DATA_ROOT


def make_problem_files(code, tests):
    """Create problem directory with init.yml and test case files."""
    pdir = os.path.join(PROBLEMS_DIR, code)
    os.makedirs(pdir, exist_ok=True)
    # Write each test case input and output
    for i, (inp, out) in enumerate(tests, 1):
        with open(os.path.join(pdir, f'{i}.in'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(inp if inp.endswith('\n') else inp + '\n')
        with open(os.path.join(pdir, f'{i}.out'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(out if out.endswith('\n') else out + '\n')
    # Write init.yml
    pts = 100 // len(tests)
    remainder = 100 - pts * len(tests)
    test_yaml = []
    for i in range(len(tests)):
        p = pts + (1 if i < remainder else 0)
        test_yaml.append(f"  - {{in: {i+1}.in, out: {i+1}.out, points: {p}}}")
    with open(os.path.join(pdir, 'init.yml'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('archive: ~\n\ntest_cases:\n' + '\n'.join(test_yaml) + '\n')


def upsert_problem(code, name, description, time_limit, memory_limit, points, tests, group, types_keys):
    make_problem_files(code, tests)
    p, created = Problem.objects.update_or_create(
        code=code,
        defaults={
            'name': name,
            'description': description,
            'group': group,
            'time_limit': time_limit,
            'memory_limit': memory_limit,
            'points': points,
            'partial': False,
            'is_public': True,
            'is_manually_managed': False,
        },
    )
    if types_keys:
        types = ProblemType.objects.filter(name__in=types_keys)
        p.types.set(types)
    admin = User.objects.filter(username='admin').first()
    if admin:
        p.authors.set([admin.profile])
    return p, created


# Problem types (Russian labels)
TYPES_MAP = {
    'math': 'Математика',
    'impl': 'Реализация',
    'strings': 'Строки',
    'arrays': 'Массивы',
    'sort': 'Сортировка',
    'greedy': 'Жадные',
    'dp': 'Динамическое программирование',
    'num': 'Теория чисел',
    'geo': 'Геометрия',
}


def ensure_types():
    for key, label in TYPES_MAP.items():
        ProblemType.objects.update_or_create(name=key, defaults={'full_name': label})


# --- Problem catalog (25 problems) ---
PROBLEMS = [
    # ===== EASY (1 point) =====
    ('aminusb', 'A − B', 'Разность двух чисел', 1, 1,
     'Даны два целых числа **A** и **B**. Выведите их разность **A − B**.\n\n'
     '## Входные данные\nОдна строка: два числа $A$ и $B$ ($-10^9 \\le A, B \\le 10^9$).\n\n'
     '## Выходные данные\nОдно число — $A - B$.',
     [('5 3', '2'), ('0 0', '0'), ('10 -5', '15'),
      ('-1000000000 1000000000', '-2000000000'), ('42 42', '0')], ['math']),

    ('aplusbplusc', 'A + B + C', 'Сумма трёх чисел', 1, 1,
     'Даны три целых числа. Выведите их сумму.\n\n'
     '## Вход\nТри числа через пробел, каждое от $-10^9$ до $10^9$.\n\n'
     '## Выход\nИх сумма.',
     [('1 2 3', '6'), ('0 0 0', '0'), ('-1 -2 -3', '-6'),
      ('1000000000 1000000000 1000000000', '3000000000'), ('5 -3 7', '9')], ['math']),

    ('max-of-two', 'Максимум из двух', 'Простое сравнение', 1, 1,
     'Даны два целых числа. Выведите наибольшее из них.\n\n'
     '## Вход\nДва числа $A$ и $B$ ($|A|, |B| \\le 10^9$).\n\n'
     '## Выход\nНаибольшее число.',
     [('3 5', '5'), ('10 -7', '10'), ('0 0', '0'),
      ('-100 -200', '-100'), ('42 42', '42')], ['impl']),

    ('max-of-three', 'Максимум из трёх', '', 1, 1,
     'Даны три целых числа. Выведите наибольшее.\n\n'
     '## Вход\nТри числа $A$, $B$, $C$ через пробел.\n\n'
     '## Выход\nНаибольшее число.',
     [('1 2 3', '3'), ('5 5 5', '5'), ('-10 -20 -5', '-5'),
      ('100 50 75', '100'), ('0 1 -1', '1')], ['impl']),

    ('square-area', 'Площадь квадрата', 'Квадрат стороны', 1, 1,
     'Дана длина стороны квадрата. Вычислите его площадь.\n\n'
     '## Вход\nОдно целое число $A$ ($1 \\le A \\le 10^4$) — длина стороны.\n\n'
     '## Выход\nПлощадь квадрата.',
     [('5', '25'), ('1', '1'), ('10', '100'), ('100', '10000'), ('9999', '99980001')], ['math', 'geo']),

    ('rect-perimeter', 'Периметр прямоугольника', '', 1, 1,
     'Даны стороны $A$ и $B$ прямоугольника. Выведите его периметр $2(A+B)$.\n\n'
     '## Вход\nДва числа $A$ и $B$ ($1 \\le A, B \\le 10^4$).\n\n'
     '## Выход\nПериметр.',
     [('3 4', '14'), ('5 5', '20'), ('1 1', '4'), ('100 50', '300'), ('10000 1', '20002')], ['math', 'geo']),

    ('swap-numbers', 'Обмен чисел', 'Вывести в обратном порядке', 1, 1,
     'Даны два целых числа $A$ и $B$. Выведите их в обратном порядке через пробел.\n\n'
     '## Вход\nДва числа.\n\n## Выход\n$B$ и $A$ через пробел.',
     [('1 2', '2 1'), ('5 5', '5 5'), ('-10 10', '10 -10'),
      ('100 0', '0 100'), ('7 13', '13 7')], ['impl']),

    ('even-or-odd', 'Чёт или нечёт', 'Проверка чётности', 1, 1,
     'Дано целое число. Выведите "even", если оно чётное, иначе "odd".\n\n'
     '## Вход\nЦелое число $N$ ($-10^9 \\le N \\le 10^9$).\n\n'
     '## Выход\nСтрока "even" или "odd".',
     [('4', 'even'), ('7', 'odd'), ('0', 'even'), ('-3', 'odd'), ('1000000000', 'even')], ['impl', 'num']),

    ('avg-two', 'Среднее арифметическое', '', 1, 1,
     'Даны два целых числа. Выведите их среднее арифметическое с 2 знаками после запятой.\n\n'
     '## Вход\nДва числа $A$ и $B$.\n\n## Выход\nСреднее арифметическое с 2 знаками.',
     [('4 6', '5.00'), ('1 2', '1.50'), ('0 0', '0.00'),
      ('-10 10', '0.00'), ('7 13', '10.00')], ['math']),

    ('abs-value', 'Модуль числа', '', 1, 1,
     'Дано целое число. Выведите его модуль $|N|$.\n\n'
     '## Вход\nОдно число $N$ ($-10^9 \\le N \\le 10^9$).\n\n## Выход\nМодуль числа.',
     [('-5', '5'), ('5', '5'), ('0', '0'), ('-1000000000', '1000000000'), ('42', '42')], ['math']),

    # ===== MEDIUM (2 points) =====
    ('sum-1n', 'Сумма от 1 до N', 'Формула $N(N+1)/2$', 1, 2,
     'Найдите сумму чисел $1 + 2 + \\ldots + N$.\n\n'
     '## Вход\nЦелое $N$ ($1 \\le N \\le 10^6$).\n\n## Выход\nСумма.',
     [('1', '1'), ('5', '15'), ('10', '55'), ('100', '5050'),
      ('1000000', '500000500000')], ['math']),

    ('factorial', 'Факториал', '$N!$', 1, 2,
     'Вычислите $N!$ (факториал). $N \\le 20$ чтобы влезло в 64-битное целое.\n\n'
     '## Вход\nЦелое $N$ ($0 \\le N \\le 20$).\n\n## Выход\nЗначение $N!$.',
     [('0', '1'), ('1', '1'), ('5', '120'), ('10', '3628800'),
      ('20', '2432902008176640000')], ['math', 'impl']),

    ('fibonacci', 'Фибоначчи', '$F_N$', 1, 2,
     'Последовательность Фибоначчи: $F_1 = F_2 = 1$, $F_n = F_{n-1} + F_{n-2}$. '
     'Выведите $F_N$. $N \\le 90$.\n\n'
     '## Вход\nЦелое $N$ ($1 \\le N \\le 90$).\n\n## Выход\nЗначение $F_N$.',
     [('1', '1'), ('2', '1'), ('10', '55'), ('30', '832040'),
      ('90', '2880067194370816120')], ['math', 'dp']),

    ('gcd', 'НОД', 'Алгоритм Евклида', 1, 2,
     'Найдите НОД двух натуральных чисел.\n\n'
     '## Вход\nДва числа $A$ и $B$ ($1 \\le A, B \\le 10^9$).\n\n## Выход\n$\\gcd(A, B)$.',
     [('12 18', '6'), ('7 5', '1'), ('100 50', '50'),
      ('999999999 3', '3'), ('1 1', '1')], ['num']),

    ('is-prime', 'Простое число', '', 2, 2,
     'Является ли $N$ простым? Выведите "yes" или "no".\n\n'
     '## Вход\nЦелое $N$ ($2 \\le N \\le 10^9$).\n\n## Выход\n"yes" или "no".',
     [('2', 'yes'), ('4', 'no'), ('17', 'yes'), ('1000000007', 'yes'),
      ('1000000008', 'no')], ['num']),

    ('digit-sum', 'Сумма цифр', '', 1, 2,
     'Найдите сумму цифр целого числа $N$ (для $N \\ge 0$).\n\n'
     '## Вход\n$N$ ($0 \\le N \\le 10^{18}$).\n\n## Выход\nСумма цифр.',
     [('12345', '15'), ('0', '0'), ('99', '18'), ('1000000000', '1'),
      ('999999999999999999', '162')], ['impl']),

    ('count-digits', 'Количество цифр', '', 1, 2,
     'Сколько цифр в десятичной записи числа $N$? (без знака минус)\n\n'
     '## Вход\n$N$ ($0 \\le |N| \\le 10^{18}$).\n\n## Выход\nКоличество цифр.',
     [('0', '1'), ('7', '1'), ('12345', '5'), ('-100', '3'),
      ('1000000000000000000', '19')], ['impl']),

    ('reverse-number', 'Обратное число', 'Перевернуть цифры', 1, 2,
     'Переверните цифры натурального числа. Ведущие нули игнорируются в результате.\n\n'
     '## Вход\n$N$ ($1 \\le N \\le 10^{18}$).\n\n## Выход\nЧисло с перевёрнутыми цифрами.',
     [('123', '321'), ('100', '1'), ('9', '9'), ('1000000000', '1'),
      ('987654321', '123456789')], ['impl']),

    ('power-ab', 'Степень $A^B$', 'Маленькие $A$, $B$', 1, 2,
     'Вычислите $A^B$. Гарантируется, что результат не превысит $10^{18}$.\n\n'
     '## Вход\nДва числа $A$ ($0 \\le A \\le 10^6$) и $B$ ($0 \\le B \\le 60$).\n\n## Выход\n$A^B$.',
     [('2 10', '1024'), ('5 0', '1'), ('1 100', '1'),
      ('10 15', '1000000000000000'), ('3 20', '3486784401')], ['math']),

    ('lcm', 'НОК', 'Наименьшее общее кратное', 1, 2,
     'Найдите НОК двух натуральных чисел.\n\n'
     '## Вход\n$A$ и $B$ ($1 \\le A, B \\le 10^6$). Результат влезает в $10^{12}$.\n\n## Выход\n$\\mathrm{lcm}(A, B)$.',
     [('4 6', '12'), ('3 5', '15'), ('100 200', '200'),
      ('999983 999979', '999961999657'), ('1 7', '7')], ['num']),

    ('sum-digits-n-times', 'Цифровой корень', 'Повторяем сумму цифр пока не останется одна', 1, 3,
     'Пока число имеет более одной цифры, заменяем его суммой его цифр. '
     'Выведите полученную одну цифру.\n\n'
     '## Вход\n$N$ ($0 \\le N \\le 10^{18}$).\n\n## Выход\nОднозначный цифровой корень.',
     [('38', '2'), ('0', '0'), ('9', '9'), ('999999999', '9'),
      ('123456789', '9')], ['math', 'impl']),

    ('divisors-count', 'Количество делителей', 'Посчитайте $\\tau(N)$', 2, 3,
     'Сколько положительных делителей у числа $N$?\n\n'
     '## Вход\n$N$ ($1 \\le N \\le 10^{12}$).\n\n## Выход\nКоличество делителей.',
     [('1', '1'), ('12', '6'), ('100', '9'), ('999999999999', '768'),
      ('1000000000000', '169')], ['num']),

    # ===== HARD (3-5 points) =====
    ('fast-power-mod', 'Быстрое возведение в степень', '$A^B \\bmod M$', 2, 4,
     'Вычислите $A^B \\bmod M$ с помощью быстрого возведения.\n\n'
     '## Вход\nТри числа $A$, $B$, $M$ ($0 \\le A, B \\le 10^{18}$, $1 \\le M \\le 10^9$).\n\n## Выход\nЗначение $A^B \\bmod M$.',
     [('2 10 1000', '24'), ('3 0 7', '1'), ('5 100 13', '1'),
      ('123456789 987654321 1000000007', '652541198'),
      ('1000000000000000000 1000000000000000000 999999937', '816769497')], ['math', 'num']),

    ('primes-upto-n', 'Простые до N', 'Решето Эратосфена', 2, 4,
     'Выведите все простые числа от 2 до $N$ включительно через пробел в одну строку.\n\n'
     '## Вход\n$N$ ($2 \\le N \\le 10^5$).\n\n## Выход\nПростые числа через пробел.',
     [('10', '2 3 5 7'), ('2', '2'), ('20', '2 3 5 7 11 13 17 19'),
      ('30', '2 3 5 7 11 13 17 19 23 29'),
      ('50', '2 3 5 7 11 13 17 19 23 29 31 37 41 43 47')], ['num']),

    ('fib-mod', 'Фибоначчи по модулю', 'Большой $N$', 2, 5,
     'Найдите $F_N \\bmod 10^9+7$. Здесь $N$ может быть до $10^{12}$ — нужно быстрое вычисление (матричное возведение или метод удвоения).\n\n'
     '## Вход\n$N$ ($1 \\le N \\le 10^{12}$).\n\n## Выход\n$F_N \\bmod (10^9+7)$.',
     [('1', '1'), ('10', '55'), ('100', '687995182'),
      ('1000000', '138351445'), ('1000000000000', '586268941')], ['math', 'dp']),
]


def main():
    from django.db import transaction
    ensure_types()
    group, _ = ProblemGroup.objects.get_or_create(name='Общие', defaults={'full_name': 'Общие задачи'})
    allowed_langs = Language.objects.filter(key__in=['C', 'CPP11', 'CPP14', 'CPP17', 'CPP20', 'PY3', 'JAVA8'])

    created_count = 0
    updated_count = 0
    with transaction.atomic():
        for tup in PROBLEMS:
            code, name, short, time_limit, points, description, tests, types_keys = tup
            # memory_limit default 256 MB
            p, created = upsert_problem(
                code=code, name=name, description=description,
                time_limit=time_limit, memory_limit=262144,
                points=points, tests=tests, group=group, types_keys=types_keys,
            )
            p.allowed_languages.set(allowed_langs)
            p.save()
            # Add to wsl-judge if exists
            j = Judge.objects.filter(name='wsl-judge').first()
            if j:
                j.problems.add(p)
            if created:
                created_count += 1
                print(f'[+] {code}: {name}')
            else:
                updated_count += 1
                print(f'[~] {code}: {name}')
    print(f'\nDone. Created: {created_count}, Updated: {updated_count}, Total: {len(PROBLEMS)}')


if __name__ == '__main__':
    main()
