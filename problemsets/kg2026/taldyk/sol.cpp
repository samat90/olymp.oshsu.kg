// Kruskal reconstruction tree (by decreasing clearance) + binary lifting
// + persistent segment tree over leaf order for the k-th highest altitude.
#include <bits/stdc++.h>
using namespace std;

static char ibuf[1 << 25];
size_t ipos = 0, ilen = 0;
inline int gc() {
    if (ipos == ilen) { ilen = fread(ibuf, 1, sizeof ibuf, stdin); ipos = 0; if (!ilen) return -1; }
    return ibuf[ipos++];
}
inline long long rd() {
    int c = gc();
    while (c < '0' || c > '9') c = gc();
    long long x = 0;
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return x;
}

const int LOG = 19;
int n, m, tot;
vector<int> dsu, lc, rc, val, upv[LOG], tin, tout, leafAt;
int findp(int x) { while (dsu[x] != x) x = dsu[x] = dsu[dsu[x]]; return x; }

// persistent segment tree over altitude ranks
vector<int> L, R, C;
int newnode(int l, int r, int c) { L.push_back(l); R.push_back(r); C.push_back(c); return (int)C.size() - 1; }
int K;
int ins(int prev, int lo, int hi, int pos) {
    int cur = newnode(L[prev], R[prev], C[prev] + 1);
    if (lo == hi) return cur;
    int mid = (lo + hi) / 2;
    if (pos <= mid) { int x = ins(L[prev], lo, mid, pos); L[cur] = x; }
    else { int x = ins(R[prev], mid + 1, hi, pos); R[cur] = x; }
    return cur;
}
int kth(int a, int b, int lo, int hi, int k) {  // k-th largest among versions (a, b]
    while (lo < hi) {
        int mid = (lo + hi) / 2;
        int right = C[R[b]] - C[R[a]];
        if (k <= right) { a = R[a]; b = R[b]; lo = mid + 1; }
        else { k -= right; a = L[a]; b = L[b]; hi = mid; }
    }
    return lo;
}

int main() {
    n = rd(); m = rd();
    vector<long long> h(n + 1);
    for (int i = 1; i <= n; i++) h[i] = rd();
    vector<array<long long, 3>> e(m);
    for (auto &x : e) { x[1] = rd(); x[2] = rd(); x[0] = rd(); }
    sort(e.begin(), e.end(), [](const array<long long, 3> &a, const array<long long, 3> &b) { return a[0] > b[0]; });
    int N = 2 * n;
    dsu.resize(N); iota(dsu.begin(), dsu.end(), 0);
    lc.assign(N, -1); rc.assign(N, -1); val.assign(N, INT_MAX);
    for (int j = 0; j < LOG; j++) upv[j].assign(N, 0);
    tot = n + 1;
    for (int i = 1; i <= n; i++) upv[0][i] = i;
    for (auto &x : e) {
        int a = findp(x[1]), b = findp(x[2]);
        if (a == b) continue;
        int v = tot++;
        val[v] = (int)x[0];
        lc[v] = a; rc[v] = b;
        dsu[a] = dsu[b] = v;
        upv[0][a] = upv[0][b] = v;
        upv[0][v] = v;
    }
    // roots point to themselves; ranks of altitudes
    vector<long long> alts(h.begin() + 1, h.end());
    sort(alts.begin(), alts.end());
    alts.erase(unique(alts.begin(), alts.end()), alts.end());
    K = alts.size();
    tin.assign(tot, 0); tout.assign(tot, 0);
    leafAt.clear();
    vector<int> ver(1, 0);
    newnode(0, 0, 0);  // node 0: empty tree
    int timer = 0;
    vector<int> st;
    for (int r = 1; r < tot; r++) {
        if (upv[0][r] != r) continue;  // not a root
        st.push_back(r);
        while (!st.empty()) {
            int v = st.back();
            if (v > 0) {
                st.back() = ~v;
                tin[v] = timer;
                if (v <= n) {
                    int pos = lower_bound(alts.begin(), alts.end(), h[v]) - alts.begin();
                    ver.push_back(ins(ver.back(), 0, K - 1, pos));
                    timer++;
                } else {
                    st.push_back(rc[v]);
                    st.push_back(lc[v]);
                }
            } else {
                st.pop_back();
                tout[~v] = timer;
            }
        }
    }
    for (int j = 1; j < LOG; j++)
        for (int v = 1; v < tot; v++) upv[j][v] = upv[j - 1][upv[j - 1][v]];
    int q = rd();
    long long last = 0;
    string out;
    char buf[32];
    while (q--) {
        long long a = rd(), b = rd(), c = rd();
#ifdef RAW
        int v = a; long long W = b; long long k = c;
#else
        int v = a ^ last; long long W = b ^ last; long long k = c ^ last;
#endif
        for (int j = LOG - 1; j >= 0; j--) {
            int u = upv[j][v];
            if (u != v && val[u] >= W) v = u;
        }
        // one more step check (binary lifting above may stop below due to self-loop roots)
        while (upv[0][v] != v && val[upv[0][v]] >= W) v = upv[0][v];
        long long size = tout[v] - tin[v];
        long long ans = -1;
        if (k <= size) ans = alts[kth(ver[tin[v]], ver[tout[v]], 0, K - 1, (int)k)];
        last = ans == -1 ? 0 : ans;
        snprintf(buf, sizeof buf, "%lld\n", ans);
        out += buf;
    }
    fputs(out.c_str(), stdout);
}
