// The first 2^(k+1) segments are the first 2^k segments followed by the same path traversed backwards
// and rotated clockwise around E_k = P(2^k):  P(2^k + m) = E_k + rotR(P(2^k - m) - E_k).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef pair<ll, ll> pt;
pt E[64];

pt rotR(pt a) { return {a.second, -a.first}; }

pt pos(ll N) {
    if (N == 0) return {0, 0};
    int k = 63 - __builtin_clzll(N);
    if ((1LL << k) == N) return E[k];
    ll m = N - (1LL << k);
    pt a = pos((1LL << k) - m), e = E[k];
    pt r = rotR({a.first - e.first, a.second - e.second});
    return {e.first + r.first, e.second + r.second};
}

int main() {
    E[0] = {1, 0};
    for (int k = 0; k < 62; k++) {
        pt r = rotR({-E[k].first, -E[k].second});
        E[k + 1] = {E[k].first + r.first, E[k].second + r.second};
    }
    int q;
    if (scanf("%d", &q) != 1) return 0;
    while (q--) {
        ll N;
        scanf("%lld", &N);
        pt p = pos(N);
        printf("%lld %lld\n", p.first, p.second);
    }
}
