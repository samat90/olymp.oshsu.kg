// Sprague-Grundy on a DAG; winning first moves counted with sorted neighbour Grundy values.
#include <bits/stdc++.h>
using namespace std;

static char ibuf[1 << 25];
size_t ipos = 0, ilen = 0;
inline int gc() {
    if (ipos == ilen) { ilen = fread(ibuf, 1, sizeof ibuf, stdin); ipos = 0; if (!ilen) return -1; }
    return ibuf[ipos++];
}
inline int rd() {
    int c = gc();
    while (c < '0' || c > '9') c = gc();
    int x = 0;
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return x;
}

int main() {
    int n = rd(), m = rd();
    vector<int> head(n + 2, 0), eu(m), ev(m), indeg(n + 1, 0);
    for (int i = 0; i < m; i++) { eu[i] = rd(); ev[i] = rd(); head[eu[i]]++; indeg[ev[i]]++; }
    // CSR adjacency
    vector<int> start(n + 2, 0);
    for (int v = 1; v <= n; v++) start[v + 1] = start[v] + head[v];
    vector<int> adj(m), fill(start.begin(), start.end());
    for (int i = 0; i < m; i++) adj[fill[eu[i]]++] = ev[i];
    // reverse topological order via Kahn on the graph
    vector<int> order;
    order.reserve(n);
    for (int v = 1; v <= n; v++) if (!indeg[v]) order.push_back(v);
    for (size_t i = 0; i < order.size(); i++) {
        int v = order[i];
        for (int j = start[v]; j < start[v + 1]; j++) if (--indeg[adj[j]] == 0) order.push_back(adj[j]);
    }
    vector<int> g(n + 1, 0), mark(m + 2, 0);
    vector<int> sortedg(m);
    int stamp = 0;
    for (int i = n - 1; i >= 0; i--) {
        int v = order[i];
        ++stamp;
        int d = start[v + 1] - start[v];
        for (int j = start[v]; j < start[v + 1]; j++) {
            int x = g[adj[j]];
            if (x <= d) mark[x] = stamp;
            sortedg[j] = x;
        }
        int x = 0;
        while (mark[x] == stamp) x++;
        g[v] = x;
        sort(sortedg.begin() + start[v], sortedg.begin() + start[v + 1]);
    }
    int q = rd();
    string out;
    char buf[32];
    vector<int> pos;
    while (q--) {
        int k = rd();
        pos.resize(k);
        int X = 0;
        for (int i = 0; i < k; i++) { pos[i] = rd(); X ^= g[pos[i]]; }
        long long cnt = 0;
        if (X) {
            for (int v : pos) {
                int target = g[v] ^ X;
                auto b = sortedg.begin() + start[v], e = sortedg.begin() + start[v + 1];
                auto r = equal_range(b, e, target);
                cnt += r.second - r.first;
            }
        }
        snprintf(buf, sizeof buf, "%lld\n", cnt);
        out += buf;
    }
    fputs(out.c_str(), stdout);
}
