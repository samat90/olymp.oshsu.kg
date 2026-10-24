// Min-cost flow with potentials and dense Dijkstra (independent check).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
int main() {
    int n;
    scanf("%d", &n);
    vector<vector<ll>> c(n, vector<ll>(n));
    for (auto &r : c) for (auto &x : r) scanf("%lld", &x);
    // bipartite: students 0..n-1, rooms n..2n-1; residual: match[] arrays
    const ll INF = LLONG_MAX / 4;
    vector<int> roomOf(n, -1), studentOf(n, -1);
    vector<ll> pu(n, 0), pv(n, 0);  // potentials
    ll total = 0;
    for (int it = 0; it < n; it++) {
        // Dijkstra from all free students over reduced costs
        vector<ll> du(n, INF), dv(n, INF);
        vector<int> prevRoom(n, -1), fromStudent(n, -1);
        vector<char> doneU(n, 0), doneV(n, 0);
        for (int i = 0; i < n; i++) if (roomOf[i] < 0) du[i] = 0;
        // dense Dijkstra over 2n vertices
        while (true) {
            int bu = -1, bv = -1; ll best = INF;
            for (int i = 0; i < n; i++) if (!doneU[i] && du[i] < best) { best = du[i]; bu = i; bv = -1; }
            for (int j = 0; j < n; j++) if (!doneV[j] && dv[j] < best) { best = dv[j]; bv = j; bu = -1; }
            if (best == INF) break;
            if (bu >= 0) {
                doneU[bu] = 1;
                for (int j = 0; j < n; j++) {
                    if (c[bu][j] < 0 || roomOf[bu] == j) continue;
                    ll nd = du[bu] + c[bu][j] + pu[bu] - pv[j];
                    if (nd < dv[j]) { dv[j] = nd; fromStudent[j] = bu; }
                }
            } else {
                doneV[bv] = 1;
                int s = studentOf[bv];
                if (s >= 0) {
                    ll nd = dv[bv] - c[s][bv] + pv[bv] - pu[s];
                    if (nd < du[s]) { du[s] = nd; prevRoom[s] = bv; }
                }
            }
        }
        int target = -1; ll bestd = INF;
        for (int j = 0; j < n; j++) if (studentOf[j] < 0 && dv[j] < bestd) { bestd = dv[j]; target = j; }
        if (target < 0) { puts("-1"); return 0; }
        for (int i = 0; i < n; i++) if (du[i] < INF) pu[i] += du[i];
        for (int j = 0; j < n; j++) if (dv[j] < INF) pv[j] += dv[j];
        // augment
        int j = target;
        while (j >= 0) {
            int s = fromStudent[j];
            int oldRoom = roomOf[s];
            roomOf[s] = j; studentOf[j] = s;
            j = (oldRoom >= 0 && prevRoom[s] == oldRoom) ? oldRoom : -1;
            if (oldRoom >= 0 && j < 0) { /* came from start */ }
        }
    }
    for (int i = 0; i < n; i++) total += c[i][roomOf[i]];
    printf("%lld\n", total);
}
