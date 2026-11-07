// Answer = sum over primes p, d of mu(d) [A/pd][B/pd] = sum_T f(T) [A/T][B/T], f(T) = sum_{p | T} mu(T/p).
// f is computed by a linear sieve; [A/T][B/T] takes O(sqrt) different values (blocks).
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

int main() {
    int q;
    if (scanf("%d", &q) != 1) return 0;
    vector<pair<int, int>> qs(q);
    int M = 1;
    for (auto &x : qs) scanf("%d %d", &x.first, &x.second), M = max({M, x.first, x.second});
    vector<signed char> mu(M + 1, 0);
    vector<int> f(M + 1, 0), primes;
    vector<bool> comp(M + 1, false);
    mu[1] = 1;
    for (int i = 2; i <= M; i++) {
        if (!comp[i]) primes.push_back(i), mu[i] = -1, f[i] = 1;
        for (int p : primes) {
            ll t = (ll)i * p;
            if (t > M) break;
            comp[t] = true;
            if (i % p == 0) { mu[t] = 0; f[t] = mu[i]; break; }
            mu[t] = -mu[i];
            f[t] = -f[i] + mu[i];
        }
    }
    for (int i = 1; i <= M; i++) f[i] += f[i - 1];
    for (auto [A, B] : qs) {
        ll res = 0;
        int lim = min(A, B);
        for (int T = 1, nx; T <= lim; T = nx + 1) {
            nx = min(A / (A / T), B / (B / T));
            res += (ll)(f[nx] - f[T - 1]) * (A / T) * (B / T);
        }
        printf("%lld\n", res);
    }
}
