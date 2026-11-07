// Occurrences inside the blocks T_j (prefix of length 2^j) and their complements satisfy
// cnt[j+1][c] = cnt[j][c] + cnt[j][1-c] + (windows across the middle). A prefix of length N is a chain
// of such blocks (one per set bit of N); windows that cross a block border are checked directly.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int L;
char pat[64];
inline int t(ll i) { return __builtin_popcountll(i) & 1; }
bool match(ll i, int c) {  // window at absolute position i in the string t[] xor c
    for (int x = 0; x < L; x++)
        if ((t(i + x) ^ c) != pat[x] - '0') return false;
    return true;
}

int main() {
    int q;
    if (scanf("%d", &q) != 1) return 0;
    while (q--) {
        ll N;
        scanf("%lld %s", &N, pat);
        L = strlen(pat);
        static ll cnt[62][2];
        for (int c = 0; c < 2; c++) cnt[0][c] = (L == 1 && pat[0] - '0' == c);
        for (int j = 0; j + 1 < 62; j++)
            for (int c = 0; c < 2; c++) {
                ll cross = 0, B = 1LL << j;
                for (ll i = max(0LL, B - L + 1); i < B; i++)
                    if (i + L <= 2 * B && match(i, c)) cross++;
                cnt[j + 1][c] = cnt[j][c] + cnt[j][1 - c] + cross;
            }
        ll S = 0, total = 0;
        vector<ll> borders;
        for (int b = 60; b >= 0; b--)
            if (N >> b & 1) {
                total += cnt[b][t(S)];
                if (S) borders.push_back(S);
                S += 1LL << b;
            }
        set<ll> cand;
        for (ll B : borders)
            for (ll i = max(0LL, B - L + 1); i < B; i++)
                if (i + L <= N) cand.insert(i);
        for (ll i : cand)
            if (match(i, 0)) total++;
        printf("%lld\n", total);
    }
}
