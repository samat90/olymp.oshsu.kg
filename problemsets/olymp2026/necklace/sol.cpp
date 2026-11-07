// Burnside. A rotation by s positions splits the circle into g = gcd(s, n) cycles; a fixed colouring is a
// proper colouring of the cycle C_g: (k-1)^g + (-1)^g (k-1) (zero for g = 1). Exactly phi(n / g) rotations
// give g. Reflections: for odd n the axis crosses an edge whose ends must be equal -> 0; for even n the
// n/2 axes through two beads fix k (k-1)^(n/2) colourings (a path), the axes through edges fix none.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 1000000007;
ll pw(ll b, ll e) { ll r = 1; b %= MOD; if (b < 0) b += MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ll n, k;
        scanf("%lld %lld", &n, &k);
        vector<pair<ll, int>> f;
        ll x = n;
        for (ll p = 2; p * p <= x; p++)
            if (x % p == 0) { int c = 0; while (x % p == 0) x /= p, c++; f.push_back({p, c}); }
        if (x > 1) f.push_back({x, 1});
        // enumerate divisors d of n together with phi(n / d)
        vector<pair<ll, ll>> divs{{1, 1}};  // (d, phi(n/d)) built prime by prime
        for (auto [p, c] : f) {
            vector<pair<ll, ll>> nd;
            for (auto [d, ph] : divs) {
                ll pp = 1;
                for (int e = 0; e <= c; e++) {
                    // exponent of p in d is e, in n/d it is c - e
                    int r = c - e;
                    ll phr = r == 0 ? 1 : (p - 1);
                    for (int t = 1; t < r; t++) phr *= p;
                    nd.push_back({d * pp, ph * phr});
                    pp *= p;
                }
            }
            divs = nd;
        }
        ll km = (k - 1) % MOD, rot = 0;
        for (auto [d, ph] : divs) {
            ll P = (pw(km, d) + (d % 2 ? MOD - km : km)) % MOD;
            rot = (rot + ph % MOD * P) % MOD;
        }
        ll necklaces = rot * pw(n, MOD - 2) % MOD;
        ll refl = n % 2 ? 0 : (n / 2) % MOD * (k % MOD) % MOD * pw(km, n / 2) % MOD;
        ll bracelets = (rot + refl) % MOD * pw(2 * n, MOD - 2) % MOD;
        printf("%lld %lld\n", necklaces, bracelets);
    }
}
