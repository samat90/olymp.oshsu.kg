// Walk down the quadrants in curve order (reverse order for the maximum): the first quadrant that meets
// the rectangle contains the answer. The rectangle is mapped into the quadrant's own coordinates
// (transposed for the first quadrant, reflected in the anti-diagonal for the last one).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

ll best(int k, ll x1, ll y1, ll x2, ll y2, bool wantMax) {
    if (k == 0) return 0;
    ll s = 1LL << (k - 1);
    for (int it = 0; it < 4; it++) {
        int t = wantMax ? 3 - it : it;
        ll qx = t >= 2 ? s : 0, qy = (t == 1 || t == 2) ? s : 0;
        ll ax = max(x1, qx), bx = min(x2, qx + s - 1), ay = max(y1, qy), by = min(y2, qy + s - 1);
        if (ax > bx || ay > by) continue;
        ll lx1, lx2, ly1, ly2;
        if (t == 0) lx1 = ay, lx2 = by, ly1 = ax, ly2 = bx;
        else if (t == 1) lx1 = ax, lx2 = bx, ly1 = ay - s, ly2 = by - s;
        else if (t == 2) lx1 = ax - s, lx2 = bx - s, ly1 = ay - s, ly2 = by - s;
        else lx1 = s - 1 - by, lx2 = s - 1 - ay, ly1 = 2 * s - 1 - bx, ly2 = 2 * s - 1 - ax;
        return (ll)t * s * s + best(k - 1, lx1, ly1, lx2, ly2, wantMax);
    }
    return -1;
}

int main() {
    int k, q;
    if (scanf("%d %d", &k, &q) != 2) return 0;
    while (q--) {
        ll x1, y1, x2, y2;
        scanf("%lld %lld %lld %lld", &x1, &y1, &x2, &y2);
        printf("%lld %lld\n", best(k, x1, y1, x2, y2, false), best(k, x1, y1, x2, y2, true));
    }
}
