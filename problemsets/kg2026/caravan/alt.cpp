// Independent check: convex hull of the ancestors' lines kept in one array; a new line replaces the
// suffix it dominates (position found by binary search) and is undone when the DFS leaves.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef __int128 i128;
int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<int> par(n + 1);
    vector<ll> len(n + 1), S(n + 1), V(n + 1);
    vector<vector<int>> ch(n + 1);
    for (int i = 2; i <= n; i++) {
        scanf("%d %lld %lld %lld", &par[i], &len[i], &S[i], &V[i]);
        ch[par[i]].push_back(i);
    }
    // lines y = k x + b with k = -dist (strictly decreasing along a root path), minimum envelope
    vector<ll> K(n + 1), B(n + 1);
    int top = 0;
    auto bad = [&](int a, int b, ll k, ll c) {  // is line b useless between a and (k, c)?
        // intersection(a, new) <= intersection(a, b)
        return (i128)(c - B[a]) * (K[a] - K[b]) <= (i128)(B[b] - B[a]) * (K[a] - k);
    };
    vector<ll> dist(n + 1, 0), dp(n + 1, 0);
    // iterative DFS with saved (position, overwritten line, old top)
    struct Frame { int v; size_t idx; int pos; ll ok, ob; int otop; };
    vector<Frame> st;
    K[0] = 0; B[0] = 0; top = 1;
    st.push_back({1, 0, -1, 0, 0, 0});
    while (!st.empty()) {
        Frame &f = st.back();
        if (f.idx < ch[f.v].size()) {
            int u = ch[f.v][f.idx++];
            dist[u] = dist[f.v] + len[u];
            ll x = V[u];
            int lo = 0, hi = top - 1;
            while (lo < hi) {
                int m = (lo + hi) / 2;
                if ((i128)K[m] * x + B[m] >= (i128)K[m + 1] * x + B[m + 1]) lo = m + 1; else hi = m;
            }
            dp[u] = K[lo] * x + B[lo] + S[u] + V[u] * dist[u];
            ll k = -dist[u], c = dp[u];
            // find the first position p >= 1 such that line p-1 stays and p is useless
            int l = 1, r = top;
            while (l < r) {
                int m = (l + r) / 2;
                if (bad(m - 1, m, k, c)) r = m; else l = m + 1;
            }
            int pos = l;
            Frame nf{u, 0, pos, pos < (int)K.size() ? K[pos] : 0, pos < (int)B.size() ? B[pos] : 0, top};
            K[pos] = k; B[pos] = c; top = pos + 1;
            st.push_back(nf);
        } else {
            if (f.pos >= 0) { K[f.pos] = f.ok; B[f.pos] = f.ob; top = f.otop; }
            st.pop_back();
        }
    }
    for (int i = 2; i <= n; i++) printf("%lld%c", dp[i], i == n ? '\n' : ' ');
    if (n == 1) printf("\n");
}
