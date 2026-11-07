// Ji's segment tree beats: a node keeps max, strict second max, count of max, sum, and lazy add.
// chmin(x) stops at nodes where x >= max; if second < x < max only the maxima change (tag on the node);
// otherwise recurse. Range add shifts max/second/sum. Amortised O((n + q) log^2 n).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll NEG = LLONG_MIN / 4;
int n;
vector<ll> mx, se, sm, lz;
vector<int> cnt, len_;

void pull(int v) {
    int l = 2 * v, r = 2 * v + 1;
    sm[v] = sm[l] + sm[r];
    if (mx[l] == mx[r]) mx[v] = mx[l], cnt[v] = cnt[l] + cnt[r], se[v] = max(se[l], se[r]);
    else if (mx[l] > mx[r]) mx[v] = mx[l], cnt[v] = cnt[l], se[v] = max(se[l], mx[r]);
    else mx[v] = mx[r], cnt[v] = cnt[r], se[v] = max(mx[l], se[r]);
}
void applyAdd(int v, ll x) {
    mx[v] += x, sm[v] += x * len_[v], lz[v] += x;
    if (se[v] != NEG) se[v] += x;
}
void applyMin(int v, ll x) {  // assumes se[v] < x < mx[v]
    if (x >= mx[v]) return;
    sm[v] -= (mx[v] - x) * cnt[v];
    mx[v] = x;
}
void push(int v) {
    for (int c = 2 * v; c <= 2 * v + 1; c++) {
        if (lz[v]) applyAdd(c, lz[v]);
        applyMin(c, mx[v]);
    }
    lz[v] = 0;
}
void build(int v, int l, int r, const vector<ll> &a) {
    len_[v] = r - l + 1;
    if (l == r) { mx[v] = sm[v] = a[l]; se[v] = NEG; cnt[v] = 1; return; }
    int m = (l + r) / 2;
    build(2 * v, l, m, a), build(2 * v + 1, m + 1, r, a);
    pull(v);
}
void chmin(int v, int l, int r, int ql, int qr, ll x) {
    if (qr < l || r < ql || x >= mx[v]) return;
    if (ql <= l && r <= qr && se[v] < x) { applyMin(v, x); return; }
    push(v);
    int m = (l + r) / 2;
    chmin(2 * v, l, m, ql, qr, x), chmin(2 * v + 1, m + 1, r, ql, qr, x);
    pull(v);
}
void add(int v, int l, int r, int ql, int qr, ll x) {
    if (qr < l || r < ql) return;
    if (ql <= l && r <= qr) { applyAdd(v, x); return; }
    push(v);
    int m = (l + r) / 2;
    add(2 * v, l, m, ql, qr, x), add(2 * v + 1, m + 1, r, ql, qr, x);
    pull(v);
}
ll qsum(int v, int l, int r, int ql, int qr) {
    if (qr < l || r < ql) return 0;
    if (ql <= l && r <= qr) return sm[v];
    push(v);
    int m = (l + r) / 2;
    return qsum(2 * v, l, m, ql, qr) + qsum(2 * v + 1, m + 1, r, ql, qr);
}
ll qmax(int v, int l, int r, int ql, int qr) {
    if (qr < l || r < ql) return NEG;
    if (ql <= l && r <= qr) return mx[v];
    push(v);
    int m = (l + r) / 2;
    return max(qmax(2 * v, l, m, ql, qr), qmax(2 * v + 1, m + 1, r, ql, qr));
}

int main() {
    int q;
    if (scanf("%d %d", &n, &q) != 2) return 0;
    vector<ll> a(n);
    for (auto &x : a) scanf("%lld", &x);
    mx.assign(4 * n, 0), se.assign(4 * n, NEG), sm.assign(4 * n, 0), lz.assign(4 * n, 0);
    cnt.assign(4 * n, 0), len_.assign(4 * n, 0);
    build(1, 0, n - 1, a);
    while (q--) {
        int t, l, r;
        scanf("%d %d %d", &t, &l, &r);
        l--, r--;
        if (t == 1) { ll x; scanf("%lld", &x); chmin(1, 0, n - 1, l, r, x); }
        else if (t == 2) { ll x; scanf("%lld", &x); add(1, 0, n - 1, l, r, x); }
        else if (t == 3) printf("%lld\n", qsum(1, 0, n - 1, l, r));
        else printf("%lld\n", qmax(1, 0, n - 1, l, r));
    }
}
