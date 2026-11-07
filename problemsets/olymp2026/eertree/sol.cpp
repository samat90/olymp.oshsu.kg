// Palindromic tree: every new character adds at most one new palindrome; cnt[v] counts the positions
// where v is the longest palindromic suffix, and occurrences are summed along suffix links (children
// were created after their link, so a reverse pass in creation order is enough).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
const int N = 1000005;
int nxt[N + 2][26], len_[N + 2], lnk[N + 2];
ll cnt[N + 2];
char s[N];

int main() {
    if (scanf("%1000000s", s) != 1) return 0;
    int n = strlen(s);
    // node 0: root with length -1, node 1: root with length 0
    len_[0] = -1, lnk[0] = 0, len_[1] = 0, lnk[1] = 0;
    int sz = 2, last = 1;
    for (int i = 0; i < n; i++) {
        int c = s[i] - 'a', v = last;
        while (true) {
            int l = len_[v];
            if (i - 1 - l >= 0 && s[i - 1 - l] == s[i]) break;
            v = lnk[v];
        }
        if (nxt[v][c]) { last = nxt[v][c]; cnt[last]++; continue; }
        int u = sz++;
        len_[u] = len_[v] + 2;
        if (len_[u] == 1) lnk[u] = 1;
        else {
            int w = lnk[v];
            while (true) {
                int l = len_[w];
                if (i - 1 - l >= 0 && s[i - 1 - l] == s[i]) break;
                w = lnk[w];
            }
            lnk[u] = nxt[w][c];
        }
        nxt[v][c] = u;
        last = u;
        cnt[u]++;
    }
    ll best = 0;
    for (int u = sz - 1; u >= 2; u--) {
        cnt[lnk[u]] += cnt[u];
        best = max(best, cnt[u] * len_[u]);
    }
    printf("%d %lld\n", sz - 2, best);
}
