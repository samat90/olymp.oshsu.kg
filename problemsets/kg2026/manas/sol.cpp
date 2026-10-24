// Suffix array (prefix doubling with radix sort) + LCP. Distinct substrings in lexicographic order:
// suffix sa[i] contributes the lengths lcp[i]+1 .. n-sa[i]. For the k-th one, the suffixes that share
// it form the range [i, b] where b is the last index with min(lcp[i+1..b]) >= L; the leftmost
// occurrence is min(sa[i..b]). Both via sparse tables.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

vector<int> suffixArray(const string &s) {
    int n = s.size(), classes = 256;
    vector<int> sa(n), c(n), cnt(max(classes, n), 0);
    for (int i = 0; i < n; i++) cnt[(unsigned char)s[i]]++;
    for (int i = 1; i < classes; i++) cnt[i] += cnt[i - 1];
    for (int i = n - 1; i >= 0; i--) sa[--cnt[(unsigned char)s[i]]] = i;
    c[sa[0]] = 0; classes = 1;
    for (int i = 1; i < n; i++) { if (s[sa[i]] != s[sa[i - 1]]) classes++; c[sa[i]] = classes - 1; }
    vector<int> pn(n), cn(n);
    for (int h = 0; (1 << h) < n; h++) {
        // sort cyclic shifts of length 2^(h+1); a sentinel-free variant: compare (c[i], c[i+len] or -1)
        int len = 1 << h;
        // positions i with i + len >= n come first among equal classes (their second key is -1)
        int k = 0;
        for (int i = n - len; i < n; i++) pn[k++] = i;
        for (int i = 0; i < n; i++) if (sa[i] >= len) pn[k++] = sa[i] - len;
        fill(cnt.begin(), cnt.begin() + classes, 0);
        for (int i = 0; i < n; i++) cnt[c[pn[i]]]++;
        for (int i = 1; i < classes; i++) cnt[i] += cnt[i - 1];
        for (int i = n - 1; i >= 0; i--) sa[--cnt[c[pn[i]]]] = pn[i];
        cn[sa[0]] = 0; classes = 1;
        for (int i = 1; i < n; i++) {
            int a = sa[i], b = sa[i - 1];
            int a2 = a + len < n ? c[a + len] : -1, b2 = b + len < n ? c[b + len] : -1;
            if (c[a] != c[b] || a2 != b2) classes++;
            cn[a] = classes - 1;
        }
        c.swap(cn);
        if (classes == n) break;
    }
    return sa;
}

int main() {
    int n, q;
    if (scanf("%d %d", &n, &q) != 2) return 0;
    static char buf[400005];
    scanf("%s", buf);
    string s(buf, n);
    vector<int> sa = suffixArray(s), rk(n), lcp(n, 0);
    for (int i = 0; i < n; i++) rk[sa[i]] = i;
    for (int i = 0, h = 0; i < n; i++) {
        if (rk[i] == 0) { h = 0; continue; }
        int j = sa[rk[i] - 1];
        while (i + h < n && j + h < n && s[i + h] == s[j + h]) h++;
        lcp[rk[i]] = h;
        if (h) h--;
    }
    vector<ll> pre(n + 1, 0);
    for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + (n - sa[i] - lcp[i]);
    int LOG = 1;
    while ((1 << LOG) <= n) LOG++;
    vector<vector<int>> mn(LOG, vector<int>(n)), ms(LOG, vector<int>(n));
    mn[0] = lcp; ms[0] = sa;
    for (int j = 1; j < LOG; j++)
        for (int i = 0; i + (1 << j) <= n; i++) {
            mn[j][i] = min(mn[j - 1][i], mn[j - 1][i + (1 << (j - 1))]);
            ms[j][i] = min(ms[j - 1][i], ms[j - 1][i + (1 << (j - 1))]);
        }
    auto rmqS = [&](int l, int r) {
        int j = 31 - __builtin_clz(r - l + 1);
        return min(ms[j][l], ms[j][r - (1 << j) + 1]);
    };
    string out;
    char ob[48];
    while (q--) {
        ll k;
        scanf("%lld", &k);
        if (k > pre[n]) { out += "-1\n"; continue; }
        int i = lower_bound(pre.begin() + 1, pre.end(), k) - pre.begin() - 1;
        int L = lcp[i] + (int)(k - pre[i]);
        // extend to the right while lcp >= L, greedy over the sparse table
        int b = i;
        for (int j = LOG - 1; j >= 0; j--)
            if (b + 1 + (1 << j) - 1 < n && mn[j][b + 1] >= L) b += 1 << j;
        int st = rmqS(i, b);
        snprintf(ob, sizeof ob, "%d %d\n", st + 1, st + L);
        out += ob;
    }
    fputs(out.c_str(), stdout);
}
