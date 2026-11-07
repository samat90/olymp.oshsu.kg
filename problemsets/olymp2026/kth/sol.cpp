// Persistent segment tree over compressed values: version i counts the values a[1..i]. The k-th smallest
// on [l, r] descends both versions r and l-1 at once. Fully online.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const int MAXN = 200005 * 20;
int lc[MAXN], rc[MAXN], cntv[MAXN], tot = 0;
int upd(int prev, int l, int r, int pos) {
    int v = ++tot;
    lc[v] = lc[prev], rc[v] = rc[prev], cntv[v] = cntv[prev] + 1;
    if (l < r) {
        int m = (l + r) / 2;
        if (pos <= m) lc[v] = upd(lc[prev], l, m, pos);
        else rc[v] = upd(rc[prev], m + 1, r, pos);
    }
    return v;
}
int kth(int a, int b, int l, int r, int k) {
    while (l < r) {
        int m = (l + r) / 2, left = cntv[lc[b]] - cntv[lc[a]];
        if (k <= left) a = lc[a], b = lc[b], r = m;
        else k -= left, a = rc[a], b = rc[b], l = m + 1;
    }
    return l;
}
int main() {
    int n, q;
    if (scanf("%d %d", &n, &q) != 2) return 0;
    vector<ll> a(n);
    for (auto &x : a) scanf("%lld", &x);
    vector<ll> vals(a);
    sort(vals.begin(), vals.end());
    vals.erase(unique(vals.begin(), vals.end()), vals.end());
    int K = vals.size();
    vector<int> root(n + 1, 0);
    for (int i = 0; i < n; i++)
        root[i + 1] = upd(root[i], 0, K - 1, lower_bound(vals.begin(), vals.end(), a[i]) - vals.begin());
    ll last = 0;
    while (q--) {
        ll x, y, z;
        scanf("%lld %lld %lld", &x, &y, &z);
        ll l = ((x ^ last) % n) + 1, r = ((y ^ last) % n) + 1;
        if (l > r) swap(l, r);
        ll k = ((z ^ last) % (r - l + 1)) + 1;
        last = vals[kth(root[l - 1], root[r], 0, K - 1, k)];
        printf("%lld\n", last);
    }
}
