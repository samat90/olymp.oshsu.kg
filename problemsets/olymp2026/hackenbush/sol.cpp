// Green Hackenbush on a rooted tree: g(v) = XOR over children c of (g(c) + 1), the position is lost iff g(0) = 0.
// Top-down we keep need(v): the Grundy value the subtree of v must get so that g(0) becomes 0 (need(0) = 0).
// For a child c: (g(c)+1) must turn into t = need(v) ^ g(v) ^ (g(c)+1). If t = 0, cutting the branch c wins;
// otherwise the cut must be inside c's subtree with need(c) = t - 1.
#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<int> p(n + 1, 0);
    for (int v = 1; v <= n; v++) scanf("%d", &p[v]);
    vector<long long> g(n + 1, 0), need(n + 1, -1);
    for (int v = n; v >= 1; v--) g[p[v]] ^= g[v] + 1;  // parents have smaller numbers
    need[0] = 0;
    long long wins = 0;
    for (int v = 1; v <= n; v++) {  // parents are processed before children
        int u = p[v];
        if (need[u] < 0) continue;
        long long t = need[u] ^ g[u] ^ (g[v] + 1);
        if (t == 0) wins++;
        else need[v] = t - 1;
    }
    printf("%lld\n", wins);
}
