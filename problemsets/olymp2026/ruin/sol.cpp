// Gambler's ruin. With p = x/y, q = 1 - p, r = q/p and N = a + b the expected duration is
// a*b when p = q, otherwise a/(q-p) - N/(q-p) * (1 - r^a)/(1 - r^N). Everything is computed mod P;
// the exponents are reduced mod P-1 (r is not divisible by P).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef unsigned long long ull;
const ll MOD = 998244353;
ll pw(ll b, ull e) { ll r = 1; b %= MOD; if (b < 0) b += MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }
ll inv(ll v) { return pw(v, MOD - 2); }

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ull a, b; ll x, y;
        scanf("%llu %llu %lld %lld", &a, &b, &x, &y);
        if (2 * x == y) { printf("%lld\n", (ll)(a % MOD) * (ll)(b % MOD) % MOD); continue; }
        ll p = x % MOD * inv(y) % MOD, q = (y - x) % MOD * inv(y) % MOD;
        ll r = (y - x) % MOD * inv(x) % MOD;
        unsigned __int128 N = (unsigned __int128)a + b;
        ll ra = pw(r, a % (MOD - 1)), rN = pw(r, (ull)(N % (MOD - 1)));
        ll iqp = inv((q - p + MOD) % MOD);
        ll A = (ll)(a % MOD) * iqp % MOD;
        ll Bn = (ll)(N % MOD) * iqp % MOD * ((1 - ra + MOD) % MOD) % MOD * inv((1 - rN + MOD) % MOD) % MOD;
        printf("%lld\n", (A - Bn + MOD) % MOD);
    }
}
