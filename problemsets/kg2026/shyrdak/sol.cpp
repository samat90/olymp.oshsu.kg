// Burnside's lemma over rotations: answer = (1/n) * sum_{d|n} phi(n/d) * ((k-1)^d + (-1)^d (k-1)).
// n is factorised with Miller-Rabin + Pollard's rho. When P | n the sum is computed modulo P^2
// (P^2 > 10^18 >= n, so P divides n at most once) and divided exactly.
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long ull;
typedef __uint128_t u128;
const ull P = 1000000007ULL;

ull mulmod(ull a, ull b, ull m) { return (u128)a * b % m; }
ull powmod(ull a, ull e, ull m) {
    ull r = 1 % m; a %= m;
    while (e) { if (e & 1) r = mulmod(r, a, m); a = mulmod(a, a, m); e >>= 1; }
    return r;
}
bool isPrime(ull n) {
    if (n < 2) return false;
    for (ull p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}) { if (n % p == 0) return n == p; }
    ull d = n - 1; int s = 0;
    while (!(d & 1)) { d >>= 1; s++; }
    for (ull a : {2ULL, 325ULL, 9375ULL, 28178ULL, 450775ULL, 9780504ULL, 1795265022ULL}) {
        if (a % n == 0) continue;
        ull x = powmod(a % n, d, n);
        if (x == 1 || x == n - 1) continue;
        bool comp = true;
        for (int i = 1; i < s && comp; i++) { x = mulmod(x, x, n); if (x == n - 1) comp = false; }
        if (comp) return false;
    }
    return true;
}
mt19937_64 rng(12345);
ull rho(ull n) {
    if (n % 2 == 0) return 2;
    while (true) {
        ull c = rng() % (n - 1) + 1, x = 0, y = rng() % n, g = 1, q = 1, ys = 0;
        auto f = [&](ull v) { return (ull)(((u128)v * v + c) % n); };
        const int m = 128;
        for (int r = 1; g == 1; r <<= 1) {
            x = y;
            for (int i = 0; i < r; i++) y = f(y);
            for (int k = 0; k < r && g == 1; k += m) {
                ys = y;
                for (int i = 0; i < m && i < r - k; i++) { y = f(y); q = mulmod(q, x > y ? x - y : y - x, n); }
                g = __gcd(q, n);
            }
        }
        if (g == n) {
            do { ys = f(ys); g = __gcd(x > ys ? x - ys : ys - x, n); } while (g == 1);
        }
        if (g != n) return g;
    }
}
void factor(ull n, map<ull, int> &f) {
    if (n == 1) return;
    if (isPrime(n)) { f[n]++; return; }
    for (ull p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37})
        if (n % p == 0) { f[p]++; factor(n / p, f); return; }
    ull d = rho(n);
    factor(d, f); factor(n / d, f);
}

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ull n, k;
        if (scanf("%llu %llu", &n, &k) != 2) return 0;
        map<ull, int> fm;
        factor(n, fm);
        vector<pair<ull, int>> f(fm.begin(), fm.end());
        bool div = n % P == 0;
        ull M = div ? P * P : P;
        ull x = (k % M + M - 1) % M;  // k - 1 modulo M
        ull S = 0;
        // enumerate divisors d together with phi(n/d)
        // xd = x^d is carried along: x^(d*p) = (x^d)^p is cheap for the small primes of
        // numbers with many divisors.
        function<void(size_t, ull, ull, ull)> go = [&](size_t i, ull d, ull ph, ull xd) {
            if (i == f.size()) {
                ull term = xd;
                term = (d & 1) ? (term + M - x) % M : (term + x) % M;
                S = (S + mulmod(ph, term, M)) % M;
                return;
            }
            ull p = f[i].first; int a = f[i].second;
            ull pd = 1;
            for (int e = 0; e <= a; e++) {
                int r = a - e;  // exponent of p in n/d
                ull phr = 1;
                if (r > 0) { phr = (p - 1) % M; for (int t = 1; t < r; t++) phr = mulmod(phr, p % M, M); }
                go(i + 1, d * pd, mulmod(ph, phr, M), xd);
                if (e < a) { pd *= p; xd = powmod(xd, p, M); }
            }
        };
        go(0, 1, 1, x);
        ull ans;
        if (div) {
            ull s1 = S / P;  // S = n * answer is divisible by P
            ull m = n / P;
            ans = mulmod(s1 % P, powmod(m % P, P - 2, P), P);
        } else {
            ans = mulmod(S, powmod(n % P, P - 2, P), P);
        }
        printf("%llu\n", ans);
    }
}
