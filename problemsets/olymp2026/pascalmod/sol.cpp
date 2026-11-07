// Kummer: v_p(C(n,k)) = number of carries when adding a = k and b = n - k in base p.
// Digit DP over the base-p digits of n from the lowest one, state = (carry, carries so far capped at e,
// comparison of the lower digits of n with those of N). Digits of n are summed in three ranges at once:
// the number of digit pairs (a_i, b_i) is a linear function of n's digit, so range sums are closed forms.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef __int128 LL;
const ll MOD = 1000000007;

ll S(ll p, int cin, int cout, ll lo, ll hi) {
    ll a = cout == 0 ? cin : 0, b = cout == 0 ? p - 1 : p - 2 + cin;
    lo = max(lo, a), hi = min(hi, b);
    if (lo > hi) return 0;
    LL cnt = hi - lo + 1, sd = (LL)(lo + hi) * cnt / 2;
    LL r = cout == 0 ? sd + cnt * (1 - cin) : cnt * (p - 1 + cin) - sd;
    return (ll)(r % MOD);
}

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ll N, p;
        int e;
        scanf("%lld %lld %d", &N, &p, &e);
        vector<ll> dig;
        for (ll x = N; x; x /= p) dig.push_back(x % p);
        int L = dig.size();
        e = min(e, L + 1);
        // dp[carry][carries][flag], flag 0: less, 1: equal, 2: greater
        vector<ll> dp(2 * (e + 1) * 3, 0), nd(dp.size());
        auto id = [&](int c, int k, int f) { return (c * (e + 1) + k) * 3 + f; };
        dp[id(0, 0, 1)] = 1;
        for (int i = 0; i < L; i++) {
            fill(nd.begin(), nd.end(), 0);
            ll d = dig[i], W[2][2][3];
            for (int c = 0; c < 2; c++)
                for (int co = 0; co < 2; co++)
                    W[c][co][0] = S(p, c, co, 0, d - 1), W[c][co][1] = S(p, c, co, d, d), W[c][co][2] = S(p, c, co, d + 1, p - 1);
            for (int c = 0; c < 2; c++)
                for (int k = 0; k <= e; k++)
                    for (int f = 0; f < 3; f++) {
                        ll v = dp[id(c, k, f)];
                        if (!v) continue;
                        for (int co = 0; co < 2; co++) {
                            int nk = min(e, k + co);
                            ll *w = W[c][co];
                            ll &a0 = nd[id(co, nk, 0)], &a1 = nd[id(co, nk, f)], &a2 = nd[id(co, nk, 2)];
                            a0 = (a0 + v * w[0]) % MOD;
                            a1 = (a1 + v * w[1]) % MOD;
                            a2 = (a2 + v * w[2]) % MOD;
                        }
                    }
            swap(dp, nd);
        }
        ll small = 0;
        for (int k = 0; k < e; k++) small = (small + dp[id(0, k, 0)]) % MOD;
        ll total = (ll)((LL)N * (N + 1) / 2 % MOD);
        printf("%lld\n", ((total - small) % MOD + MOD) % MOD);
    }
}
