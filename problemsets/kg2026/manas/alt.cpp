// Independent check: suffix automaton, number of distinct paths from every state, greedy walk by
// letters; the leftmost occurrence ends at firstpos of the final state.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
int main() {
    int n, q;
    if (scanf("%d %d", &n, &q) != 2) return 0;
    static char buf[400005];
    scanf("%s", buf);
    int cap = 2 * n + 2;
    vector<array<int, 26>> nx(cap);
    vector<int> len(cap), link(cap), firstpos(cap);
    for (auto &a : nx) a.fill(-1);
    link[0] = -1;
    int sz = 1, last = 0;
    for (int i = 0; i < n; i++) {
        int c = buf[i] - 'a', cur = sz++;
        len[cur] = len[last] + 1; firstpos[cur] = i;
        int p = last;
        while (p != -1 && nx[p][c] < 0) { nx[p][c] = cur; p = link[p]; }
        if (p == -1) link[cur] = 0;
        else {
            int qq = nx[p][c];
            if (len[p] + 1 == len[qq]) link[cur] = qq;
            else {
                int cl = sz++;
                nx[cl] = nx[qq]; len[cl] = len[p] + 1; link[cl] = link[qq]; firstpos[cl] = firstpos[qq];
                while (p != -1 && nx[p][c] == qq) { nx[p][c] = cl; p = link[p]; }
                link[qq] = link[cur] = cl;
            }
        }
        last = cur;
    }
    vector<int> order(sz);
    iota(order.begin(), order.end(), 0);
    sort(order.begin(), order.end(), [&](int a, int b) { return len[a] > len[b]; });
    vector<ll> paths(sz, 1);  // number of non-empty strings starting here, plus 1 for stopping
    for (int v : order) for (int c = 0; c < 26; c++) if (nx[v][c] >= 0) paths[v] += paths[nx[v][c]];
    ll total = paths[0] - 1;
    while (q--) {
        ll k;
        scanf("%lld", &k);
        if (k > total) { puts("-1"); continue; }
        int v = 0, L = 0;
        while (k > 0) {
            for (int c = 0; c < 26; c++) {
                int u = nx[v][c];
                if (u < 0) continue;
                if (k > paths[u]) k -= paths[u];
                else { v = u; L++; k--; break; }
            }
        }
        int end = firstpos[v];
        printf("%d %d\n", end - L + 2, end + 1);
    }
}
