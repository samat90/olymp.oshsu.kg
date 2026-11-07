// Circular merging = best segment of length n in the doubled array. Interval DP with Knuth's optimisation
// (the merge cost is the segment sum, which satisfies the quadrangle inequality): O((2n)^2).
// Only segments of length <= n are needed: dp[i][len], opt[i][len].
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<ll> a(2 * n);
    for (int i = 0; i < n; i++) scanf("%lld", &a[i]), a[i + n] = a[i];
    int N = 2 * n;
    vector<ll> pre(N + 1, 0);
    for (int i = 0; i < N; i++) pre[i + 1] = pre[i] + a[i];
    vector<vector<ll>> dp(N, vector<ll>(n + 1, 0));
    vector<vector<int>> opt(N, vector<int>(n + 1, 0));
    for (int i = 0; i < N; i++) opt[i][1] = i;
    for (int len = 2; len <= n; len++)
        for (int i = 0; i + len - 1 < N; i++) {
            int j = i + len - 1;
            ll best = LLONG_MAX;
            int lo = opt[i][len - 1], hi = min(j - 1, opt[i + 1][len - 1]), bk = lo;
            for (int k = lo; k <= hi; k++) {
                ll v = dp[i][k - i + 1] + dp[k + 1][j - k];
                if (v < best) best = v, bk = k;
            }
            dp[i][len] = best + pre[j + 1] - pre[i];
            opt[i][len] = bk;
        }
    ll ans = LLONG_MAX;
    for (int i = 0; i < n; i++) ans = min(ans, dp[i][n]);
    puts(std::to_string(ans).c_str());
}
