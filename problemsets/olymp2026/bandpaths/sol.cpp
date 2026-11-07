// Two absorbing walls at -1 and h+1: by repeated reflections (period 2(h+2)) the count is
// sum_j [ P(a -> b + 2j(h+2)) - P(a -> -2 - b + 2j(h+2)) ], P(a -> c) = C(N, (N + c - a) / 2).
// Only O(N / h) terms are non-zero.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 1000000007;
const int MX = 1000005;
ll f[MX], fi[MX];
ll pw(ll b, ll e) { ll r = 1; b %= MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }
ll paths(ll N, ll d) {  // walks of N steps with total displacement d
    if ((N + d) % 2 != 0 || d > N || d < -N) return 0;
    ll up = (N + d) / 2;
    return f[N] * fi[up] % MOD * fi[N - up] % MOD;
}
int main() {
    f[0] = 1;
    for (int i = 1; i < MX; i++) f[i] = f[i - 1] * i % MOD;
    fi[MX - 1] = pw(f[MX - 1], MOD - 2);
    for (int i = MX - 1; i > 0; i--) fi[i - 1] = fi[i] * i % MOD;
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ll N, h, a, b;
        scanf("%lld %lld %lld %lld", &N, &h, &a, &b);
        ll per = 2 * (h + 2), res = 0;
        // terms with |displacement| <= N
        ll jlo = (-N - (b - a)) / per - 1, jhi = (N - (b - a)) / per + 1;
        for (ll j = jlo; j <= jhi; j++) res += paths(N, b + j * per - a);
        jlo = (-N - (-2 - b - a)) / per - 1, jhi = (N - (-2 - b - a)) / per + 1;
        for (ll j = jlo; j <= jhi; j++) res -= paths(N, -2 - b + j * per - a);
        res %= MOD;
        if (res < 0) res += MOD;
        printf("%lld\n", res);
    }
}
