// Centroid decomposition; at every centroid the depth histograms are squared with an FFT:
// pairs through the centroid = (A * A) - sum over child subtrees (S * S), halved at the end.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef complex<double> cd;

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

void fft(vector<cd> &a, bool inv) {
    int n = a.size();
    for (int i = 1, j = 0; i < n; i++) {
        int bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) swap(a[i], a[j]);
    }
    for (int len = 2; len <= n; len <<= 1) {
        double ang = 2 * M_PI / len * (inv ? -1 : 1);
        cd wl(cos(ang), sin(ang));
        for (int i = 0; i < n; i += len) {
            cd w(1);
            for (int j = 0; j < len / 2; j++) {
                // recompute the root directly every 32 steps to keep the error small
                if ((j & 31) == 0) w = polar(1.0, ang * j);
                cd u = a[i + j], v = a[i + j + len / 2] * w;
                a[i + j] = u + v; a[i + j + len / 2] = u - v;
                w *= wl;
            }
        }
    }
    if (inv) for (auto &x : a) x /= n;
}

// square of a histogram
vector<ll> square(const vector<ll> &h) {
    int m = h.size();
    vector<ll> res(2 * m - 1, 0);
    if (m <= 64) {
        for (int i = 0; i < m; i++) if (h[i]) for (int j = 0; j < m; j++) res[i + j] += h[i] * h[j];
        return res;
    }
    int sz = 1;
    while (sz < 2 * m) sz <<= 1;
    vector<cd> a(sz);
    for (int i = 0; i < m; i++) a[i] = cd((double)h[i], 0);
    fft(a, false);
    for (auto &x : a) x *= x;
    fft(a, true);
    for (int i = 0; i < 2 * m - 1; i++) res[i] = llround(a[i].real());
    return res;
}

int n;
vector<vector<int>> g;
vector<int> sub;
vector<char> removed;
vector<ll> ans;

int findCentroid(int root) {
    // iterative size computation
    vector<int> order{root}, parent{-1};
    static vector<int> par;
    if ((int)par.size() < n + 1) par.assign(n + 1, 0);
    par[root] = 0;
    for (size_t i = 0; i < order.size(); i++) {
        int v = order[i];
        for (int u : g[v]) if (!removed[u] && u != par[v]) { par[u] = v; order.push_back(u); }
    }
    for (int i = order.size() - 1; i >= 0; i--) {
        int v = order[i];
        sub[v] = 1;
        for (int u : g[v]) if (!removed[u] && u != par[v]) sub[v] += sub[u];
    }
    int total = order.size();
    for (int v : order) {
        int mx = total - sub[v];
        for (int u : g[v]) if (!removed[u] && u != par[v]) mx = max(mx, sub[u]);
        if (mx * 2 <= total) return v;
    }
    return root;
}

void depths(int start, int from, vector<ll> &h) {
    vector<pair<int, int>> st{{start, from}};
    vector<int> d{1};
    // BFS by layers
    vector<int> cur{start}, prv{from};
    int depth = 1;
    while (!cur.empty()) {
        if ((int)h.size() <= depth) h.resize(depth + 1, 0);
        h[depth] += cur.size();
        vector<int> nc, np;
        for (size_t i = 0; i < cur.size(); i++)
            for (int u : g[cur[i]]) if (!removed[u] && u != prv[i]) { nc.push_back(u); np.push_back(cur[i]); }
        cur.swap(nc); prv.swap(np);
        depth++;
    }
}

int main() {
    n = rd();
    g.assign(n + 1, {});
    for (int i = 0; i < n - 1; i++) { int a = rd(), b = rd(); g[a].push_back(b); g[b].push_back(a); }
    sub.assign(n + 1, 0); removed.assign(n + 1, 0); ans.assign(2 * n + 2, 0);
    vector<int> todo{1};
    while (!todo.empty()) {
        int r = todo.back(); todo.pop_back();
        int c = findCentroid(r);
        vector<ll> all{1};
        for (int u : g[c]) {
            if (removed[u]) continue;
            vector<ll> h{0};
            depths(u, c, h);
            auto sq = square(h);
            for (size_t k = 0; k < sq.size(); k++) ans[k] -= sq[k];
            if (all.size() < h.size()) all.resize(h.size(), 0);
            for (size_t k = 0; k < h.size(); k++) all[k] += h[k];
        }
        auto sq = square(all);
        for (size_t k = 0; k < sq.size(); k++) ans[k] += sq[k];
        removed[c] = 1;
        for (int u : g[c]) if (!removed[u]) todo.push_back(u);
    }
    string out;
    char buf[24];
    for (int k = 1; k < n; k++) {
        int len = snprintf(buf, sizeof buf, "%lld%c", ans[k] / 2, k == n - 1 ? '\n' : ' ');
        out.append(buf, len);
    }
    if (n == 1) out = "\n";
    fputs(out.c_str(), stdout);
}
