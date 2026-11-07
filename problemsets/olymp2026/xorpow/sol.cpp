// Count codes, Walsh-Hadamard transform, raise every value to the power K (exponent reduced mod P-1,
// zero stays zero), inverse transform.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 998244353;
ll pw(ll b, ll e) { ll r = 1; b %= MOD; if (b < 0) b += MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }

void fwht(vector<ll> &a) {
    int n = a.size();
    for (int len = 1; len < n; len <<= 1)
        for (int i = 0; i < n; i += 2 * len)
            for (int j = i; j < i + len; j++) {
                ll u = a[j], v = a[j + len];
                a[j] = (u + v) % MOD, a[j + len] = (u - v + MOD) % MOD;
            }
}

int main() {
    int B, n, q;
    ll K;
    if (scanf("%d %d %lld %d", &B, &n, &K, &q) != 4) return 0;
    int S = 1 << B;
    vector<ll> c(S, 0);
    for (int i = 0; i < n; i++) { int x; scanf("%d", &x); c[x]++; }
    fwht(c);
    ll e = K % (MOD - 1);
    if (e == 0) e = MOD - 1;  // K >= 1: nonzero values give 1, zero gives 0
    for (auto &x : c) x = pw(x, e);
    fwht(c);
    ll inv = pw(S, MOD - 2);
    while (q--) {
        int x; scanf("%d", &x);
        printf("%lld\n", c[x] * inv % MOD);
    }
}
