// Erdos-Gallai in O(n log n): sort decreasingly; for each k the right part sum_{i>k} min(d_i, k) is
// (number of i > k with d_i >= k) * k + (sum of the d_i < k among i > k), found with a pointer.
// A graphical sequence has a connected realization iff n = 1, or all d_i >= 1 and sum >= 2(n - 1).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        int n;
        scanf("%d", &n);
        vector<ll> d(n);
        ll sum = 0;
        for (auto &x : d) scanf("%lld", &x), sum += x;
        sort(d.rbegin(), d.rend());
        bool ok = sum % 2 == 0;
        vector<ll> pre(n + 1, 0);
        for (int i = 0; i < n; i++) pre[i + 1] = pre[i] + d[i];
        // p = first index (0-based) with d[p] < k; d is non-increasing
        int p = n;
        for (ll k = 1; k <= n && ok; k++) {
            while (p > 0 && d[p - 1] < k) p--;
            ll left = pre[k];
            int from = max<ll>(k, p);  // indices >= from have d < k
            ll big = from - k;          // indices k..from-1 have d >= k
            ll right = k * (k - 1) + big * k + (pre[n] - pre[from]);
            if (left > right) ok = false;
        }
        bool conn = ok && (n == 1 || (d[n - 1] >= 1 && sum >= 2LL * (n - 1)));
        printf("%s %s\n", ok ? "YES" : "NO", conn ? "YES" : "NO");
    }
}
