// Maximum weight closure: source -> i with capacity p[i] > 0, i -> sink with -p[i] for p[i] < 0,
// a -> b with infinite capacity. Answer = sum of positive profits - minimum cut (Dinic).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
struct E { int to; ll cap; };
vector<E> es;
vector<vector<int>> g;
vector<int> lvl, it;
void add(int a, int b, ll c) {
    g[a].push_back(es.size()); es.push_back({b, c});
    g[b].push_back(es.size()); es.push_back({a, 0});
}
bool bfs(int s, int t) {
    fill(lvl.begin(), lvl.end(), -1);
    queue<int> q; q.push(s); lvl[s] = 0;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int id : g[u]) if (es[id].cap > 0 && lvl[es[id].to] < 0) lvl[es[id].to] = lvl[u] + 1, q.push(es[id].to);
    }
    return lvl[t] >= 0;
}
ll dfs(int u, int t, ll f) {
    if (u == t) return f;
    for (int &i = it[u]; i < (int)g[u].size(); i++) {
        int id = g[u][i], v = es[id].to;
        if (es[id].cap > 0 && lvl[v] == lvl[u] + 1) {
            ll d = dfs(v, t, min(f, es[id].cap));
            if (d > 0) { es[id].cap -= d; es[id ^ 1].cap += d; return d; }
        }
    }
    return 0;
}
int main() {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    int s = n, t = n + 1;
    g.assign(n + 2, {}); lvl.assign(n + 2, 0); it.assign(n + 2, 0);
    ll pos = 0;
    for (int i = 0; i < n; i++) {
        ll p; scanf("%lld", &p);
        if (p > 0) add(s, i, p), pos += p;
        else if (p < 0) add(i, t, -p);
    }
    const ll INF = (ll)4e18;
    for (int i = 0; i < m; i++) { int a, b; scanf("%d %d", &a, &b); add(a - 1, b - 1, INF); }
    ll flow = 0;
    while (bfs(s, t)) {
        fill(it.begin(), it.end(), 0);
        while (ll f = dfs(s, t, INF)) flow += f;
    }
    printf("%lld\n", pos - flow);
}
