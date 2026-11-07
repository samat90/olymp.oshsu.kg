// conn(S) = 1 - sum over proper subsets T of S containing the lowest vertex of S:
//           conn(T) * P(no surviving road between T and S \ T).
// P(no road inside X) = fail(X); the cut probability is fail(S) / (fail(T) fail(S \ T)).
// Probabilities can be exactly 0 (p = 100), so every value is kept as (number of zero factors, the rest).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 998244353;
ll pw(ll b, ll e) { ll r = 1; b %= MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }

int main() {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    ll inv100 = pw(100, MOD - 2);
    // per pair: zero count and product of nonzero failure probabilities
    vector<vector<int>> pz(n, vector<int>(n, 0));
    vector<vector<ll>> pv(n, vector<ll>(n, 1));
    for (int i = 0; i < m; i++) {
        int u, v, p;
        scanf("%d %d %d", &u, &v, &p);
        u--, v--;
        ll q = (100 - p) * inv100 % MOD;
        if (q == 0) pz[u][v]++, pz[v][u]++;
        else pv[u][v] = pv[u][v] * q % MOD, pv[v][u] = pv[v][u] * q % MOD;
    }
    int N = 1 << n;
    vector<int> fz(N, 0), fz2;
    vector<ll> fv(N, 1);
    for (int S = 1; S < N; S++) {
        int v = __builtin_ctz(S), R = S & (S - 1);
        fz[S] = fz[R], fv[S] = fv[R];
        for (int u = 0; u < n; u++)
            if (R >> u & 1) fz[S] += pz[v][u], fv[S] = fv[S] * pv[v][u] % MOD;
    }
    vector<ll> ifv(N);
    for (int S = 0; S < N; S++) ifv[S] = pw(fv[S], MOD - 2);
    vector<ll> conn(N, 0);
    for (int S = 1; S < N; S++) {
        int low = S & -S, rest = S ^ low;
        ll sum = 0;
        // T = low | sub, sub a proper subset of rest
        for (int sub = (rest - 1) & rest;; sub = (sub - 1) & rest) {
            int T = low | sub, U = S ^ T;
            if (fz[S] == fz[T] + fz[U])
                sum = (sum + conn[T] * (fv[S] * ifv[T] % MOD * ifv[U] % MOD)) % MOD;
            if (sub == 0) break;
        }
        if (rest == 0) sum = 0;
        conn[S] = (1 - sum + MOD) % MOD;
    }
    printf("%lld\n", conn[N - 1]);
}
