// Each die is a polynomial sum_j x^v / k. Multiply all of them by divide and conquer with NTT
// (the total degree is at most 2e5), then answer the queries with prefix sums.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 998244353, G = 3;
ll pw(ll b, ll e) { ll r = 1; b %= MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }

void ntt(vector<ll> &a, bool inv) {
    int n = a.size();
    for (int i = 1, j = 0; i < n; i++) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) swap(a[i], a[j]);
    }
    for (int len = 2; len <= n; len <<= 1) {
        ll w = pw(G, (MOD - 1) / len);
        if (inv) w = pw(w, MOD - 2);
        for (int i = 0; i < n; i += len) {
            ll wn = 1;
            for (int j = 0; j < len / 2; j++) {
                ll u = a[i + j], v = a[i + j + len / 2] * wn % MOD;
                a[i + j] = u + v < MOD ? u + v : u + v - MOD;
                a[i + j + len / 2] = u - v >= 0 ? u - v : u - v + MOD;
                wn = wn * w % MOD;
            }
        }
    }
    if (inv) { ll ni = pw(n, MOD - 2); for (auto &x : a) x = x * ni % MOD; }
}

vector<ll> mul(vector<ll> a, vector<ll> b) {
    int need = a.size() + b.size() - 1;
    if (min(a.size(), b.size()) <= 32) {
        vector<ll> c(need, 0);
        for (size_t i = 0; i < a.size(); i++) if (a[i]) for (size_t j = 0; j < b.size(); j++) c[i + j] = (c[i + j] + a[i] * b[j]) % MOD;
        return c;
    }
    int n = 1;
    while (n < need) n <<= 1;
    a.resize(n), b.resize(n);
    ntt(a, false), ntt(b, false);
    for (int i = 0; i < n; i++) a[i] = a[i] * b[i] % MOD;
    ntt(a, true);
    a.resize(need);
    return a;
}

vector<vector<ll>> polys;
vector<ll> prod(int l, int r) {
    if (r - l == 1) return polys[l];
    int m = (l + r) / 2;
    return mul(prod(l, m), prod(m, r));
}

int main() {
    int n, q;
    if (scanf("%d %d", &n, &q) != 2) return 0;
    polys.resize(n);
    for (int i = 0; i < n; i++) {
        int k; scanf("%d", &k);
        vector<int> v(k);
        int mx = 0;
        for (auto &x : v) scanf("%d", &x), mx = max(mx, x);
        vector<ll> p(mx + 1, 0);
        ll ik = pw(k, MOD - 2);
        for (int x : v) p[x] = (p[x] + ik) % MOD;
        polys[i] = p;
    }
    vector<ll> res = prod(0, n);
    vector<ll> pre(res.size() + 1, 0);
    for (size_t i = 0; i < res.size(); i++) pre[i + 1] = (pre[i] + res[i]) % MOD;
    ll S = res.size();
    while (q--) {
        ll l, r;
        scanf("%lld %lld", &l, &r);
        l = min(l, S), r = min(r + 1, S);
        printf("%lld\n", l >= r ? 0 : (pre[r] - pre[l] + MOD) % MOD);
    }
}
