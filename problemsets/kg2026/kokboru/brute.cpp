// BFS from every village (small tests only).
#include <bits/stdc++.h>
using namespace std;
int main() {
    int n; scanf("%d", &n);
    vector<vector<int>> g(n + 1);
    for (int i = 0; i < n - 1; i++) { int a, b; scanf("%d %d", &a, &b); g[a].push_back(b); g[b].push_back(a); }
    vector<long long> cnt(n + 1, 0);
    vector<int> d(n + 1);
    for (int s = 1; s <= n; s++) {
        fill(d.begin(), d.end(), -1);
        d[s] = 0;
        queue<int> q; q.push(s);
        while (!q.empty()) { int v = q.front(); q.pop(); for (int u : g[v]) if (d[u] < 0) { d[u] = d[v] + 1; q.push(u); } }
        for (int v = s + 1; v <= n; v++) cnt[d[v]]++;
    }
    for (int k = 1; k < n; k++) printf("%lld%c", cnt[k], k == n - 1 ? '\n' : ' ');
    if (n == 1) printf("\n");
}
