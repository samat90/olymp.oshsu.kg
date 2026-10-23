"""Independent reference answers and input-contract validation for the full archive."""
import bisect
import heapq
import math
import re
from collections import Counter
from itertools import accumulate, groupby

MOD = 1_000_000_007


def identify(problem):
    code, old = problem['code'], problem['description']
    if code == 'aplusb' or code.startswith('nn26-'):
        return code, {}
    group, raw = code.rsplit('-', 1)
    number = int(raw)
    params = {}
    families = {
        'str': ['length', 'reverse_string', 'vowels', 'consonants', 'uppercase', 'palindrome', 'frequent_char', 'deduplicate_string', 'words', 'rle'],
        'arr': ['array_sum', 'array_max', 'array_min', 'average', 'positive', 'even_count', 'second_max', 'reverse_array', 'prefix', 'distinct_count'],
        'sort': ['sort_asc', 'sort_desc', 'kth', 'median', 'inversions', 'sort_even', 'closest', 'mode', 'sort_unique', 'merge'],
        'nt': ['prime', 'divisor_count', 'divisor_sum', 'digit_sum', 'digit_count'],
        'geo': ['rectangle_area', 'rectangle_perimeter', 'triangle_area', 'distance', 'circle_area'],
        'greedy': ['coins', 'pieces', 'budget'],
        'impl': ['parity', 'leap', 'fizzbuzz', 'binary', 'reverse_number'],
        'comb': ['factorial', 'choose', 'arrangements', 'pascal', 'catalan'],
        'bs': ['find', 'lower_bound', 'at_least', 'isqrt', 'icbrt'],
    }
    if group in families:
        family = families[group][(number - 1) % len(families[group])]
    elif group == 'math':
        if number <= 18:
            family = ['sum_n', 'sum_squares', 'sum_cubes'][(number - 1) % 3]
            params['limit'] = int(re.search(r'N <= (\d+)', old).group(1))
        elif 21 <= number <= 40:
            family = 'mod_sum' if number <= 30 else 'mod_product'
            params['mod'] = int(re.search(r'при делении на (\d+)', old).group(1))
        elif 41 <= number <= 55:
            family = 'power'
            params['base'] = int(re.search(r'Вычислите (\d+)\^N', old).group(1))
        elif 56 <= number <= 63:
            family = 'fibonacci'
            params['limit'] = int(re.search(r'N <= (\d+)', old).group(1))
        elif 64 <= number <= 70:
            family = 'tribonacci'
        elif 71 <= number <= 85:
            family = 'gcd' if number % 2 else 'lcm'
        elif 86 <= number <= 100:
            family = ['abs_diff', 'min_three', 'median_three', 'sign'][(number - 86) % 4]
        else:
            raise ValueError(code)
    elif group == 'dp':
        if number <= 20:
            family = 'stairs'
            params['steps'] = [(1, 2), (1, 2, 3), (1, 3), (2, 3), (1, 2, 5)][(number - 1) // 4]
            params['limit'] = [20, 50, 100, 1000][(number - 1) % 4]
        elif number <= 30:
            family = 'max_subarray'
        else:
            raise ValueError(code)
    else:
        raise ValueError(code)
    return family, params


def fib(n):
    if n == 0:
        return 0, 1
    a, b = fib(n // 2)
    c, d = a * (2 * b - a) % MOD, (a * a + b * b) % MOD
    return (d, (c + d) % MOD) if n % 2 else (c, d)


def inversions(values):
    ranks = {v: i + 1 for i, v in enumerate(sorted(set(values)))}
    bit = [0] * (len(ranks) + 1)
    answer = 0
    for v in reversed(values):
        i = ranks[v] - 1
        while i:
            answer += bit[i]
            i -= i & -i
        i = ranks[v]
        while i < len(bit):
            bit[i] += 1
            i += i & -i
    return answer


def solve(f, p, raw):
    def bounded(values, lo, hi):
        assert all(lo <= v <= hi for v in values), (f, 'outside bounds', lo, hi)

    def ints(count=None):
        tokens = raw.split()
        assert all(re.fullmatch(r'-?\d+', x) for x in tokens), (f, 'integer tokens')
        values = list(map(int, tokens))
        if count is not None:
            assert len(values) == count, (f, 'wrong token count')
        return values

    strings = {'length', 'reverse_string', 'vowels', 'consonants', 'uppercase', 'palindrome', 'frequent_char', 'deduplicate_string', 'words', 'rle'}
    if f in strings:
        s = raw.rstrip('\r\n')
        assert '\n' not in s and '\r' not in s and 1 <= len(s) <= 1000
        assert re.fullmatch(r'[a-z ]+' if f == 'words' else r'[a-z]+', s)
        counts = Counter(s)
        answers = {
            'length': lambda: len(s), 'reverse_string': lambda: s[::-1],
            'vowels': lambda: sum(counts[x] for x in 'aeiou'),
            'consonants': lambda: sum(counts[x] for x in 'bcdfghjklmnpqrstvwxyz'),
            'uppercase': lambda: s.upper(), 'palindrome': lambda: 'YES' if s == s[::-1] else 'NO',
            'frequent_char': lambda: min(counts, key=lambda x: (-counts[x], x)),
            'deduplicate_string': lambda: ''.join(dict.fromkeys(s)),
            'words': lambda: len(s.split()),
            'rle': lambda: ''.join(k + str(sum(1 for _ in g)) for k, g in groupby(s)),
        }
        return str(answers[f]())

    if f == 'nn26-abiturients':
        lines = raw.strip().splitlines()
        n = int(lines[0]); assert 1 <= n <= 100000 and len(lines) == n + 1
        people = [line.split() for line in lines[1:]]
        assert all(len(row) == 2 and re.fullmatch(r'[A-Za-z]{1,30}', row[0]) and 0 <= int(row[1]) <= 100 for row in people)
        people.sort(key=lambda row: row[0], reverse=True)
        people.sort(key=lambda row: int(row[1]))
        return '\n'.join(' '.join(row) for row in people)

    a = ints()
    arrays = {'array_sum', 'array_max', 'array_min', 'average', 'positive', 'even_count', 'second_max', 'reverse_array', 'prefix', 'distinct_count', 'sort_asc', 'sort_desc', 'kth', 'median', 'inversions', 'sort_even', 'closest', 'mode', 'sort_unique', 'merge', 'budget', 'find', 'lower_bound', 'at_least', 'max_subarray', 'nn26-digitsort'}
    if f in arrays:
        n = a[0]; assert 1 <= n <= (1000 if f == 'inversions' else 100000)
        extra = f in {'kth', 'closest', 'merge', 'budget', 'find', 'lower_bound', 'at_least'}
        k = a[1] if extra else None
        values = a[2:] if extra else a[1:]
        if f == 'merge':
            assert 1 <= k <= 100000 and len(values) == n + k
            assert values[:n] == sorted(values[:n]) and values[n:] == sorted(values[n:])
        else:
            assert len(values) == n
        bounded(values, 1 if f in {'budget', 'nn26-digitsort'} else -10**9, 10**9)
        if f in {'kth', 'closest'}: assert 1 <= k <= n
        if f == 'budget': assert 0 <= k <= 10**14
        if f in {'find', 'lower_bound', 'at_least'}:
            assert values == sorted(values)
            bounded([k], -10**9, 10**9)
        if f == 'find': assert len(set(values)) == n
        if f == 'second_max': assert n >= 2 and len(set(values)) == n
        if f == 'array_sum': result = sum(values)
        elif f == 'array_max': result = max(values)
        elif f == 'array_min': result = min(values)
        elif f == 'average': result = f'{sum(values)/n:.6f}'
        elif f == 'positive': result = sum(v > 0 for v in values)
        elif f == 'even_count': result = sum(v % 2 == 0 for v in values)
        elif f == 'second_max': result = sorted(values)[-2]
        elif f == 'reverse_array': result = values[::-1]
        elif f == 'prefix': result = list(accumulate(values))
        elif f == 'distinct_count': result = len(set(values))
        elif f in {'sort_asc', 'merge'}: result = sorted(values)
        elif f == 'sort_desc': result = sorted(values, reverse=True)
        elif f == 'kth': result = sorted(values)[k-1]
        elif f == 'median': result = sorted(values)[(n-1)//2]
        elif f == 'inversions': result = inversions(values)
        elif f == 'sort_even': result = sorted(v for v in values if v % 2 == 0) or [0]
        elif f == 'closest': result = sorted(v for _, v in sorted(enumerate(values), key=lambda pair: (abs(pair[1]), pair[0]))[:k])
        elif f == 'mode':
            counts = Counter(values); result = min(counts, key=lambda x: (-counts[x], x))
        elif f == 'sort_unique': result = sorted(set(values))
        elif f == 'budget': result = bisect.bisect_right(list(accumulate(sorted(values))), k)
        elif f == 'find': result = bisect.bisect_left(values, k) + 1 if k in values else -1
        elif f == 'lower_bound':
            i = bisect.bisect_left(values, k); result = values[i] if i < n else 'NONE'
        elif f == 'at_least': result = n - bisect.bisect_left(values, k)
        elif f == 'max_subarray':
            low = 0; total = 0; result = -10**30
            for value in values:
                total += value; result = max(result, total-low); low = min(low, total)
        elif f == 'nn26-digitsort': result = sorted(values, key=lambda x: (sum(map(int, str(x))), -x))
        return ' '.join(map(str, result)) if isinstance(result, list) else str(result)

    if f == 'nn26-trails':
        n, m = a[:2]; assert 2 <= n <= 100000 and 0 <= m <= 200000 and len(a) == 2 + 3*m
        graph = [[] for _ in range(n)]
        for u, v, w in zip(a[2::3], a[3::3], a[4::3]):
            assert 1 <= u <= n and 1 <= v <= n and 1 <= w <= 10000
            graph[u-1].append((v-1,w)); graph[v-1].append((u-1,w))
        dist = [math.inf]*n; dist[0] = 0; queue = [(0,0)]
        while queue:
            d, u = heapq.heappop(queue)
            if d != dist[u]: continue
            for v, w in graph[u]:
                if d+w < dist[v]: dist[v] = d+w; heapq.heappush(queue,(d+w,v))
        return str(-1 if dist[-1] == math.inf else dist[-1])
    if f == 'nn26-pik-lenin':
        n, energy = a[:2]; assert 1 <= n <= 500 and 1 <= energy <= 5000 and len(a) == 2+2*n
        dp = [0]*(energy+1)
        for height, cost in zip(a[2::2],a[3::2]):
            assert 1 <= height <= 10000 and 0 <= cost <= 10000
            for used in range(energy,cost-1,-1): dp[used] = max(dp[used],dp[used-cost]+height)
        return str(dp[-1])

    if f in {'mod_sum', 'mod_product'}:
        n = a[0]; assert 1 <= n <= 1000 and len(a) == n+1
        bounded(a[1:], 0 if f == 'mod_sum' else 1, 10**9)
        return str((sum(a[1:]) if f == 'mod_sum' else math.prod(a[1:])) % p['mod'])

    counts = {'gcd':2,'lcm':2,'abs_diff':2,'aplusb':2,'min_three':3,'median_three':3,'rectangle_area':2,'rectangle_perimeter':2,'triangle_area':2,'distance':4,'pieces':2,'choose':2,'arrangements':2,'nn26-bells':2,'nn26-desks':3}
    assert len(a) == counts.get(f,1), (f, 'token count')
    n = a[0]
    ranges = {
        'sum_n':(1,p.get('limit',1)), 'sum_squares':(1,p.get('limit',1)), 'sum_cubes':(1,p.get('limit',1)),
        'power':(0,10**18),'fibonacci':(0,p.get('limit',1)),'tribonacci':(0,10**6),
        'gcd':(1,10**18),'lcm':(1,10**9),'abs_diff':(-10**9,10**9),'aplusb':(-10**9,10**9),
        'min_three':(-10**9,10**9),'median_three':(-10**9,10**9),'sign':(-10**9,10**9),
        'prime':(2,10**9),'divisor_count':(1,10**9),'divisor_sum':(1,10**9),
        'digit_sum':(0,10**18),'digit_count':(0,10**18),'rectangle_area':(1,10**9),
        'rectangle_perimeter':(1,10**9),'triangle_area':(1,10**9),'distance':(-10000,10000),
        'circle_area':(1,10000),'coins':(1,10**6),'pieces':(1,10**9),'stairs':(1,p.get('limit',1)),
        'parity':(-10**9,10**9),'leap':(1,10**9),'fizzbuzz':(1,10**6),
        'binary':(0,10**18),'reverse_number':(-10**18,10**18),'factorial':(0,10**6),
        'choose':(0,1000),'arrangements':(0,1000),'pascal':(0,30),'catalan':(0,1000),
        'isqrt':(0,10**18),'icbrt':(0,10**18),
    }
    if f in ranges: bounded(a,*ranges[f])
    if f == 'sum_n': result = n*(n+1)//2
    elif f == 'sum_squares': result = n*(n+1)*(2*n+1)//6
    elif f == 'sum_cubes': result = (n*(n+1)//2)**2
    elif f == 'power': result = pow(p['base'],n,MOD)
    elif f == 'fibonacci': result = fib(n)[0]
    elif f == 'tribonacci':
        x,y,z = 0,0,1
        for _ in range(n): x,y,z = y,z,(x+y+z)%MOD
        result = x
    elif f == 'gcd': result = math.gcd(*a)
    elif f == 'lcm': result = math.lcm(*a)
    elif f == 'abs_diff': result = abs(a[0]-a[1])
    elif f == 'aplusb': result = sum(a)
    elif f == 'min_three': result = min(a)
    elif f == 'median_three': result = sorted(a)[1]
    elif f == 'sign': result = (n>0)-(n<0)
    elif f == 'prime': result = 'YES' if all(n % d for d in range(2,math.isqrt(n)+1)) else 'NO'
    elif f in {'divisor_count','divisor_sum'}:
        divisors = set()
        for d in range(1,math.isqrt(n)+1):
            if n % d == 0: divisors.update((d,n//d))
        result = len(divisors) if f == 'divisor_count' else sum(divisors)
    elif f == 'digit_sum': result = sum(map(int,str(n)))
    elif f == 'digit_count': result = len(str(n))
    elif f == 'rectangle_area': result = math.prod(a)
    elif f == 'rectangle_perimeter': result = 2*sum(a)
    elif f == 'triangle_area':
        product=math.prod(a); result = str(product//2)+('.5' if product%2 else '.0')
    elif f == 'distance': result = f'{math.hypot(a[2]-a[0],a[3]-a[1]):.6f}'
    elif f == 'circle_area': result = f'{math.pi*n*n:.6f}'
    elif f == 'coins':
        result=0
        for coin in (25,10,5,1): q,n=divmod(n,coin); result+=q
    elif f == 'pieces': assert a[1]<=n; result=n//a[1]
    elif f == 'stairs':
        ways=[0]*(n+1); ways[0]=1
        for i in range(1,n+1): ways[i]=sum(ways[i-step] for step in p['steps'] if step<=i)%MOD
        result=ways[n]
    elif f == 'parity': result='Even' if n%2==0 else 'Odd'
    elif f == 'leap': result='YES' if n%400==0 or (n%4==0 and n%100!=0) else 'NO'
    elif f == 'fizzbuzz': result=('Fizz' if n%3==0 else '')+('Buzz' if n%5==0 else '') or str(n)
    elif f == 'binary': result=format(n,'b')
    elif f == 'reverse_number': result=int(str(abs(n))[::-1])*(-1 if n<0 else 1)
    elif f == 'factorial':
        result=1
        for i in range(2,n+1): result=result*i%MOD
    elif f in {'choose','arrangements'}:
        assert 0<=a[1]<=n
        result=(math.comb(n,a[1]) if f=='choose' else math.perm(n,a[1]))%MOD
    elif f == 'pascal': return ' '.join(str(math.comb(n,k)) for k in range(n+1))
    elif f == 'catalan': result=math.comb(2*n,n)//(n+1)%MOD
    elif f == 'isqrt': result=math.isqrt(n)
    elif f == 'icbrt':
        lo,hi=0,10**6+1
        while hi-lo>1:
            mid=(lo+hi)//2
            if mid**3<=n: lo=mid
            else: hi=mid
        result=lo
    elif f == 'nn26-bells':
        assert 0<=n<=23 and 0<=a[1]<=59
        result=max(0,(n*60+a[1]-480)//90+1)
    elif f == 'nn26-desks':
        desks,students,teachers=a
        assert 1<=desks<=10**9 and 0<=students<=2*10**9 and 0<=teachers<=desks
        result=max(0,desks-teachers-(students+1)//2)
    else: raise ValueError(f)
    return str(result)
