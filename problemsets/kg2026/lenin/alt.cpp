// Independent check: the halves are split the other way (larger first half), and the sweep goes by
// value: first-half sums by increasing value, second-half sums with enough value enter a Fenwick
// tree over weights.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
int main() {
    int n; ll W, V;
    if (scanf("%d %lld %lld", &n, &W, &V) != 3) return 0;
    vector<ll> w(n), v(n);
    for (int i = 0; i < n; i++) scanf("%lld %lld", &w[i], &v[i]);
    int h = (n + 1) / 2;
    auto gen = [&](int l, int r) {
        int m = r - l;
        vector<pair<ll, ll>> res(1 << m);
        for (int mask = 0; mask < (1 << m); mask++) {
            if (mask == 0) { res[0] = {0, 0}; continue; }
            int b = __builtin_ctz(mask);
            res[mask] = {res[mask & (mask - 1)].first + w[l + b], res[mask & (mask - 1)].second + v[l + b]};
        }
        return res;
    };
    auto A = gen(0, h), B = gen(h, n);
    // condition: wa + wb <= W and va + vb >= V
    sort(A.begin(), A.end(), [](auto &x, auto &y) { return x.second < y.second; });  // increasing value
    sort(B.begin(), B.end(), [](auto &x, auto &y) { return x.second > y.second; });  // decreasing value
    vector<ll> ws;
    for (auto &b : B) ws.push_back(b.first);
    sort(ws.begin(), ws.end());
    ws.erase(unique(ws.begin(), ws.end()), ws.end());
    vector<ll> bit(ws.size() + 1, 0);
    size_t j = 0;
    ll ans = 0;
    for (auto &a : A) {
        // as a's value grows, more of B qualify: vb >= V - va
        while (j < B.size() && B[j].second >= V - a.second) {
            int i = lower_bound(ws.begin(), ws.end(), B[j].first) - ws.begin() + 1;
            for (; i <= (int)ws.size(); i += i & -i) bit[i]++;
            j++;
        }
        // count inserted with wb <= W - wa
        int i = upper_bound(ws.begin(), ws.end(), W - a.first) - ws.begin();
        for (; i > 0; i -= i & -i) ans += bit[i];
    }
    printf("%lld\n", ans);
}
