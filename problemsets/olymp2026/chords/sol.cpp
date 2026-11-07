// Euler's formula: parts = 1 + m + (number of crossing pairs), even with shared nails.
// Chords (a < b), (c < d) cross iff a < c < b < d. For chord i: crossings to the right =
//   #{j : a_i < a_j < b_i} - #{j : a_j > a_i, b_j < b_i} - #{j : b_j = b_i, a_j > a_i}
// (left ends inside, minus nested chords, minus chords that end on the same nail).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    int m;
    if (scanf("%d", &m) != 1) return 0;
    vector<ll> a(m), b(m);
    for (int i = 0; i < m; i++) { scanf("%lld %lld", &a[i], &b[i]); if (a[i] > b[i]) swap(a[i], b[i]); }
    vector<ll> la(a.begin(), a.end());
    sort(la.begin(), la.end());
    vector<ll> vals(b.begin(), b.end());
    sort(vals.begin(), vals.end());
    vals.erase(unique(vals.begin(), vals.end()), vals.end());
    int K = vals.size();
    vector<int> bit(K + 1, 0);
    auto add = [&](int i) { for (i++; i <= K; i += i & -i) bit[i]++; };
    auto sum = [&](int i) { int s = 0; for (; i > 0; i -= i & -i) s += bit[i]; return s; };  // ranks < i
    vector<pair<ll, int>> byA(m);  // (a, rank of b), sorted by a decreasing
    for (int i = 0; i < m; i++) byA[i] = {a[i], int(lower_bound(vals.begin(), vals.end(), b[i]) - vals.begin())};
    sort(byA.begin(), byA.end(), greater<pair<ll, int>>());
    ll cross = 0;
    // A_i: left ends strictly inside (a_i, b_i)
    for (int i = 0; i < m; i++)
        cross += (lower_bound(la.begin(), la.end(), b[i]) - la.begin()) - (upper_bound(la.begin(), la.end(), a[i]) - la.begin());
    // N_i: nested chords, inserted with larger a
    for (int t = 0; t < m;) {
        int u = t;
        while (u < m && byA[u].first == byA[t].first) u++;
        for (int z = t; z < u; z++) cross -= sum(byA[z].second);
        for (int z = t; z < u; z++) add(byA[z].second);
        t = u;
    }
    // S_i: same right end, larger left end
    vector<pair<ll, ll>> byB(m);
    for (int i = 0; i < m; i++) byB[i] = {b[i], a[i]};
    sort(byB.begin(), byB.end());
    for (int i = 0; i < m;) {
        int j = i;
        while (j < m && byB[j].first == byB[i].first) j++;
        for (int t = i; t < j; t++) cross -= j - (upper_bound(byB.begin() + i, byB.begin() + j, byB[t]) - byB.begin());
        i = j;
    }
    printf("%lld\n", 1 + (ll)m + cross);
}
