// Equilateral lattice triangles do not exist, so an isosceles triangle has exactly one apex.
// For every apex P sort the squared distances to the other points: equal distances give C(c, 2) pairs.
// Degenerate pairs (P is the midpoint of AB) are subtracted: A and 2P - A both present.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef unsigned long long ull;

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<ll> x(n), y(n);
    for (int i = 0; i < n; i++) scanf("%lld %lld", &x[i], &y[i]);
    set<pair<ll, ll>> pts;
    for (int i = 0; i < n; i++) pts.insert({x[i], y[i]});
    vector<ull> d(n);
    ll total = 0;
    for (int p = 0; p < n; p++) {
        int m = 0;
        for (int q = 0; q < n; q++)
            if (q != p) {
                ull dx = (ull)llabs(x[q] - x[p]), dy = (ull)llabs(y[q] - y[p]);
                d[m++] = dx * dx + dy * dy;
            }
        sort(d.begin(), d.begin() + m);
        for (int i = 0; i < m;) {
            int j = i;
            while (j < m && d[j] == d[i]) j++;
            ll c = j - i;
            total += c * (c - 1) / 2;
            i = j;
        }
        ll mid = 0;
        for (int q = 0; q < n; q++)
            if (q != p && pts.count({2 * x[p] - x[q], 2 * y[p] - y[q]})) mid++;
        total -= mid / 2;
    }
    printf("%lld\n", total);
}
