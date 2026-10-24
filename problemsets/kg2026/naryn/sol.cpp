// Offline dynamic connectivity: every bridge lives on a time interval, the intervals are put into
// a segment tree over time, and a DFS over the tree uses a DSU with rollback.
#include <bits/stdc++.h>
using namespace std;

static char ibuf[1 << 25];
size_t ipos = 0, ilen = 0;
inline int gc() {
    if (ipos == ilen) { ilen = fread(ibuf, 1, sizeof ibuf, stdin); ipos = 0; if (!ilen) return -1; }
    return ibuf[ipos++];
}
inline int rdc() { int c = gc(); while (c != '+' && c != '-' && c != '?' && c != 'C') c = gc(); return c; }
inline int rd() {
    int c = gc();
    while (c < '0' || c > '9') c = gc();
    int x = 0;
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return x;
}

int n, q, comps;
vector<int> par, sz;
vector<pair<int, int>> ops;  // (absorbed root, size before) for rollback
int findr(int x) { while (par[x] != x) x = par[x]; return x; }
void unite(int a, int b) {
    a = findr(a); b = findr(b);
    if (a == b) return;
    if (sz[a] < sz[b]) swap(a, b);
    par[b] = a; sz[a] += sz[b]; comps--;
    ops.push_back({b, a});
}
void rollback(size_t to) {
    while (ops.size() > to) {
        auto [b, a] = ops.back(); ops.pop_back();
        par[b] = b; sz[a] -= sz[b]; comps++;
    }
}

vector<vector<pair<int, int>>> seg;
void addEdge(int v, int l, int r, int ql, int qr, pair<int, int> e) {
    if (qr < l || r < ql) return;
    if (ql <= l && r <= qr) { seg[v].push_back(e); return; }
    int m = (l + r) / 2;
    addEdge(2 * v, l, m, ql, qr, e);
    addEdge(2 * v + 1, m + 1, r, ql, qr, e);
}

vector<int> type, qa, qb;
string out;
void solve(int v, int l, int r) {
    size_t mark = ops.size();
    for (auto &e : seg[v]) unite(e.first, e.second);
    if (l == r) {
        if (type[l] == '?') out += findr(qa[l]) == findr(qb[l]) ? "YES\n" : "NO\n";
        else if (type[l] == 'C') { out += to_string(comps); out += '\n'; }
    } else {
        int m = (l + r) / 2;
        solve(2 * v, l, m);
        solve(2 * v + 1, m + 1, r);
    }
    rollback(mark);
}

int main() {
    n = rd(); q = rd();
    type.resize(q); qa.resize(q); qb.resize(q);
    map<pair<int, int>, vector<int>> open;
    vector<array<int, 4>> intervals;  // l, r, u, v
    for (int i = 0; i < q; i++) {
        type[i] = rdc();
        if (type[i] != 'C') {
            int a = rd(), b = rd();
            if (a > b) swap(a, b);
            qa[i] = a; qb[i] = b;
            if (type[i] == '+') open[{a, b}].push_back(i);
            else if (type[i] == '-') {
                auto &vec = open[{a, b}];
                intervals.push_back({vec.back(), i, a, b});
                vec.pop_back();
            }
        }
    }
    for (auto &[key, vec] : open) for (int t : vec) intervals.push_back({t, q - 1, key.first, key.second});
    seg.assign(4 * q, {});
    for (auto &iv : intervals) if (iv[0] <= iv[1]) addEdge(1, 0, q - 1, iv[0], iv[1], {iv[2], iv[3]});
    par.resize(n + 1); sz.assign(n + 1, 1);
    iota(par.begin(), par.end(), 0);
    comps = n;
    solve(1, 0, q - 1);
    fputs(out.c_str(), stdout);
}
