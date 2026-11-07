// Berlekamp-Massey finds the shortest recurrence (length L <= k); then a[N] = sum r_i a[i], where
// x^N mod (characteristic polynomial) = sum r_i x^i, computed by binary powering of polynomials mod P(x).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 998244353;
ll pw(ll b, ll e) { ll r = 1; b %= MOD; if (b < 0) b += MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }

vector<ll> berlekamp(const vector<ll> &s) {
    int n = s.size(), L = 0, m = 0;
    vector<ll> C(n + 1, 0), B(n + 1, 0), T;
    C[0] = B[0] = 1;
    ll b = 1;
    for (int i = 0; i < n; i++) {
        ++m;
        ll d = s[i] % MOD;
        for (int j = 1; j <= L; j++) d = (d + C[j] * s[i - j]) % MOD;
        if (!d) continue;
        T = C;
        ll coef = d * pw(b, MOD - 2) % MOD;
        for (int j = m; j <= n; j++) C[j] = ((C[j] - coef * B[j - m]) % MOD + MOD) % MOD;
        if (2 * L > i) continue;
        L = i + 1 - L, B = T, b = d, m = 0;
    }
    vector<ll> c(L);  // a[i] = sum c[j] a[i-1-j]
    for (int j = 0; j < L; j++) c[j] = (MOD - C[j + 1]) % MOD;
    return c;
}

int main() {
    int k;
    ll N;
    if (scanf("%d %lld", &k, &N) != 2) return 0;
    vector<ll> a(2 * k);
    for (auto &x : a) scanf("%lld", &x);
    vector<ll> c = berlekamp(a);
    int L = c.size();
    if (N < 2 * k) { printf("%lld\n", a[N]); return 0; }
    if (L == 0) { puts("0"); return 0; }
    // multiply two polynomials of degree < L modulo x^L - c[0] x^(L-1) - ... - c[L-1]
    auto mulmod = [&](const vector<ll> &p, const vector<ll> &q) {
        vector<ll> r(2 * L - 1, 0);
        for (int i = 0; i < L; i++) if (p[i]) for (int j = 0; j < L; j++) r[i + j] = (r[i + j] + p[i] * q[j]) % MOD;
        for (int i = 2 * L - 2; i >= L; i--) {
            if (!r[i]) continue;
            for (int j = 0; j < L; j++) r[i - 1 - j] = (r[i - 1 - j] + r[i] * c[j]) % MOD;
        }
        r.resize(L);
        return r;
    };
    vector<ll> res(L, 0), base(L, 0);
    res[0] = 1;
    if (L == 1) base[0] = c[0]; else base[1] = 1;
    for (ll e = N; e; e >>= 1) {
        if (e & 1) res = mulmod(res, base);
        base = mulmod(base, base);
    }
    ll ans = 0;
    for (int i = 0; i < L; i++) ans = (ans + res[i] * a[i]) % MOD;
    printf("%lld\n", ans);
}
