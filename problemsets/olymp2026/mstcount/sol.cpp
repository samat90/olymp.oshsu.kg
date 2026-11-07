// Edges are processed in groups of equal weight. Before a group the components of the cheaper edges
// are fixed; inside the group every connected piece of the "component graph" needs a spanning tree,
// and the choices in different pieces are independent: multiply their counts (Kirchhoff, determinant mod p).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const ll MOD = 1000000007;

ll pw(ll b, ll e) { ll r = 1; b %= MOD; for (; e; e >>= 1, b = b * b % MOD) if (e & 1) r = r * b % MOD; return r; }

ll det(vector<vector<ll>> a) {
    int n = a.size();
    ll res = 1;
    for (int c = 0; c < n; c++) {
        int p = -1;
        for (int r = c; r < n; r++) if (a[r][c]) { p = r; break; }
        if (p < 0) return 0;
        if (p != c) swap(a[p], a[c]), res = MOD - res;
        res = res * a[c][c] % MOD;
        ll inv = pw(a[c][c], MOD - 2);
        for (int r = c + 1; r < n; r++) {
            if (!a[r][c]) continue;
            ll f = a[r][c] * inv % MOD;
            for (int k = c; k < n; k++) a[r][k] = ((a[r][k] - f * a[c][k]) % MOD + MOD) % MOD;
        }
    }
    return res % MOD;
}

vector<int> par;
int find(int x) { return par[x] == x ? x : par[x] = find(par[x]); }

int main() {
    int n, m;
    if (scanf("%d %d", &n, &m) != 2) return 0;
    vector<array<ll, 3>> e(m);
    for (auto &x : e) scanf("%lld %lld %lld", &x[1], &x[2], &x[0]);
    sort(e.begin(), e.end());
    par.resize(n + 1);
    iota(par.begin(), par.end(), 0);
    ll cost = 0, ways = 1;
    int comps = n;
    for (int i = 0; i < m;) {
        int j = i;
        while (j < m && e[j][0] == e[i][0]) j++;
        // group [i, j): graph on the current components
        map<int, vector<int>> adj;
        vector<pair<int, int>> ge;
        for (int t = i; t < j; t++) {
            int a = find(e[t][1]), b = find(e[t][2]);
            if (a != b) ge.push_back({a, b});
        }
        // pieces of the component graph
        map<int, int> lp;
        function<int(int)> f2 = [&](int x) { return lp[x] == x ? x : lp[x] = f2(lp[x]); };
        for (auto &g : ge) { if (!lp.count(g.first)) lp[g.first] = g.first; if (!lp.count(g.second)) lp[g.second] = g.second; }
        for (auto &g : ge) { int a = f2(g.first), b = f2(g.second); if (a != b) lp[a] = b; }
        map<int, vector<int>> verts;
        for (auto &kv : lp) verts[f2(kv.first)].push_back(kv.first);
        map<int, vector<pair<int, int>>> pe;
        for (auto &g : ge) pe[f2(g.first)].push_back(g);
        for (auto &kv : verts) {
            auto &vs = kv.second;
            int s = vs.size();
            map<int, int> idx;
            for (int t = 0; t < s; t++) idx[vs[t]] = t;
            vector<vector<ll>> L(s - 1, vector<ll>(s - 1, 0));
            for (auto &g : pe[kv.first]) {
                int a = idx[g.first], b = idx[g.second];
                if (a < s - 1) L[a][a]++;
                if (b < s - 1) L[b][b]++;
                if (a < s - 1 && b < s - 1) L[a][b] = (L[a][b] + MOD - 1) % MOD, L[b][a] = (L[b][a] + MOD - 1) % MOD;
            }
            ways = ways * det(L) % MOD;
            cost += (ll)(s - 1) * e[i][0];
            comps -= s - 1;
        }
        for (auto &g : ge) { int a = find(g.first), b = find(g.second); if (a != b) par[a] = b; }
        i = j;
    }
    if (comps != 1) { puts("-1"); return 0; }
    printf("%lld %lld\n", cost, ways);
}
