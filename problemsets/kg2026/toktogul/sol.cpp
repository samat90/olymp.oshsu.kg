// Min-cost flow with lower bounds: reduce to a circulation with a super source/sink,
// then successive shortest paths (Dijkstra with potentials, all costs are non-negative).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll INF = LLONG_MAX / 4;

struct E { int to; ll cap, cost; };
vector<E> es;
vector<vector<int>> g;
void addEdge(int u, int v, ll cap, ll cost) {
    g[u].push_back(es.size()); es.push_back({v, cap, cost});
    g[v].push_back(es.size()); es.push_back({u, 0, -cost});
}

int main() {
    int n, m;
    ll F;
    if (scanf("%d %d %lld", &n, &m, &F) != 3) return 0;
    int S = n + 1, T = n + 2, N = n + 3;
    g.assign(N, {});
    vector<ll> ex(N, 0);
    ll base = 0;
    for (int i = 0; i < m; i++) {
        int u, v; ll l, c, w;
        if (scanf("%d %d %lld %lld %lld", &u, &v, &l, &c, &w) != 5) return 0;
        base += l * w;
        ex[v] += l; ex[u] -= l;
        if (c > l) addEdge(u, v, c - l, w);
    }
    // the answer flow F leaves n and returns to 1 along a virtual edge with lower = upper = F
    ex[1] += F; ex[n] -= F;
    ll need = 0;
    for (int v = 1; v <= n; v++) {
        if (ex[v] > 0) { addEdge(S, v, ex[v], 0); need += ex[v]; }
        else if (ex[v] < 0) addEdge(v, T, -ex[v], 0);
    }
    // Primal-dual: Dijkstra for potentials, then Dinic's blocking flow on edges of zero reduced cost.
    vector<ll> pot(N, 0), dist(N);
    vector<int> level(N), it(N);
    ll flow = 0, cost = 0;
    auto reduced = [&](int v, const E &e) { return e.cost + pot[v] - pot[e.to]; };
    function<ll(int, ll)> dfs = [&](int v, ll f) -> ll {
        if (v == T) return f;
        for (int &i = it[v]; i < (int)g[v].size(); i++) {
            E &e = es[g[v][i]];
            if (e.cap > 0 && level[e.to] == level[v] + 1 && reduced(v, e) == 0) {
                ll got = dfs(e.to, min(f, e.cap));
                if (got) { e.cap -= got; es[g[v][i] ^ 1].cap += got; return got; }
            }
        }
        return 0;
    };
    while (flow < need) {
        fill(dist.begin(), dist.end(), INF);
        dist[S] = 0;
        priority_queue<pair<ll, int>, vector<pair<ll, int>>, greater<>> pq;
        pq.push({0, S});
        while (!pq.empty()) {
            auto [d, v] = pq.top(); pq.pop();
            if (d > dist[v]) continue;
            for (int id : g[v]) {
                const E &e = es[id];
                if (e.cap <= 0) continue;
                ll nd = d + reduced(v, e);
                if (nd < dist[e.to]) { dist[e.to] = nd; pq.push({nd, e.to}); }
            }
        }
        if (dist[T] >= INF) break;
        for (int v = 0; v < N; v++) pot[v] += min(dist[v], dist[T]);
        while (flow < need) {
            fill(level.begin(), level.end(), -1);
            level[S] = 0;
            queue<int> q;
            q.push(S);
            while (!q.empty()) {
                int v = q.front(); q.pop();
                for (int id : g[v]) {
                    const E &e = es[id];
                    if (e.cap > 0 && level[e.to] < 0 && reduced(v, e) == 0) { level[e.to] = level[v] + 1; q.push(e.to); }
                }
            }
            if (level[T] < 0) break;
            fill(it.begin(), it.end(), 0);
            while (ll f = dfs(S, need - flow)) { flow += f; cost += f * (pot[T] - pot[S]); }
        }
    }
    if (flow < need) puts("-1");
    else printf("%lld\n", base + cost);
}
