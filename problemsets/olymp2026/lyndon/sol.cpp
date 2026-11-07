// Duval's algorithm gives the Lyndon factorisation of s; run on s + s it also gives the start of the
// minimal rotation (the last factor start before position n). Distinct rotations: the smallest period p
// (from the prefix function) if p divides n, otherwise n.
#include <bits/stdc++.h>
using namespace std;

int main() {
    static char buf[1000005];
    if (scanf("%1000000s", buf) != 1) return 0;
    string s(buf);
    int n = s.size();
    // Lyndon factorisation of s
    long long factors = 0;
    for (int i = 0; i < n;) {
        int j = i + 1, k = i;
        while (j < n && s[k] <= s[j]) { if (s[k] < s[j]) k = i; else k++; j++; }
        while (i <= k) i += j - k, factors++;
    }
    // minimal rotation via Duval on s + s
    string t = s + s;
    int ans = 0;
    for (int i = 0; i < n;) {
        ans = i;
        int j = i + 1, k = i;
        while (j < 2 * n && t[k] <= t[j]) { if (t[k] < t[j]) k = i; else k++; j++; }
        while (i <= k) i += j - k;
    }
    vector<int> pi(n, 0);
    for (int i = 1; i < n; i++) {
        int k = pi[i - 1];
        while (k && s[i] != s[k]) k = pi[k - 1];
        if (s[i] == s[k]) k++;
        pi[i] = k;
    }
    int p = n - pi[n - 1], distinct = n % p == 0 ? p : n;
    // the smallest index with the minimal rotation: rotations repeat with period `distinct`
    printf("%d %d %lld\n", ans % distinct + 1, distinct, factors);
}
