// Josephus with large n: while n >= k, one full pass removes floor(n/k) people, which gives
// J(n) from J(n - n/k) by a shift (O(k log n) steps); for n < k the usual recurrence J(n) = (J(n-1) + k) mod n.
// The recursion is unrolled with an explicit stack.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

ll josephus(ll n, ll k) {  // 0-based survivor
    if (k == 1) return n - 1;
    vector<ll> st;
    ll m = n;
    while (m > 1 && m >= k) st.push_back(m), m -= m / k;
    // now m < k (or m == 1): plain recurrence from 1 to m
    ll r = 0;
    for (ll i = 2; i <= m; i++) r = (r + k) % i;
    while (!st.empty()) {
        ll N = st.back(); st.pop_back();
        // r is the survivor among N - N/k people, numbered from the person after the last removed one
        r -= N % k;
        if (r < 0) r += N;
        else r += r / (k - 1);
    }
    return r;
}

int main() {
    int T;
    if (scanf("%d", &T) != 1) return 0;
    while (T--) {
        ll n, k;
        scanf("%lld %lld", &n, &k);
        printf("%lld\n", josephus(n, k) + 1);
    }
}
