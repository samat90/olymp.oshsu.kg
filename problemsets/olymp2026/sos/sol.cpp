// g[m] = number of masks containing m (superset sums, O(B 2^B)); h[m] = 2^g[m] - 1 subsets have AND
// containing m; Moebius inversion over supersets turns h into the counts of AND exactly m.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 1000000007;

int main() {
    int B, n, q;
    if (scanf("%d %d %d", &B, &n, &q) != 3) return 0;
    int S = 1 << B;
    vector<ll> g(S, 0);
    for (int i = 0; i < n; i++) { int x; scanf("%d", &x); g[x]++; }
    for (int b = 0; b < B; b++)
        for (int m = 0; m < S; m++)
            if (!(m >> b & 1)) g[m] += g[m | 1 << b];
    vector<ll> p2(n + 1, 1);
    for (int i = 1; i <= n; i++) p2[i] = p2[i - 1] * 2 % MOD;
    vector<ll> h(S);
    for (int m = 0; m < S; m++) h[m] = (p2[g[m]] - 1 + MOD) % MOD;
    for (int b = 0; b < B; b++)
        for (int m = 0; m < S; m++)
            if (!(m >> b & 1)) h[m] = (h[m] - h[m | 1 << b] + MOD) % MOD;
    while (q--) { int x; scanf("%d", &x); printf("%lld\n", h[x]); }
}
