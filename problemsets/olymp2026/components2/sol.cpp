// In a forest C = V - E (lit vertices minus lit edges), so E[C^2] = E[V^2] - 2 E[VE] + E[E^2].
// Each term is a sum over pairs of indicators; pairs that share vertices are corrected separately:
// E[V^2] = S^2 - S2 + S, E[VE] = sum_e q_e (2 + S - p_u - p_v),
// E[E^2] = Q^2 + sum_e (q_e - q_e^2) + sum_u (p_u - p_u^2)(A_u^2 - B_u), A_u, B_u = sums of p, p^2 over neighbours.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 998244353;
ll pw(ll b, ll e) { ll r = 1; b %= MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    ll inv100 = pw(100, MOD - 2);
    vector<ll> p(n + 1), A(n + 1, 0), B(n + 1, 0);
    ll S = 0, S2 = 0;
    for (int i = 1; i <= n; i++) {
        ll x; scanf("%lld", &x);
        p[i] = x * inv100 % MOD;
        S = (S + p[i]) % MOD, S2 = (S2 + p[i] * p[i]) % MOD;
    }
    ll V2 = ((S * S - S2 + S) % MOD + MOD) % MOD;
    ll VE = 0, Q = 0, corr = 0;
    for (int i = 0; i < n - 1; i++) {
        int u, v; scanf("%d %d", &u, &v);
        ll qe = p[u] * p[v] % MOD;
        VE = (VE + qe * ((2 + S - p[u] - p[v]) % MOD + MOD)) % MOD;
        Q = (Q + qe) % MOD;
        corr = (corr + qe - qe * qe % MOD + MOD) % MOD;
        A[u] = (A[u] + p[v]) % MOD, A[v] = (A[v] + p[u]) % MOD;
        B[u] = (B[u] + p[v] * p[v]) % MOD, B[v] = (B[v] + p[u] * p[u]) % MOD;
    }
    ll E2 = (Q * Q + corr) % MOD;
    for (int u = 1; u <= n; u++) {
        ll a = (p[u] - p[u] * p[u] % MOD + MOD) % MOD;
        ll b = (A[u] * A[u] - B[u] + MOD) % MOD;
        E2 = (E2 + a * b) % MOD;
    }
    printf("%lld\n", ((V2 - 2 * VE + E2) % MOD + 2 * MOD) % MOD);
}
