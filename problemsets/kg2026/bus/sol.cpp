// Trips in decreasing departure order; E(trip) = earliest arrival at n after boarding it.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll INF = LLONG_MAX;

static char ibuf[1 << 25];
size_t ipos = 0, ilen = 0;
inline int gc() {
    if (ipos == ilen) { ilen = fread(ibuf, 1, sizeof ibuf, stdin); ipos = 0; if (!ilen) return -1; }
    return ibuf[ipos++];
}
inline ll rd() {
    int c = gc();
    while (c < '0' || c > '9') c = gc();
    ll x = 0;
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return x;
}

int main() {
    int n = rd(), m = rd();
    vector<ll> c(n + 1);
    for (int i = 1; i <= n; i++) c[i] = rd();
    vector<int> A(m), B(m);
    vector<ll> T1(m), T2(m);
    for (int i = 0; i < m; i++) { A[i] = rd(); B[i] = rd(); T1[i] = rd(); T2[i] = rd(); }
    vector<int> ord(m);
    iota(ord.begin(), ord.end(), 0);
    sort(ord.begin(), ord.end(), [&](int x, int y) { return T1[x] > T1[y]; });
    // Per stop: departures in decreasing order with prefix minima of E.
    vector<vector<ll>> dep(n + 1), best(n + 1);
    for (int id : ord) {
        ll e;
        if (B[id] == n) e = T2[id];
        else {
            ll need = T2[id] + c[B[id]];
            const vector<ll> &d = dep[B[id]];
            // number of entries with departure >= need (d is decreasing)
            int k = upper_bound(d.begin(), d.end(), need, greater<ll>()) - d.begin();
            // upper_bound with greater: first element with d < need
            e = k ? best[B[id]][k - 1] : INF;
        }
        vector<ll> &d = dep[A[id]], &b = best[A[id]];
        ll prev = b.empty() ? INF : b.back();
        d.push_back(T1[id]);
        b.push_back(min(prev, e));
    }
    int q = rd();
    string out;
    char buf[32];
    const vector<ll> &d = dep[1];
    while (q--) {
        ll t = rd();
        int k = upper_bound(d.begin(), d.end(), t, greater<ll>()) - d.begin();
        // elements before k are > t or == t? upper_bound with greater<> finds first x with t > x, i.e. x < t.
        ll e = k ? best[1][k - 1] : INF;
        if (n == 1) e = t;
        snprintf(buf, sizeof buf, "%lld\n", e == INF ? -1LL : e);
        out += buf;
    }
    fputs(out.c_str(), stdout);
}
