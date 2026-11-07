// Count solutions modulo every prime power p^e of m (CRT multiplies the counts); m is factored by
// Miller-Rabin + Pollard rho. For a = p^k u (u a unit, k < e): k must be even, x = p^(k/2) y,
// y^2 = u (mod p^(e-k)); a unit has 0 or 2 roots for odd p, and for p = 2: 1, 0/2, 0/4 roots
// (f = 1, 2, >= 3). Each root lifts to p^(k/2) values of x. For a = 0 mod p^e there are p^floor(e/2).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef unsigned long long ull;
typedef __uint128_t u128;

ull mulmod(ull a, ull b, ull m) { return (u128)a * b % m; }
ull powmod(ull b, ull e, ull m) { ull r = 1 % m; b %= m; for (; e; e >>= 1, b = mulmod(b, b, m)) if (e & 1) r = mulmod(r, b, m); return r; }
bool isPrime(ull n) {
    if (n < 2) return false;
    for (ull p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}) if (n % p == 0) return n == p;
    ull d = n - 1; int r = 0;
    while (d % 2 == 0) d /= 2, r++;
    for (ull a : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37}) {
        ull x = powmod(a, d, n);
        if (x == 1 || x == n - 1) continue;
        bool ok = false;
        for (int i = 1; i < r; i++) { x = mulmod(x, x, n); if (x == n - 1) { ok = true; break; } }
        if (!ok) return false;
    }
    return true;
}
mt19937_64 rng(12345);
ull rho(ull n) {
    if (n % 2 == 0) return 2;
    while (true) {
        ull x = rng() % n, y = x, c = rng() % (n - 1) + 1, d = 1;
        auto f = [&](ull v) { return (mulmod(v, v, n) + c) % n; };
        while (d == 1) {
            ull q = 1, xs = x, ys = y;
            for (int i = 0; i < 64 && d == 1; i++) {
                x = f(x); y = f(f(y));
                q = mulmod(q, x > y ? x - y : y - x, n);
                if (q == 0) break;
            }
            d = __gcd(q, n);
            if (d == n || q == 0) {  // backtrack one step at a time
                x = xs, y = ys, d = 1;
                do { x = f(x); y = f(f(y)); d = __gcd(x > y ? x - y : y - x, n); } while (d == 1);
            }
        }
        if (d != n) return d;
    }
}
void factor(ull n, map<ull, int> &f) {
    if (n == 1) return;
    for (ull p : {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37})
        if (n % p == 0) { while (n % p == 0) n /= p, f[p]++; factor(n, f); return; }
    if (isPrime(n)) { f[n]++; return; }
    ull d = rho(n);
    factor(d, f), factor(n / d, f);
}

ull countPP(ull p, int e, ull a) {
    ull pe = 1;
    for (int i = 0; i < e; i++) pe *= p;
    a %= pe;
    auto ppow = [&](int t) { ull r = 1; while (t--) r *= p; return r; };
    if (a == 0) return ppow(e / 2);
    int k = 0;
    while (a % p == 0) a /= p, k++;
    if (k % 2) return 0;
    int f = e - k;
    ull base;
    if (p == 2) base = f == 1 ? 1 : (f == 2 ? (a % 4 == 1 ? 2 : 0) : (a % 8 == 1 ? 4 : 0));
    else base = powmod(a % p, (p - 1) / 2, p) == 1 ? 2 : 0;
    return base * ppow(k / 2);
}

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ull a, m;
        scanf("%llu %llu", &a, &m);
        map<ull, int> f;
        factor(m, f);
        ull res = 1;
        for (auto [p, e] : f) { res *= countPP(p, e, a); if (!res) break; }
        printf("%llu\n", res);
    }
}
