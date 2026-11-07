// Mo's algorithm with modifications: queries are (l, r, t); sorted by (l / B, r / B, t) with B ~ n^(2/3).
// Moving a border changes one count: (c+1)^2 - c^2 = 2c + 1. Applying an update inside the window
// replaces one colour. Colours are compressed first.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    int n, q;
    if (scanf("%d %d", &n, &q) != 2) return 0;
    vector<int> c(n);
    vector<int> all;
    for (auto &x : c) scanf("%d", &x), all.push_back(x);
    struct Upd { int p, from, to; };
    struct Qry { int l, r, t, id; };
    vector<Upd> ups;
    vector<Qry> qs;
    vector<int> cur = c;
    vector<array<int, 3>> raw(q);
    for (int i = 0; i < q; i++) {
        scanf("%d %d %d", &raw[i][0], &raw[i][1], &raw[i][2]);
        if (raw[i][0] == 1) all.push_back(raw[i][2]);
    }
    sort(all.begin(), all.end());
    all.erase(unique(all.begin(), all.end()), all.end());
    auto id = [&](int x) { return int(lower_bound(all.begin(), all.end(), x) - all.begin()); };
    for (auto &x : c) x = id(x);
    cur = c;
    for (int i = 0; i < q; i++) {
        if (raw[i][0] == 1) {
            int p = raw[i][1] - 1, x = id(raw[i][2]);
            ups.push_back({p, cur[p], x});
            cur[p] = x;
        } else qs.push_back({raw[i][1] - 1, raw[i][2] - 1, (int)ups.size(), (int)qs.size()});
    }
    int B = max(1, (int)cbrt((double)n * n));
    if (ups.empty()) B = max(1, (int)sqrt((double)n));
    sort(qs.begin(), qs.end(), [&](const Qry &a, const Qry &b) {
        if (a.l / B != b.l / B) return a.l < b.l;
        if (ups.empty()) return ((a.l / B) & 1) ? a.r > b.r : a.r < b.r;
        if (a.r / B != b.r / B) return ((a.l / B) & 1) ? a.r > b.r : a.r < b.r;
        return ((a.r / B) & 1) ? a.t > b.t : a.t < b.t;
    });
    vector<ll> cnt(all.size() + 1, 0), ans(qs.size());
    ll val = 0;
    int L = 0, R = -1, T = 0;
    vector<int> a = c;
    auto addc = [&](int col) { val += 2 * cnt[col] + 1; cnt[col]++; };
    auto remc = [&](int col) { cnt[col]--; val -= 2 * cnt[col] + 1; };
    auto applyU = [&](int k, bool fwd) {
        int p = ups[k].p, to = fwd ? ups[k].to : ups[k].from;
        if (L <= p && p <= R) remc(a[p]), addc(to);
        a[p] = to;
    };
    for (auto &qq : qs) {
        while (T < qq.t) applyU(T++, true);
        while (T > qq.t) applyU(--T, false);
        while (R < qq.r) addc(a[++R]);
        while (L > qq.l) addc(a[--L]);
        while (R > qq.r) remc(a[R--]);
        while (L < qq.l) remc(a[L++]);
        ans[qq.id] = val;
    }
    for (auto v : ans) printf("%lld\n", v);
}
