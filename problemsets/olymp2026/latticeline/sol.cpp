// Count = sum_{x=1}^{X} floor((c - a x) / b), X = floor((c - b) / a). With i = X - x this is
// floor_sum(X, b, a, c - aX) = sum_{i<X} floor((a i + r) / b), computed by the Euclid-like recursion.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef unsigned long long ull;
typedef __int128 LL;

LL floor_sum(LL n, LL m, LL a, LL b) {  // sum_{i=0}^{n-1} floor((a i + b) / m), a, b >= 0
    LL ans = 0;
    while (true) {
        if (a >= m) ans += n * (n - 1) / 2 * (a / m), a %= m;
        if (b >= m) ans += n * (b / m), b %= m;
        LL y = a * n + b;
        if (y < m) break;
        n = y / m, b = y % m;
        swap(m, a);
    }
    return ans;
}

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ll a, b, c;
        scanf("%lld %lld %lld", &a, &b, &c);
        if (c < a + b) { puts("0"); continue; }
        ll X = (c - b) / a;
        LL r = floor_sum(X, b, a, c - a * X);
        printf("%lld\n", (ll)r);
    }
}
