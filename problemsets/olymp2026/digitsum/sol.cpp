// For every digit sum S (1..162): f[len][need][rem] = number of digit strings of length len with digit sum
// `need` that, appended to a prefix with remainder rem (mod S), give remainder 0. Then count(X) walks the
// digits of X (tight prefix) and adds table values; all queries are answered for one S at a time.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    vector<ll> lo(T), hi(T), res(T, 0);
    for (int i = 0; i < T; i++) scanf("%lld %lld", &lo[i], &hi[i]);
    static ll f[20][163][163];
    for (int S = 1; S <= 162; S++) {
        // f[0][0][0] = 1; f[len][need][rem] = sum_d f[len-1][need-d][(rem*10+d) % S]
        for (int need = 0; need <= S; need++) for (int r = 0; r < S; r++) f[0][need][r] = (need == 0 && r == 0);
        for (int len = 1; len <= 19; len++)
            for (int need = 0; need <= S; need++)
                for (int r = 0; r < S; r++) {
                    if (need > 9 * len) { f[len][need][r] = 0; continue; }
                    ll v = 0;
                    int base = r * 10 % S;
                    for (int d = 0; d <= 9 && d <= need; d++) {
                        int nr = base + d;
                        while (nr >= S) nr -= S;
                        v += f[len - 1][need - d][nr];
                    }
                    f[len][need][r] = v;
                }
        auto count = [&](ll X) -> ll {  // numbers in [0, X] with digit sum S and divisible by S
            if (X < 0) return 0;
            string d = to_string(X);
            int L = d.size(), sum = 0, rem = 0;
            ll c = 0;
            for (int i = 0; i < L; i++) {
                int cur = d[i] - '0';
                for (int x = 0; x < cur; x++) {
                    int ns = sum + x;
                    if (ns > S) break;
                    c += f[L - 1 - i][S - ns][(rem * 10 + x) % S];
                }
                sum += cur, rem = (rem * 10 + cur) % S;
                if (sum > S) return c;
            }
            if (sum == S && rem == 0) c++;
            return c;
        };
        for (int i = 0; i < T; i++) res[i] += count(hi[i]) - count(lo[i] - 1);
    }
    for (int i = 0; i < T; i++) printf("%lld\n", res[i]);
}
