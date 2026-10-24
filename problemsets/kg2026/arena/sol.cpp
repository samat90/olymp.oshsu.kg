// Segment tree over seats: longest free run, free prefix/suffix, free count, lazy assignment.
#include <bits/stdc++.h>
using namespace std;

static char ibuf[1 << 25];
size_t ipos = 0, ilen = 0;
inline int gc() {
    if (ipos == ilen) { ilen = fread(ibuf, 1, sizeof ibuf, stdin); ipos = 0; if (!ilen) return -1; }
    return ibuf[ipos++];
}
inline int rdc() { int c = gc(); while (c != '+' && c != '-' && c != '?') c = gc(); return c; }
inline int rd() {
    int c = gc();
    while (c < '0' || c > '9') c = gc();
    int x = 0;
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return x;
}

int n;
vector<int> pre, suf, best, cnt;
vector<signed char> lz;  // -1 none, 0 free, 1 busy

void setnode(int v, int len, int busy) {
    int f = busy ? 0 : len;
    pre[v] = suf[v] = best[v] = cnt[v] = f;
    lz[v] = busy;
}
void pull(int v, int l, int r) {
    int m = (l + r) / 2, L = m - l + 1, R = r - m;
    int a = 2 * v, b = 2 * v + 1;
    pre[v] = pre[a] == L ? L + pre[b] : pre[a];
    suf[v] = suf[b] == R ? R + suf[a] : suf[b];
    best[v] = max({best[a], best[b], suf[a] + pre[b]});
    cnt[v] = cnt[a] + cnt[b];
}
void push(int v, int l, int r) {
    if (lz[v] < 0) return;
    int m = (l + r) / 2;
    setnode(2 * v, m - l + 1, lz[v]);
    setnode(2 * v + 1, r - m, lz[v]);
    lz[v] = -1;
}
void build(int v, int l, int r) {
    setnode(v, r - l + 1, 0);
    lz[v] = -1;
    if (l == r) return;
    int m = (l + r) / 2;
    build(2 * v, l, m); build(2 * v + 1, m + 1, r);
}
void assign(int v, int l, int r, int ql, int qr, int busy) {
    if (qr < l || r < ql) return;
    if (ql <= l && r <= qr) { setnode(v, r - l + 1, busy); return; }
    push(v, l, r);
    int m = (l + r) / 2;
    assign(2 * v, l, m, ql, qr, busy);
    assign(2 * v + 1, m + 1, r, ql, qr, busy);
    pull(v, l, r);
}
int countfree(int v, int l, int r, int ql, int qr) {
    if (qr < l || r < ql) return 0;
    if (ql <= l && r <= qr) return cnt[v];
    push(v, l, r);
    int m = (l + r) / 2;
    return countfree(2 * v, l, m, ql, qr) + countfree(2 * v + 1, m + 1, r, ql, qr);
}
int findfirst(int k) {  // leftmost start of k consecutive free seats, best[1] >= k
    int v = 1, l = 1, r = n;
    while (l < r) {
        push(v, l, r);
        int m = (l + r) / 2;
        if (best[2 * v] >= k) { v = 2 * v; r = m; }
        else if (suf[2 * v] + pre[2 * v + 1] >= k) return m - suf[2 * v] + 1;
        else { v = 2 * v + 1; l = m + 1; }
    }
    return l;
}

int main() {
    n = rd();
    int q = rd();
    pre.assign(4 * n, 0); suf.assign(4 * n, 0); best.assign(4 * n, 0); cnt.assign(4 * n, 0); lz.assign(4 * n, -1);
    build(1, 1, n);
    string out;
    char buf[32];
    auto range = [&](int l, int r, int b) {
        if (l <= r) assign(1, 1, n, l, r, b);
        else { assign(1, 1, n, l, n, b); assign(1, 1, n, 1, r, b); }
    };
    while (q--) {
        int c = rdc();
        if (c == '+') {
            int k = rd();
            int s = 0;
            if (k <= n) {
                if (best[1] >= k) s = findfirst(k);
                else if (suf[1] > 0 && suf[1] + pre[1] >= k) s = n - suf[1] + 1;
            }
            if (s) range(s, (s + k - 2) % n + 1, 1);
            snprintf(buf, sizeof buf, "%d\n", s);
            out += buf;
        } else {
            int l = rd(), r = rd();
            if (c == '-') range(l, r, 0);
            else {
                int f = l <= r ? countfree(1, 1, n, l, r) : countfree(1, 1, n, l, n) + countfree(1, 1, n, 1, r);
                snprintf(buf, sizeof buf, "%d\n", f);
                out += buf;
            }
        }
    }
    fputs(out.c_str(), stdout);
}
