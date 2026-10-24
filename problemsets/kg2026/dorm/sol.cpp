// Hungarian algorithm O(n^3); forbidden pairs get a huge cost.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll BIG = 1000000000000LL;  // larger than any real assignment

static char ibuf[1 << 25];
size_t ipos = 0, ilen = 0;
inline int gc() {
    if (ipos == ilen) { ilen = fread(ibuf, 1, sizeof ibuf, stdin); ipos = 0; if (!ilen) return -1; }
    return ibuf[ipos++];
}
inline ll rd() {
    int c = gc();
    while (c != '-' && (c < '0' || c > '9')) c = gc();
    bool neg = false;
    if (c == '-') { neg = true; c = gc(); }
    ll x = 0;
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return neg ? -x : x;
}

int main() {
    int n = rd();
    vector<vector<ll>> a(n + 1, vector<ll>(n + 1));
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= n; j++) { ll x = rd(); a[i][j] = x < 0 ? BIG : x; }
    const ll INF = LLONG_MAX / 4;
    vector<ll> u(n + 1), v(n + 1);
    vector<int> p(n + 1), way(n + 1);
    for (int i = 1; i <= n; i++) {
        p[0] = i;
        int j0 = 0;
        vector<ll> minv(n + 1, INF);
        vector<char> used(n + 1, false);
        do {
            used[j0] = true;
            int i0 = p[j0], j1 = 0;
            ll delta = INF;
            for (int j = 1; j <= n; j++)
                if (!used[j]) {
                    ll cur = a[i0][j] - u[i0] - v[j];
                    if (cur < minv[j]) { minv[j] = cur; way[j] = j0; }
                    if (minv[j] < delta) { delta = minv[j]; j1 = j; }
                }
            for (int j = 0; j <= n; j++)
                if (used[j]) { u[p[j]] += delta; v[j] -= delta; }
                else minv[j] -= delta;
            j0 = j1;
        } while (p[j0] != 0);
        do { int j1 = way[j0]; p[j0] = p[j1]; j0 = j1; } while (j0);
    }
    ll cost = 0;
    for (int j = 1; j <= n; j++) cost += a[p[j]][j];
    printf("%lld\n", cost >= BIG ? -1LL : cost);
}
