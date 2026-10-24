// Independent check: lower bounds removed by first forcing them, then the remaining demand is met
// by cancelling with SPFA-based successive shortest paths (no potentials), on the same reduction
// but with an explicit edge n -> 1 of capacity [F, F] modelled through a source/sink pair.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll INF = LLONG_MAX / 4;
struct E { int to; ll cap, cost; };
vector<E> es;
vector<vector<int>> g;
void add(int u, int v, ll cap, ll cost) {
    g[u].push_back(es.size()); es.push_back({v, cap, cost});
    g[v].push_back(es.size()); es.push_back({u, 0, -cost});
}
int main() {
    int n, m; ll F;
    if (scanf("%d %d %lld", &n, &m, &F) != 3) return 0;
    int S = 0, T = n + 1;
    g.assign(n + 2, {});
    vector<ll> inL(n + 2, 0), outL(n + 2, 0);
    ll base = 0;
    for (int i = 0; i < m; i++) {
        int u, v; ll l, c, w;
        if (scanf("%d %d %lld %lld %lld", &u, &v, &l, &c, &w) != 5) return 0;
        add(u, v, c - l, w);
        inL[v] += l; outL[u] += l;
        base += l * w;
    }
    inL[1] += F; outL[n] += F;
    ll need = 0;
    for (int v = 1; v <= n; v++) {
        add(S, v, inL[v], 0);
        add(v, T, outL[v], 0);
        need += inL[v];
    }
    ll flow = 0, cost = 0;
    vector<ll> d(n + 2);
    vector<int> pe(n + 2);
    vector<char> inq(n + 2);
    while (true) {
        fill(d.begin(), d.end(), INF);
        d[S] = 0;
        deque<int> q{S};
        inq.assign(n + 2, 0);
        inq[S] = 1;
        while (!q.empty()) {
            int v = q.front(); q.pop_front(); inq[v] = 0;
            for (int id : g[v]) {
                E &e = es[id];
                if (e.cap > 0 && d[v] + e.cost < d[e.to]) {
                    d[e.to] = d[v] + e.cost; pe[e.to] = id;
                    if (!inq[e.to]) { inq[e.to] = 1; q.push_back(e.to); }
                }
            }
        }
        if (d[T] >= INF) break;
        ll f = INF;
        for (int v = T; v != S; v = es[pe[v] ^ 1].to) f = min(f, es[pe[v]].cap);
        for (int v = T; v != S; v = es[pe[v] ^ 1].to) { es[pe[v]].cap -= f; es[pe[v] ^ 1].cap += f; }
        flow += f; cost += f * d[T];
    }
    if (flow < need) puts("-1");
    else printf("%lld\n", base + cost);
}
