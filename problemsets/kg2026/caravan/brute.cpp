// Direct DP over all ancestors (small tests only).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
int main() {
    int n; scanf("%d", &n);
    vector<int> par(n + 1, 0); vector<ll> len(n + 1), S(n + 1), V(n + 1), dist(n + 1, 0), dp(n + 1, 0);
    for (int i = 2; i <= n; i++) scanf("%d %lld %lld %lld", &par[i], &len[i], &S[i], &V[i]);
    // parents may come after children in numbering: compute in BFS order
    vector<vector<int>> ch(n + 1);
    for (int i = 2; i <= n; i++) ch[par[i]].push_back(i);
    vector<int> order{1};
    for (size_t i = 0; i < order.size(); i++) for (int u : ch[order[i]]) order.push_back(u);
    for (int u : order) {
        if (u == 1) continue;
        dist[u] = dist[par[u]] + len[u];
        ll best = LLONG_MAX;
        for (int j = par[u]; j; j = par[j]) best = min(best, dp[j] + S[u] + V[u] * (dist[u] - dist[j]));
        dp[u] = best;
    }
    for (int i = 2; i <= n; i++) printf("%lld%c", dp[i], i == n ? '\n' : ' ');
    if (n == 1) printf("\n");
}
