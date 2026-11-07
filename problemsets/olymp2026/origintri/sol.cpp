// A triangle misses the origin iff its three directions fit in a half-plane. Sort the stars by angle;
// for each star i let k_i = number of stars within the open half-turn after it: triangles with i as the
// first vertex of such a half-plane are C(k_i, 2). Answer = C(n, 3) - sum C(k_i, 2) (two pointers).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
struct P { ll x, y; };
int half(const P &p) { return (p.y < 0 || (p.y == 0 && p.x < 0)) ? 1 : 0; }
ll cross(const P &a, const P &b) { return a.x * b.y - a.y * b.x; }

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<P> p(n);
    for (auto &q : p) scanf("%lld %lld", &q.x, &q.y);
    sort(p.begin(), p.end(), [](const P &a, const P &b) {
        int ha = half(a), hb = half(b);
        if (ha != hb) return ha < hb;
        return cross(a, b) > 0;
    });
    ll total = (ll)n * (n - 1) * (n - 2) / 6, bad = 0;
    int j = 0;
    for (int i = 0; i < n; i++) {
        if (j < i + 1) j = i + 1;
        while (j < i + n && cross(p[i], p[j % n]) > 0) j++;
        ll k = j - i - 1;
        bad += k * (k - 1) / 2;
    }
    printf("%lld\n", total - bad);
}
