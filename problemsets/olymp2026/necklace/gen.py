"""gen.py T maxN maxK mode(small/rand/smooth/prime/pow2) seed"""
import random
import sys

T, N, K, mode, s = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
random.seed(s * 313 + T)


def is_prime(v):
    if v < 2:
        return False
    i = 2
    while i * i <= v:
        if v % i == 0:
            return False
        i += 1
    return True


out = []
for _ in range(T):
    if mode == 'small':
        n, k = random.randint(3, N), random.randint(1, K)
    else:
        if mode == 'smooth':  # many divisors
            n = 1
            while True:
                p = random.choice([2, 2, 2, 3, 3, 5, 7, 11, 13])
                if n * p > N:
                    break
                n *= p
            n = max(3, n)
        elif mode == 'prime':
            n = random.randint(N // 2, N)
            while not is_prime(n):
                n -= 1
        elif mode == 'pow2':
            n = 1 << random.randint(2, N.bit_length() - 1)
            if random.random() < 0.3:
                n = n // 2 * 3 if n // 2 * 3 <= N else n
        else:
            n = random.randint(3, N)
        k = random.randint(1, K) if random.random() < 0.85 else random.choice([1, 2, 3, K])
    out.append('%d %d' % (n, k))
print(T)
print('\n'.join(out))
