// Independent check: centroid decomposition with exact convolutions (NTT modulo two primes + CRT)
// and the "merge children one by one" scheme: pairs through the centroid = sum over i of
// conv(prefix of earlier children incl. the centroid, child i).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef unsigned long long ull;

template <ull MOD, ull G> struct NTT {
    static ull pw(ull a, ull e) { ull r = 1; a %= MOD; while (e) { if (e & 1) r = r * a % MOD; a = a * a % MOD; e >>= 1; } return r; }
    static void run(vector<ull> &a, bool inv) {
        int n = a.size();
        for (int i = 1, j = 0; i < n; i++) {
            int bit = n >> 1;
            for (; j & bit; bit >>= 1) j ^= bit;
            j ^= bit;
            if (i < j) swap(a[i], a[j]);
        }
        for (int len = 2; len <= n; len <<= 1) {
            ull w = pw(G, (MOD - 1) / len);
            if (inv) w = pw(w, MOD - 2);
            for (int i = 0; i < n; i += len) {
                ull wn = 1;
                for (int j = 0; j < len / 2; j++) {
                    ull u = a[i + j], v = a[i + j + len / 2] * wn % MOD;
                    a[i + j] = (u + v) % MOD; a[i + j + len / 2] = (u + MOD - v) % MOD;
                    wn = wn * w % MOD;
                }
            }
        }
        if (inv) { ull ni = pw(n, MOD - 2); for (auto &x : a) x = x * ni % MOD; }
    }
    static vector<ull> conv(const vector<ll> &x, const vector<ll> &y) {
        int need = x.size() + y.size() - 1, sz = 1;
        while (sz < need) sz <<= 1;
        vector<ull> a(sz, 0), b(sz, 0);
        for (size_t i = 0; i < x.size(); i++) a[i] = x[i] % MOD;
        for (size_t i = 0; i < y.size(); i++) b[i] = y[i] % MOD;
        run(a, false); run(b, false);
        for (int i = 0; i < sz; i++) a[i] = a[i] * b[i] % MOD;
        run(a, true);
        a.resize(need);
        return a;
    }
};
const ull M1 = 998244353, M2 = 1004535809;
vector<ll> conv(const vector<ll> &x, const vector<ll> &y) {
    vector<ll> r(x.size() + y.size() - 1, 0);
    if ((ll)x.size() * (ll)y.size() <= 4096) {
        for (size_t i = 0; i < x.size(); i++) for (size_t j = 0; j < y.size(); j++) r[i + j] += x[i] * y[j];
        return r;
    }
    auto a = NTT<M1, 3>::conv(x, y), b = NTT<M2, 3>::conv(x, y);
    ull inv = NTT<M2, 3>::pw(M1 % M2, M2 - 2);
    for (size_t i = 0; i < r.size(); i++) {
        ull t = (b[i] + M2 - a[i] % M2) % M2 * inv % M2;
        r[i] = a[i] + t * M1;  // exact, the true value is below M1 * M2
    }
    return r;
}

int n;
vector<vector<int>> g;
vector<char> removed;
vector<int> sz_, par_;
vector<ll> ans;

int main() {
    scanf("%d", &n);
    g.assign(n + 1, {});
    for (int i = 0; i < n - 1; i++) { int a, b; scanf("%d %d", &a, &b); g[a].push_back(b); g[b].push_back(a); }
    removed.assign(n + 1, 0); sz_.assign(n + 1, 0); par_.assign(n + 1, 0);
    ans.assign(n + 1, 0);
    vector<int> stack{1};
    while (!stack.empty()) {
        int r = stack.back(); stack.pop_back();
        vector<int> order{r};
        par_[r] = 0;
        for (size_t i = 0; i < order.size(); i++)
            for (int u : g[order[i]]) if (!removed[u] && u != par_[order[i]]) { par_[u] = order[i]; order.push_back(u); }
        for (int i = order.size() - 1; i >= 0; i--) {
            int v = order[i]; sz_[v] = 1;
            for (int u : g[v]) if (!removed[u] && u != par_[v]) sz_[v] += sz_[u];
        }
        int tot = order.size(), c = r;
        for (int v : order) {
            int mx = tot - sz_[v];
            for (int u : g[v]) if (!removed[u] && u != par_[v]) mx = max(mx, sz_[u]);
            if (2 * mx <= tot) { c = v; break; }
        }
        // children of the centroid, sorted by depth so prefix arrays stay small first
        vector<vector<ll>> hs;
        for (int u : g[c]) {
            if (removed[u]) continue;
            vector<ll> h{0};
            vector<int> cur{u}, prv{c};
            for (int d = 1; !cur.empty(); d++) {
                h.push_back(cur.size());
                vector<int> nc, np;
                for (size_t i = 0; i < cur.size(); i++)
                    for (int w : g[cur[i]]) if (!removed[w] && w != prv[i]) { nc.push_back(w); np.push_back(cur[i]); }
                cur.swap(nc); prv.swap(np);
            }
            hs.push_back(h);
        }
        sort(hs.begin(), hs.end(), [](auto &a, auto &b) { return a.size() < b.size(); });
        vector<ll> acc{1};
        for (auto &h : hs) {
            auto r2 = conv(acc, h);
            for (size_t k = 1; k < r2.size() && k <= (size_t)n; k++) ans[k] += r2[k];
            if (acc.size() < h.size()) acc.resize(h.size(), 0);
            for (size_t k = 0; k < h.size(); k++) acc[k] += h[k];
        }
        removed[c] = 1;
        for (int u : g[c]) if (!removed[u]) stack.push_back(u);
    }
    for (int k = 1; k < n; k++) printf("%lld%c", ans[k], k == n - 1 ? '\n' : ' ');
    if (n == 1) printf("\n");
}
