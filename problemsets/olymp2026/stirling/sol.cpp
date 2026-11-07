// S(n, k) = sum_j  j^n / j!  *  (-1)^(k-j) / (k-j)!  -- one convolution (NTT mod 998244353).
// j^n for j <= K < P: the exponent is reduced mod P-1, computed by a linear sieve (completely multiplicative).
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
                a[i + j] = (u + v) % MOD, a[i + j + len / 2] = (u - v + MOD) % MOD;
                wn = wn * w % MOD;
            }
        }
    }
    if (inv) { ll ni = pw(n, MOD - 2); for (auto &x : a) x = x * ni % MOD; }
}
int main() {
    ll n; int K;
    if (scanf("%lld %d", &n, &K) != 2) return 0;
    ll e = n % (MOD - 1);
    if (e == 0) e = MOD - 1;  // n >= 1, j >= 1
    vector<ll> f(K + 1), fi(K + 1), pv(K + 1, 0);
    f[0] = 1;
    for (int i = 1; i <= K; i++) f[i] = f[i - 1] * i % MOD;
    fi[K] = pw(f[K], MOD - 2);
    for (int i = K; i > 0; i--) fi[i - 1] = fi[i] * i % MOD;
    vector<int> primes;
    vector<char> comp(K + 1, 0);
    if (K >= 1) pv[1] = 1;
    for (int i = 2; i <= K; i++) {
        if (!comp[i]) primes.push_back(i), pv[i] = pw(i, e);
        for (int p : primes) {
            if ((ll)i * p > K) break;
            comp[i * p] = 1;
            pv[i * p] = pv[i] * pv[p] % MOD;
            if (i % p == 0) break;
        }
    }
    int sz = 1;
    while (sz < 2 * (K + 1)) sz <<= 1;
    vector<ll> A(sz, 0), B(sz, 0);
    for (int j = 0; j <= K; j++) {
        A[j] = pv[j] * fi[j] % MOD;
        B[j] = (j & 1) ? (MOD - fi[j]) % MOD : fi[j];
    }
    ntt(A, false), ntt(B, false);
    for (int i = 0; i < sz; i++) A[i] = A[i] * B[i] % MOD;
    ntt(A, true);
    for (int k = 1; k <= K; k++) printf("%lld%c", A[k], k == K ? '\n' : ' ');
}
