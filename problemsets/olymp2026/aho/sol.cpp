// Aho-Corasick automaton of the words; states that end a word (directly or via suffix links) are removed.
// The number of good strings = sum of row 0 of T^L, T = transition counts between the allowed states.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef unsigned long long ull;
const ll MOD = 1000000007;
typedef vector<vector<ll>> M;

M mul(const M &A, const M &B) {
    int n = A.size();
    M C(n, vector<ll>(n, 0));
    for (int i = 0; i < n; i++)
        for (int k = 0; k < n; k++) {
            if (!A[i][k]) continue;
            ull a = A[i][k];
            for (int j = 0; j < n; j++) C[i][j] = (C[i][j] + a * B[k][j]) % MOD;
        }
    return C;
}

int main() {
    int sigma, k;
    ll L;
    if (scanf("%d %d %lld", &sigma, &k, &L) != 3) return 0;
    vector<array<int, 26>> go(1);
    go[0].fill(-1);
    vector<int> link(1, 0);
    vector<bool> term(1, false);
    char buf[205];
    for (int i = 0; i < k; i++) {
        scanf("%s", buf);
        int v = 0;
        for (char *c = buf; *c; c++) {
            int x = *c - 'a';
            if (go[v][x] < 0) {
                go[v][x] = go.size();
                go.push_back({});
                go.back().fill(-1);
                link.push_back(0);
                term.push_back(false);
            }
            v = go[v][x];
        }
        term[v] = true;
    }
    queue<int> q;
    for (int x = 0; x < 26; x++) {
        if (go[0][x] < 0) go[0][x] = 0;
        else link[go[0][x]] = 0, q.push(go[0][x]);
    }
    while (!q.empty()) {
        int v = q.front(); q.pop();
        term[v] = term[v] || term[link[v]];
        for (int x = 0; x < 26; x++) {
            int u = go[v][x];
            if (u < 0) go[v][x] = go[link[v]][x];
            else link[u] = go[link[v]][x], q.push(u);
        }
    }
    vector<int> id(go.size(), -1);
    int n = 0;
    for (size_t v = 0; v < go.size(); v++) if (!term[v]) id[v] = n++;
    M T(n, vector<ll>(n, 0));
    for (size_t v = 0; v < go.size(); v++) {
        if (term[v]) continue;
        for (int x = 0; x < sigma; x++) {
            int u = go[v][x];
            if (!term[u]) T[id[v]][id[u]]++;
        }
    }
    M R(n, vector<ll>(n, 0));
    for (int i = 0; i < n; i++) R[i][i] = 1;
    for (; L; L >>= 1) {
        if (L & 1) R = mul(R, T);
        T = mul(T, T);
    }
    ll ans = 0;
    for (int j = 0; j < n; j++) ans = (ans + R[0][j]) % MOD;
    printf("%lld\n", ans);
}
