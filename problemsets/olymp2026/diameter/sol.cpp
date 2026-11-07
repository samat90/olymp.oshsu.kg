// Farthest pairs are vertices of the strict convex hull that form an antipodal pair. Rotating calipers
// over the hull lists all antipodal pairs (with parallel edges all four combinations); the pairs at the
// maximal distance are collected in a set to avoid counting one pair twice.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef __int128 LL;
struct P { ll x, y; bool operator<(const P &o) const { return x < o.x || (x == o.x && y < o.y); } };
LL cross(P o, P a, P b) { return (LL)(a.x - o.x) * (b.y - o.y) - (LL)(a.y - o.y) * (b.x - o.x); }
LL dist(P a, P b) { return (LL)(a.x - b.x) * (a.x - b.x) + (LL)(a.y - b.y) * (a.y - b.y); }
void print128(LL v) { if (v >= 10) print128(v / 10); putchar('0' + (int)(v % 10)); }

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<P> p(n);
    for (auto &q : p) scanf("%lld %lld", &q.x, &q.y);
    sort(p.begin(), p.end());
    vector<P> h(2 * n);
    int k = 0;
    for (int i = 0; i < n; i++) {  // strict hull: collinear points removed
        while (k >= 2 && cross(h[k - 2], h[k - 1], p[i]) <= 0) k--;
        h[k++] = p[i];
    }
    for (int i = n - 2, t = k + 1; i >= 0; i--) {
        while (k >= t && cross(h[k - 2], h[k - 1], p[i]) <= 0) k--;
        h[k++] = p[i];
    }
    h.resize(k - 1);
    int m = h.size();
    if (m == 2) { print128(dist(h[0], h[1])); printf(" 1\n"); return 0; }
    set<pair<int, int>> pairs;
    auto addp = [&](int a, int b) { a %= m, b %= m; if (a != b) pairs.insert({min(a, b), max(a, b)}); };
    int j = 1;
    for (int i = 0; i < m; i++) {
        int i1 = (i + 1) % m;
        while (true) {
            int j1 = (j + 1) % m;
            LL cur = cross(h[i], h[i1], h[j]), nxt = cross(h[i], h[i1], h[j1]);
            if (nxt > cur) j = j1; else break;
        }
        int j1 = (j + 1) % m;
        addp(i, j), addp(i1, j);
        if (cross(h[i], h[i1], h[j1]) == cross(h[i], h[i1], h[j])) addp(i, j1), addp(i1, j1);
    }
    LL best = 0;
    for (auto &pr : pairs) best = max(best, dist(h[pr.first], h[pr.second]));
    ll cnt = 0;
    for (auto &pr : pairs) if (dist(h[pr.first], h[pr.second]) == best) cnt++;
    print128(best);
    printf(" %lld\n", cnt);
}
