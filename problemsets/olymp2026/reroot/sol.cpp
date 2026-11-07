// Rerooting: for every vertex keep (count, sum of distances, sum of squares) of its subtree; moving the
// root over an edge of length w turns d into d + w for one side: sum2 += 2 w sum1 + w^2 cnt, sum1 += w cnt.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef __int128 LL;
void print128(LL v) { if (v >= 10) print128(v / 10); putchar('0' + (int)(v % 10)); }

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<vector<pair<int, ll>>> g(n + 1);
    for (int i = 0; i < n - 1; i++) {
        int u, v; ll w;
        scanf("%d %d %lld", &u, &v, &w);
        g[u].push_back({v, w}), g[v].push_back({u, w});
    }
    vector<int> order, par(n + 1, 0);
    vector<ll> pw(n + 1, 0);
    order.reserve(n);
    vector<int> st{1};
    vector<bool> seen(n + 1, false);
    seen[1] = true;
    while (!st.empty()) {
        int v = st.back(); st.pop_back();
        order.push_back(v);
        for (auto [c, w] : g[v]) if (!seen[c]) seen[c] = true, par[c] = v, pw[c] = w, st.push_back(c);
    }
    vector<ll> cnt(n + 1, 1);
    vector<LL> s1(n + 1, 0), s2(n + 1, 0);  // distances from v to its subtree
    for (int i = n - 1; i > 0; i--) {
        int v = order[i], p = par[v];
        LL w = pw[v];
        cnt[p] += cnt[v];
        s1[p] += s1[v] + w * cnt[v];
        s2[p] += s2[v] + 2 * w * s1[v] + w * w * cnt[v];
    }
    vector<LL> a1(n + 1), a2(n + 1);  // distances from v to all vertices
    a1[1] = s1[1], a2[1] = s2[1];
    for (int i = 1; i < n; i++) {
        int v = order[i], p = par[v];
        LL w = pw[v];
        // the part outside v's subtree, seen from p
        LL oc = n - cnt[v];
        LL o1 = a1[p] - (s1[v] + w * cnt[v]);
        LL o2 = a2[p] - (s2[v] + 2 * w * s1[v] + w * w * cnt[v]);
        a1[v] = s1[v] + o1 + w * oc;
        a2[v] = s2[v] + o2 + 2 * w * o1 + w * w * oc;
    }
    int best = 1;
    for (int v = 2; v <= n; v++) if (a2[v] < a2[best]) best = v;
    printf("%d ", best);
    print128(a2[best]);
    puts("");
}
