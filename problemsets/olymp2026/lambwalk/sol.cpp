// For a weighted walk on a tree the expected time to cross edge (v, parent) from v is
// (2 * W_in + w) / w, where W_in is the total width inside the subtree of v (the walk is a reversible
// chain, a classic commute-time argument). From the parent into v it is (2 * (W_total - W_in) - w) / w.
// A query is the sum of the up-costs from s to lca(s, t) and the down-costs from lca to t: prefix sums.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 998244353;
ll pw(ll b, ll e) { ll r = 1; b %= MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }

int main() {
    int n, q;
    if (scanf("%d %d", &n, &q) != 2) return 0;
    vector<vector<pair<int, ll>>> g(n + 1);
    ll total = 0;
    for (int i = 0; i < n - 1; i++) {
        int u, v; ll w;
        scanf("%d %d %lld", &u, &v, &w);
        g[u].push_back({v, w}), g[v].push_back({u, w});
        total += w;
    }
    const int LOG = 18;
    vector<array<int, LOG>> up(n + 1);
    vector<int> dep(n + 1, 0), order;
    vector<ll> pw_(n + 1, 0), inside(n + 1, 0), U(n + 1, 0), D(n + 1, 0);
    vector<int> par(n + 1, 0);
    order.reserve(n);
    vector<int> st{1};
    par[1] = 0;
    vector<bool> seen(n + 1, false);
    seen[1] = true;
    while (!st.empty()) {
        int v = st.back(); st.pop_back();
        order.push_back(v);
        for (auto [c, w] : g[v]) if (!seen[c]) seen[c] = true, par[c] = v, pw_[c] = w, dep[c] = dep[v] + 1, st.push_back(c);
    }
    for (int i = n - 1; i > 0; i--) {
        int v = order[i];
        inside[par[v]] += inside[v] + pw_[v];
    }
    for (int i = 1; i < n; i++) {
        int v = order[i];
        ll w = pw_[v], iw = pw(w, MOD - 2);
        ll upc = (2 * (inside[v] % MOD) + w) % MOD * iw % MOD;
        ll downc = ((2 * ((total - inside[v]) % MOD) - w) % MOD + MOD) % MOD * iw % MOD;
        U[v] = (U[par[v]] + upc) % MOD;
        D[v] = (D[par[v]] + downc) % MOD;
    }
    for (int v = 1; v <= n; v++) up[v][0] = par[v] ? par[v] : v;
    for (int j = 1; j < LOG; j++)
        for (int i = 0; i < n; i++) { int v = order[i]; up[v][j] = up[up[v][j - 1]][j - 1]; }
    auto lca = [&](int a, int b) {
        if (dep[a] < dep[b]) swap(a, b);
        for (int j = LOG - 1; j >= 0; j--) if (dep[a] - (1 << j) >= dep[b]) a = up[a][j];
        if (a == b) return a;
        for (int j = LOG - 1; j >= 0; j--) if (up[a][j] != up[b][j]) a = up[a][j], b = up[b][j];
        return up[a][0];
    };
    while (q--) {
        int s, t;
        scanf("%d %d", &s, &t);
        int l = lca(s, t);
        ll ans = ((U[s] - U[l] + D[t] - D[l]) % MOD + 2 * MOD) % MOD;
        printf("%lld\n", ans);
    }
}
