// dp[j] = s[j] + x[j]^2 + min_i (dp[i] + x[i]^2 - 2 x[i] x[j]). Slopes -2x[i] decrease and the query points
// x[j] increase, so a monotone convex hull trick (deque) gives O(n). Values are compared in __int128.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef __int128 LL;

struct Line { LL k, b; LL at(LL x) const { return k * x + b; } };
// l2 is useless if l1 and l3 meet before l1 and l2 do
bool bad(const Line &l1, const Line &l2, const Line &l3) {
    return (l3.b - l1.b) * (l1.k - l2.k) <= (l2.b - l1.b) * (l1.k - l3.k);
}

int main() {
    int n;
    if (scanf("%d", &n) != 1) return 0;
    vector<ll> x(n), s(n);
    for (auto &v : x) scanf("%lld", &v);
    for (auto &v : s) scanf("%lld", &v);
    vector<LL> dp(n);
    dp[0] = s[0];
    deque<Line> hull;
    auto add = [&](int i) {
        Line l{-2 * (LL)x[i], dp[i] + (LL)x[i] * x[i]};
        while (hull.size() >= 2 && bad(hull[hull.size() - 2], hull.back(), l)) hull.pop_back();
        hull.push_back(l);
    };
    add(0);
    for (int j = 1; j < n; j++) {
        while (hull.size() >= 2 && hull[1].at(x[j]) <= hull[0].at(x[j])) hull.pop_front();
        dp[j] = hull[0].at(x[j]) + (LL)x[j] * x[j] + s[j];
        add(j);
    }
    printf("%lld\n", (ll)dp[n - 1]);
}
