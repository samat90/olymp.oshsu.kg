// Pruefer code: vertex 1 occurs d - 1 times, the c leaves do not occur, every other vertex occurs at least once.
// Choose the positions of vertex 1: C(n-2, d-1); choose the non-leaves among vertices 2..n: C(n-1, K) with
// K = n - c (d = 1, vertex 1 is a leaf) or K = n - 1 - c (d > 1); fill the other L = n-1-d positions with
// all K of them: surjections = sum_j (-1)^j C(K, j) (K - j)^L. Powers i^L come from a sieve (multiplicative).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 1000000007;
ll pw(ll b, ll e) { ll r = 1; b %= MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    const int MX = 1000005;
    vector<ll> f(MX), fi(MX);
    f[0] = 1;
    for (int i = 1; i < MX; i++) f[i] = f[i - 1] * i % MOD;
    fi[MX - 1] = pw(f[MX - 1], MOD - 2);
    for (int i = MX - 1; i > 0; i--) fi[i - 1] = fi[i] * i % MOD;
    auto C = [&](ll n, ll k) -> ll { return k < 0 || k > n || n < 0 ? 0 : f[n] * fi[k] % MOD * fi[n - k] % MOD; };
    while (T--) {
        ll n, c, d;
        scanf("%lld %lld %lld", &n, &c, &d);
        ll K = d == 1 ? n - c : n - 1 - c, L = n - 1 - d;
        if (K < 0 || L < 0 || K > L || (K == 0 && L > 0)) { puts("0"); continue; }
        // i^L for i = 0..K
        vector<ll> pv(K + 1, 0);
        vector<int> primes;
        vector<char> comp(K + 1, 0);
        if (K >= 0) pv[0] = L == 0 ? 1 : 0;
        if (K >= 1) pv[1] = 1;
        for (ll i = 2; i <= K; i++) {
            if (!comp[i]) primes.push_back(i), pv[i] = pw(i, L);
            for (int p : primes) {
                if (i * p > K) break;
                comp[i * p] = 1;
                pv[i * p] = pv[i] * pv[p] % MOD;
                if (i % p == 0) break;
            }
        }
        ll surj = 0;
        for (ll j = 0; j <= K; j++) {
            ll term = C(K, j) * pv[K - j] % MOD;
            surj = (j & 1) ? (surj - term + MOD) % MOD : (surj + term) % MOD;
        }
        printf("%lld\n", C(n - 2, d - 1) * C(n - 1, K) % MOD * surj % MOD);
    }
}
