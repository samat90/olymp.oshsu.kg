// Losing positions of Wythoff's game: (A_k, B_k) and (B_k, A_k), A_k = floor(k*phi) = (k + isqrt(5k^2)) / 2,
// B_k = A_k + k. Every number is exactly one A_k or B_k (Beatty), so each pile value has one partner.
// A winning move keeps one pile and moves the other to the partner, or keeps the difference d = |a - b|
// and moves to (A_d, B_d): at most three moves.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef unsigned __int128 u128;

ll isqrt128(u128 v) {
    ll r = (ll)sqrtl((long double)v);
    while (r > 0 && (u128)r * r > v) r--;
    while ((u128)(r + 1) * (r + 1) <= v) r++;
    return r;
}
ll A(ll k) { return (ll)(((u128)k + isqrt128((u128)5 * k * k)) / 2); }

ll partner(ll v) {
    if (v == 0) return 0;
    const long double phi = (1 + sqrtl(5.0L)) / 2;
    ll k1 = (ll)(v / phi), k2 = (ll)(v / (phi * phi));
    for (ll k = max(1LL, k1 - 3); k <= k1 + 3; k++) if (A(k) == v) return v + k;
    for (ll k = max(1LL, k2 - 3); k <= k2 + 3; k++) if (A(k) + k == v) return A(k);
    return -1;
}

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ll a, b;
        scanf("%lld %lld", &a, &b);
        int cnt = 0;
        ll pa = partner(a), pb = partner(b);
        if (pa < b) cnt++;           // change the second pile
        if (pb < a) cnt++;           // change the first pile
        ll d = a > b ? a - b : b - a;
        if (A(d) < min(a, b)) cnt++;  // take the same amount from both piles
        printf("%d\n", cnt);
    }
}
