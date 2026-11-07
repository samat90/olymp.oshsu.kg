// BEST theorem. Every circuit is counted once when it starts with road 1, so the answer is
// t_w * prod (outdeg(v) - 1)! when every vertex has indeg = outdeg and the roads are connected, else 0.
// t_w: arborescences towards w = minor of D_out - A over the vertices that have roads (Kirchhoff).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 1000000007;

ll pw(ll b, ll e) { ll r = 1; b %= MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }

ll det(vector<vector<ll>> a) {
    int n = a.size();
    ll res = 1;
    for (int c = 0; c < n; c++) {
        int p = -1;
        for (int r = c; r < n; r++) if (a[r][c]) { p = r; break; }
        if (p < 0) return 0;
        if (p != c) swap(a[p], a[c]), res = MOD - res;
        res = res * a[c][c] % MOD;
        ll inv = pw(a[c][c], MOD - 2);
        for (int r = c + 1; r < n; r++) {
            if (!a[r][c]) continue;
            ll f = a[r][c] * inv % MOD;
            for (int k = c; k < n; k++) a[r][k] = ((a[r][k] - f * a[c][k]) % MOD + MOD) % MOD;
        }
    }
    return res % MOD;
}

int main() {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    vector<int> a(m), b(m), in(n + 1), out(n + 1);
    vector<vector<ll>> A(n + 1, vector<ll>(n + 1, 0));
    for (int i = 0; i < m; i++) {
        scanf("%d %d", &a[i], &b[i]);
        out[a[i]]++, in[b[i]]++;
        A[a[i]][b[i]]++;
    }
    for (int v = 1; v <= n; v++)
        if (in[v] != out[v]) { puts("0"); return 0; }
    int w = a[0];
    vector<int> vs;  // vertices with roads, except w
    for (int v = 1; v <= n; v++) if (out[v] && v != w) vs.push_back(v);
    int s = vs.size();
    vector<vector<ll>> L(s, vector<ll>(s, 0));
    for (int i = 0; i < s; i++)
        for (int j = 0; j < s; j++) {
            ll v = (i == j ? out[vs[i]] : 0) - A[vs[i]][vs[j]];
            L[i][j] = ((v % MOD) + MOD) % MOD;
        }
    ll ans = det(L);
    vector<ll> fact(m + 1, 1);
    for (int i = 1; i <= m; i++) fact[i] = fact[i - 1] * i % MOD;
    for (int v = 1; v <= n; v++) if (out[v]) ans = ans * fact[out[v] - 1] % MOD;
    printf("%lld\n", ans);
}
