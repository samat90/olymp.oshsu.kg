// Groups may share vertices, so a group is a chain of the reachability order. Minimum chain cover =
// n - maximum matching in the bipartite graph "u -> v reachable" (transitive closure by bitsets).
#include <bits/stdc++.h>
using namespace std;
const int N = 1505;
bitset<N> reach[N];
int n, m;
vector<int> adj[N], order_;
int matchR[N], dist_[N], matchL[N];

bool bfs() {
    queue<int> q;
    bool found = false;
    for (int u = 0; u < n; u++) {
        if (matchL[u] < 0) dist_[u] = 0, q.push(u);
        else dist_[u] = -1;
    }
    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v = reach[u]._Find_first(); v < n; v = reach[u]._Find_next(v)) {
            int w = matchR[v];
            if (w < 0) found = true;
            else if (dist_[w] < 0) dist_[w] = dist_[u] + 1, q.push(w);
        }
    }
    return found;
}
bool dfs(int u) {
    for (int v = reach[u]._Find_first(); v < n; v = reach[u]._Find_next(v)) {
        int w = matchR[v];
        if (w < 0 || (dist_[w] == dist_[u] + 1 && dfs(w))) { matchL[u] = v, matchR[v] = u; return true; }
    }
    dist_[u] = -1;
    return false;
}

int main() {
    if (scanf("%d %d", &n, &m) != 2) return 0;
    vector<int> indeg(n, 0);
    for (int i = 0; i < m; i++) {
        int a, b;
        scanf("%d %d", &a, &b);
        adj[a - 1].push_back(b - 1);
        indeg[b - 1]++;
    }
    queue<int> q;
    for (int i = 0; i < n; i++) if (!indeg[i]) q.push(i);
    while (!q.empty()) {
        int u = q.front(); q.pop();
        order_.push_back(u);
        for (int v : adj[u]) if (--indeg[v] == 0) q.push(v);
    }
    for (int i = n - 1; i >= 0; i--) {
        int u = order_[i];
        for (int v : adj[u]) reach[u][v] = 1, reach[u] |= reach[v];
    }
    memset(matchR, -1, sizeof matchR);
    memset(matchL, -1, sizeof matchL);
    int match = 0;
    while (bfs())
        for (int u = 0; u < n; u++)
            if (matchL[u] < 0 && dfs(u)) match++;
    printf("%d\n", n - match);
}
