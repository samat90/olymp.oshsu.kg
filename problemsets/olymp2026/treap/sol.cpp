// Implicit treap: split by size, merge, lazy "reversed" flag; nodes keep subtree size, sum and max.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const int MX = 400005;
int L[MX], R[MX], sz[MX], pr[MX], tot = 0;
ll val[MX], sm[MX], mxv[MX];
bool rev[MX];
mt19937 rng(20261108);
int nw(ll v) { int t = ++tot; val[t] = sm[t] = mxv[t] = v; sz[t] = 1; pr[t] = rng(); return t; }
void pull(int t) {
    sz[t] = 1 + sz[L[t]] + sz[R[t]];
    sm[t] = val[t] + sm[L[t]] + sm[R[t]];
    mxv[t] = val[t];
    if (L[t]) mxv[t] = max(mxv[t], mxv[L[t]]);
    if (R[t]) mxv[t] = max(mxv[t], mxv[R[t]]);
}
void push(int t) {
    if (t && rev[t]) {
        swap(L[t], R[t]);
        if (L[t]) rev[L[t]] ^= 1;
        if (R[t]) rev[R[t]] ^= 1;
        rev[t] = 0;
    }
}
void split(int t, int k, int &a, int &b) {  // first k elements to a
    if (!t) { a = b = 0; return; }
    push(t);
    if (sz[L[t]] < k) split(R[t], k - sz[L[t]] - 1, R[t], b), a = t;
    else split(L[t], k, a, L[t]), b = t;
    pull(t);
}
int merge(int a, int b) {
    if (!a || !b) return a ? a : b;
    if (pr[a] > pr[b]) { push(a); R[a] = merge(R[a], b); pull(a); return a; }
    push(b); L[b] = merge(a, L[b]); pull(b); return b;
}
int main() {
    int n, q;
    if (scanf("%d %d", &n, &q) != 2) return 0;
    int root = 0;
    for (int i = 0; i < n; i++) { ll v; scanf("%lld", &v); root = merge(root, nw(v)); }
    while (q--) {
        int t; scanf("%d", &t);
        if (t == 1 || t == 4 || t == 5) {
            int l, r; scanf("%d %d", &l, &r);
            int a, b, c;
            split(root, l - 1, a, b);
            split(b, r - l + 1, b, c);
            if (t == 1) rev[b] ^= 1;
            else if (t == 4) printf("%lld\n", sm[b]);
            else printf("%lld\n", mxv[b]);
            root = merge(merge(a, b), c);
        } else if (t == 2) {
            int p; ll x; scanf("%d %lld", &p, &x);
            int a, b;
            split(root, p, a, b);
            root = merge(merge(a, nw(x)), b);
        } else {
            int p; scanf("%d", &p);
            int a, b, c;
            split(root, p - 1, a, b);
            split(b, 1, b, c);
            root = merge(a, c);
        }
    }
}
