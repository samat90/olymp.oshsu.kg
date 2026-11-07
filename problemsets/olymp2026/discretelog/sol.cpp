// Extended baby-step giant-step: while gcd(a, m) = g > 1, b must be divisible by g; divide b and m by g and
// carry a/g into a coefficient (checking small answers on the way). Then gcd(a, m) = 1 and
// coef * a^y = b (mod m) is solved by ordinary BSGS with x = steps + y; the smallest y is found first.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

ll solve(ll a, ll b, ll m) {
    if (m == 1) return 0;
    a %= m, b %= m;
    if (b == 1 % m) return 0;
    ll k = 0, coef = 1 % m;
    while (true) {
        ll g = __gcd(a, m);
        if (g == 1) break;
        if (b % g) return -1;
        b /= g, m /= g;
        coef = coef * (a / g) % m;
        k++;
        if (coef == b % m) return k;
        a %= m;
        b %= m;
    }
    // coef * a^y = b (mod m), gcd(a, m) = 1
    ll n = (ll)sqrtl((long double)m) + 1;
    // open addressing table: b * a^j -> j (the largest j is kept)
    int H = 1;
    while (H < 4 * n) H <<= 1;
    static vector<ll> key, valj;
    key.assign(H, -1), valj.assign(H, 0);
    auto slot = [&](ll k) { size_t h = (size_t)(k * 0x9E3779B97F4A7C15ULL >> 20) & (H - 1); while (key[h] != -1 && key[h] != k) h = (h + 1) & (H - 1); return h; };
    ll cur = b % m;
    for (ll j = 0; j < n; j++) {
        size_t h = slot(cur);
        key[h] = cur, valj[h] = j;
        cur = cur * a % m;
    }
    ll an = 1;
    for (ll i = 0; i < n; i++) an = an * a % m;
    ll g = coef % m;
    for (ll i = 1; i <= n + 1; i++) {
        g = g * an % m;
        size_t h = slot(g);
        if (key[h] == g) return k + i * n - valj[h];
    }
    return -1;
}

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ll a, b, m;
        scanf("%lld %lld %lld", &a, &b, &m);
        printf("%lld\n", solve(a, b, m));
    }
}
