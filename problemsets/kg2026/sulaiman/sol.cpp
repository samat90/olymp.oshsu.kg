// Heavy-light decomposition + segment tree of (max, count).
#include <bits/stdc++.h>
using namespace std;

int n;
vector<vector<int>> g;
vector<int> par, dep, heavy, head, pos, sz;
vector<long long> h;
vector<pair<long long, int>> t;

pair<long long, int> comb(pair<long long, int> a, pair<long long, int> b) {
    if (a.first != b.first) return a.first > b.first ? a : b;
    return {a.first, a.second + b.second};
}

void upd(int p, long long v) {
    p += n;
    t[p] = {v, 1};
    for (p >>= 1; p; p >>= 1) t[p] = comb(t[2 * p], t[2 * p + 1]);
}

pair<long long, int> query(int l, int r) {  // [l, r]
    pair<long long, int> res = {LLONG_MIN, 0};
    for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
        if (l & 1) res = comb(res, t[l++]);
        if (r & 1) res = comb(res, t[--r]);
    }
    return res;
}

int main() {
    scanf("%d", &n);
    h.assign(n + 1, 0);
    for (int i = 1; i <= n; i++) scanf("%lld", &h[i]);
    g.assign(n + 1, {});
    for (int i = 0; i < n - 1; i++) {
        int a, b;
        scanf("%d %d", &a, &b);
        g[a].push_back(b);
        g[b].push_back(a);
    }
    par.assign(n + 1, 0); dep.assign(n + 1, 0); heavy.assign(n + 1, -1);
    head.assign(n + 1, 0); pos.assign(n + 1, 0); sz.assign(n + 1, 1);
    vector<int> order;
    order.reserve(n);
    order.push_back(1);
    par[1] = 0;
    for (int i = 0; i < (int)order.size(); i++) {
        int v = order[i];
        for (int u : g[v]) if (u != par[v]) { par[u] = v; dep[u] = dep[v] + 1; order.push_back(u); }
    }
    for (int i = n - 1; i > 0; i--) {
        int v = order[i];
        sz[par[v]] += sz[v];
    }
    for (int v = 1; v <= n; v++) {
        int best = 0;
        for (int u : g[v]) if (u != par[v] && sz[u] > best) { best = sz[u]; heavy[v] = u; }
    }
    int cur = 0;
    for (int v : order) {
        if (par[v] != 0 && heavy[par[v]] == v) continue;
        for (int x = v; x != -1; x = heavy[x]) { head[x] = v; pos[x] = cur++; }
    }
    t.assign(2 * n, {LLONG_MIN, 0});
    for (int v = 1; v <= n; v++) t[pos[v] + n] = {h[v], 1};
    for (int i = n - 1; i > 0; i--) t[i] = comb(t[2 * i], t[2 * i + 1]);

    int q;
    scanf("%d", &q);
    string out;
    out.reserve(q * 16);
    char buf[64];
    while (q--) {
        int type;
        scanf("%d", &type);
        if (type == 1) {
            int v; long long x;
            scanf("%d %lld", &v, &x);
            upd(pos[v], x);
        } else {
            int a, b;
            scanf("%d %d", &a, &b);
            pair<long long, int> res = {LLONG_MIN, 0};
            while (head[a] != head[b]) {
                if (dep[head[a]] < dep[head[b]]) swap(a, b);
                res = comb(res, query(pos[head[a]], pos[a]));
                a = par[head[a]];
            }
            if (dep[a] > dep[b]) swap(a, b);
            res = comb(res, query(pos[a], pos[b]));
            snprintf(buf, sizeof buf, "%lld %d\n", res.first, res.second);
            out += buf;
        }
    }
    fputs(out.c_str(), stdout);
}
