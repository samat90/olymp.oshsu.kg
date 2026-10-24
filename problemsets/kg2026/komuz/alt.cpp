// Independent check: suffix array of the reversed melody; for prefix i the longest suffix seen
// before is the best LCP with an already inserted reversed prefix (neighbours by rank).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<int> s(n);
    for (auto &x : s) scanf("%d", &x);
    // t = reverse(s); reversed prefix i (length i) starts in t at position n - i.
    vector<int> t(s.rbegin(), s.rend());
    vector<int> sa(n), rk(n), tmp(n);
    iota(sa.begin(), sa.end(), 0);
    for (int i = 0; i < n; i++) rk[i] = t[i];
    for (int k = 1;; k <<= 1) {
        auto cmp = [&](int a, int b) {
            if (rk[a] != rk[b]) return rk[a] < rk[b];
            int ra = a + k < n ? rk[a + k] : -1, rb = b + k < n ? rk[b + k] : -1;
            return ra < rb;
        };
        sort(sa.begin(), sa.end(), cmp);
        tmp[sa[0]] = 0;
        for (int i = 1; i < n; i++) tmp[sa[i]] = tmp[sa[i - 1]] + cmp(sa[i - 1], sa[i]);
        rk = tmp;
        if (rk[sa[n - 1]] == n - 1) break;
    }
    vector<int> lcp(n, 0);  // lcp[i] = LCP(sa[i-1], sa[i])
    for (int i = 0, h = 0; i < n; i++) {
        if (rk[i] == 0) { h = 0; continue; }
        int j = sa[rk[i] - 1];
        while (i + h < n && j + h < n && t[i + h] == t[j + h]) h++;
        lcp[rk[i]] = h;
        if (h) h--;
    }
    int LOG = 1;
    while ((1 << LOG) <= n) LOG++;
    vector<vector<int>> sp(LOG, vector<int>(n));
    sp[0] = lcp;
    for (int j = 1; j < LOG; j++)
        for (int i = 0; i + (1 << j) <= n; i++) sp[j][i] = min(sp[j - 1][i], sp[j - 1][i + (1 << (j - 1))]);
    auto rmq = [&](int l, int r) {  // min lcp[l..r]
        int j = 31 - __builtin_clz(r - l + 1);
        return min(sp[j][l], sp[j][r - (1 << j) + 1]);
    };
    set<int> ranks;
    ll total = 0;
    string out;
    char buf[24];
    for (int i = 1; i <= n; i++) {
        int pos = n - i, r = rk[pos];
        int best = 0;
        auto it = ranks.lower_bound(r);
        if (it != ranks.end()) best = max(best, rmq(r + 1, *it));
        if (it != ranks.begin()) { --it; best = max(best, rmq(*it + 1, r)); }
        best = min(best, i);
        // the earlier reversed prefix is shorter, LCP is automatically bounded by its length
        total += i - best;
        ranks.insert(r);
        snprintf(buf, sizeof buf, "%lld\n", total);
        out += buf;
    }
    fputs(out.c_str(), stdout);
}
