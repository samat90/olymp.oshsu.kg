// Lazy segment tree: range add, range assign, range sum and max.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

static char ibuf[1 << 25];
size_t ipos = 0, ilen = 0;
inline int gc() {
    if (ipos == ilen) { ilen = fread(ibuf, 1, sizeof ibuf, stdin); ipos = 0; if (!ilen) return -1; }
    return ibuf[ipos++];
}
inline ll rd() {
    int c = gc();
    while (c != '-' && (c < '0' || c > '9')) c = gc();
    bool neg = false;
    if (c == '-') { neg = true; c = gc(); }
    ll x = 0;
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return neg ? -x : x;
}

int n;
vector<ll> sm, mx, ad, as_;
vector<char> has;

void apply_assign(int v, int len, ll x) { sm[v] = x * len; mx[v] = x; as_[v] = x; has[v] = 1; ad[v] = 0; }
void apply_add(int v, int len, ll x) { sm[v] += x * len; mx[v] += x; if (has[v]) as_[v] += x; else ad[v] += x; }

void push(int v, int l, int r) {
    int m = (l + r) / 2;
    if (has[v]) {
        apply_assign(2 * v, m - l + 1, as_[v]);
        apply_assign(2 * v + 1, r - m, as_[v]);
        has[v] = 0;
    }
    if (ad[v]) {
        apply_add(2 * v, m - l + 1, ad[v]);
        apply_add(2 * v + 1, r - m, ad[v]);
        ad[v] = 0;
    }
}

void pull(int v) { sm[v] = sm[2 * v] + sm[2 * v + 1]; mx[v] = max(mx[2 * v], mx[2 * v + 1]); }

vector<ll> a;
void build(int v, int l, int r) {
    if (l == r) { sm[v] = mx[v] = a[l]; return; }
    int m = (l + r) / 2;
    build(2 * v, l, m); build(2 * v + 1, m + 1, r);
    pull(v);
}

void update(int v, int l, int r, int ql, int qr, int type, ll x) {
    if (qr < l || r < ql) return;
    if (ql <= l && r <= qr) {
        if (type == 1) apply_add(v, r - l + 1, x); else apply_assign(v, r - l + 1, x);
        return;
    }
    push(v, l, r);
    int m = (l + r) / 2;
    update(2 * v, l, m, ql, qr, type, x);
    update(2 * v + 1, m + 1, r, ql, qr, type, x);
    pull(v);
}

ll qs, qm;
void query(int v, int l, int r, int ql, int qr) {
    if (qr < l || r < ql) return;
    if (ql <= l && r <= qr) { qs += sm[v]; qm = max(qm, mx[v]); return; }
    push(v, l, r);
    int m = (l + r) / 2;
    query(2 * v, l, m, ql, qr);
    query(2 * v + 1, m + 1, r, ql, qr);
}

int main() {
    n = rd();
    int q = rd();
    a.resize(n + 1);
    for (int i = 1; i <= n; i++) a[i] = rd();
    sm.assign(4 * n, 0); mx.assign(4 * n, 0); ad.assign(4 * n, 0); as_.assign(4 * n, 0); has.assign(4 * n, 0);
    build(1, 1, n);
    string out;
    char buf[64];
    while (q--) {
        int t = rd(), l = rd(), r = rd();
        if (t == 3) {
            qs = 0; qm = LLONG_MIN;
            query(1, 1, n, l, r);
            snprintf(buf, sizeof buf, "%lld %lld\n", qs, qm);
            out += buf;
        } else {
            ll x = rd();
            update(1, 1, n, l, r, t, x);
        }
    }
    fputs(out.c_str(), stdout);
}
