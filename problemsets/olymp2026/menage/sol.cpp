// Women take seats of one parity in any order (2 * n!), then the men: Touchard's formula
// U(n) = sum (-1)^k 2n/(2n-k) C(2n-k, k) (n-k)!  (the k "forbidden adjacencies" form a cycle of 2n positions).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 1000000007;

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    const int MX = 2000005;
    vector<ll> f(MX), fi(MX), inv(MX);
    f[0] = 1;
    for (int i = 1; i < MX; i++) f[i] = f[i - 1] * i % MOD;
    inv[1] = 1;
    for (int i = 2; i < MX; i++) inv[i] = (MOD - (MOD / i) * inv[MOD % i] % MOD) % MOD;
    fi[0] = 1;
    for (int i = 1; i < MX; i++) fi[i] = fi[i - 1] * inv[i] % MOD;
    while (T--) {
        ll n;
        scanf("%lld", &n);
        ll U = 0;
        for (ll k = 0; k <= n; k++) {
            ll C = f[2 * n - k] * fi[k] % MOD * fi[2 * n - 2 * k] % MOD;
            ll term = 2 * n % MOD * inv[2 * n - k] % MOD * C % MOD * f[n - k] % MOD;
            U = (k & 1) ? (U - term + MOD) % MOD : (U + term) % MOD;
        }
        printf("%lld\n", 2 * f[n] % MOD * U % MOD);
    }
}
