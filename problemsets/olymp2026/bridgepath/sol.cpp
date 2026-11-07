// Bridges by an iterative DFS with edge ids (parallel edges are not bridges); 2-edge-connected components
// are contracted into a tree; the answer is the tree distance: depth[u] + depth[v] - 2 depth[lca].
#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, m, q;
    if (scanf("%d %d %d", &n, &m, &q) != 3) return 0;
    vector<vector<pair<int, int>>> g(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b;
        scanf("%d %d", &a, &b);
        g[a].push_back({b, i}), g[b].push_back({a, i});
    }
    vector<int> tin(n + 1, -1), low(n + 1), it(n + 1, 0), pe(n + 1, -1);
    vector<bool> bridge(m, false);
    int timer = 0;
    for (int s = 1; s <= n; s++) {
        if (tin[s] >= 0) continue;
        vector<int> st{s};
        tin[s] = low[s] = timer++;
        while (!st.empty()) {
            int v = st.back();
            if (it[v] < (int)g[v].size()) {
                auto [u, id] = g[v][it[v]++];
                if (id == pe[v]) continue;
                if (tin[u] < 0) { pe[u] = id; tin[u] = low[u] = timer++; st.push_back(u); }
                else low[v] = min(low[v], tin[u]);
            } else {
                st.pop_back();
                if (!st.empty()) {
                    int p = st.back();
                    low[p] = min(low[p], low[v]);
                    if (low[v] > tin[p]) bridge[pe[v]] = true;
                }
            }
        }
    }
    vector<int> comp(n + 1, -1);
    int C = 0;
    for (int s = 1; s <= n; s++) {
        if (comp[s] >= 0) continue;
        vector<int> st{s};
        comp[s] = C;
        while (!st.empty()) {
            int v = st.back(); st.pop_back();
            for (auto [u, id] : g[v]) if (!bridge[id] && comp[u] < 0) comp[u] = C, st.push_back(u);
        }
        C++;
    }
    vector<vector<int>> t(C);
    for (int v = 1; v <= n; v++)
        for (auto [u, id] : g[v]) if (bridge[id]) t[comp[v]].push_back(comp[u]);
    const int LOG = 18;
    vector<array<int, LOG>> up(C);
    vector<int> dep(C, 0), order;
    vector<bool> seen(C, false);
    vector<int> st{0};
    seen[0] = true;
    up[0][0] = 0;
    while (!st.empty()) {
        int v = st.back(); st.pop_back();
        order.push_back(v);
        for (int u : t[v]) if (!seen[u]) seen[u] = true, up[u][0] = v, dep[u] = dep[v] + 1, st.push_back(u);
    }
    for (int j = 1; j < LOG; j++) for (int v : order) up[v][j] = up[up[v][j - 1]][j - 1];
    auto lca = [&](int a, int b) {
        if (dep[a] < dep[b]) swap(a, b);
        for (int j = LOG - 1; j >= 0; j--) if (dep[a] - (1 << j) >= dep[b]) a = up[a][j];
        if (a == b) return a;
        for (int j = LOG - 1; j >= 0; j--) if (up[a][j] != up[b][j]) a = up[a][j], b = up[b][j];
        return up[a][0];
    };
    while (q--) {
        int u, v;
        scanf("%d %d", &u, &v);
        int a = comp[u], b = comp[v];
        printf("%d\n", dep[a] + dep[b] - 2 * dep[lca(a, b)]);
    }
}
