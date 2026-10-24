// Meet in the middle: all (weight, value) sums of each half; sweep the first half by decreasing
// weight, add the second half's sums that fit into a Fenwick tree over values, count values >= need.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

vector<pair<ll, ll>> sums(const vector<ll> &w, const vector<ll> &v) {
    vector<pair<ll, ll>> res{{0, 0}};
    for (size_t i = 0; i < w.size(); i++) {
        size_t m = res.size();
        for (size_t j = 0; j < m; j++) res.push_back({res[j].first + w[i], res[j].second + v[i]});
    }
    return res;
}

int main() {
    int n;
    ll W, V;
    if (scanf("%d %lld %lld", &n, &W, &V) != 3) return 0;
    vector<ll> w(n), v(n);
    for (int i = 0; i < n; i++) scanf("%lld %lld", &w[i], &v[i]);
    int h = n / 2;
    auto A = sums(vector<ll>(w.begin(), w.begin() + h), vector<ll>(v.begin(), v.begin() + h));
    auto B = sums(vector<ll>(w.begin() + h, w.end()), vector<ll>(v.begin() + h, v.end()));
    sort(A.begin(), A.end(), greater<>());  // decreasing weight
    sort(B.begin(), B.end());               // increasing weight
    vector<ll> vals(B.size());
    for (size_t i = 0; i < B.size(); i++) vals[i] = B[i].second;
    sort(vals.begin(), vals.end());
    vals.erase(unique(vals.begin(), vals.end()), vals.end());
    int K = vals.size();
    vector<ll> bit(K + 1, 0);
    ll inserted = 0;
    auto add = [&](int i) { for (i++; i <= K; i += i & -i) bit[i]++; };
    auto prefix = [&](int i) { ll s = 0; for (; i > 0; i -= i & -i) s += bit[i]; return s; };  // count of ranks < i
    size_t j = 0;
    ll answer = 0;
    for (auto &a : A) {
        if (a.first > W) continue;
        while (j < B.size() && B[j].first <= W - a.first) {
            add(lower_bound(vals.begin(), vals.end(), B[j].second) - vals.begin());
            inserted++;
            j++;
        }
        ll need = V - a.second;
        int r = lower_bound(vals.begin(), vals.end(), need) - vals.begin();
        answer += inserted - prefix(r);
    }
    printf("%lld\n", answer);
}
