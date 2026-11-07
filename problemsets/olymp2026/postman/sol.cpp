// Chinese postman: answer = total length + minimum perfect matching of the odd-degree vertices with
// shortest-path distances (Euler: a connected graph with even degrees has a closed walk through all edges).
// Dijkstra from each of the <= 20 odd vertices, then bitmask DP that always matches the lowest unmatched one.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    vector<vector<pair<int, ll>>> g(n + 1);
    vector<int> deg(n + 1, 0);
    ll total = 0;
    for (int i = 0; i < m; i++) {
        int u, v; ll w;
        scanf("%d %d %lld", &u, &v, &w);
        g[u].push_back({v, w}), g[v].push_back({u, w});
        deg[u]++, deg[v]++;
        total += w;
    }
    vector<int> odd;
    for (int v = 1; v <= n; v++) if (deg[v] % 2) odd.push_back(v);
    int k = odd.size();
    vector<vector<ll>> D(k, vector<ll>(k, 0));
    for (int i = 0; i < k; i++) {
        vector<ll> dist(n + 1, LLONG_MAX);
        priority_queue<pair<ll, int>, vector<pair<ll, int>>, greater<>> pq;
        dist[odd[i]] = 0, pq.push({0, odd[i]});
        while (!pq.empty()) {
            auto [d, v] = pq.top(); pq.pop();
            if (d > dist[v]) continue;
            for (auto [u, w] : g[v]) if (d + w < dist[u]) dist[u] = d + w, pq.push({dist[u], u});
        }
        for (int j = 0; j < k; j++) D[i][j] = dist[odd[j]];
    }
    vector<ll> dp(1 << k, LLONG_MAX);
    dp[0] = 0;
    for (int mask = 0; mask < (1 << k); mask++) {
        if (dp[mask] == LLONG_MAX) continue;
        int i = 0;
        while (i < k && (mask >> i & 1)) i++;
        if (i == k) continue;
        for (int j = i + 1; j < k; j++)
            if (!(mask >> j & 1)) {
                int nm = mask | 1 << i | 1 << j;
                dp[nm] = min(dp[nm], dp[mask] + D[i][j]);
            }
    }
    printf("%lld\n", total + dp[(1 << k) - 1]);
}
