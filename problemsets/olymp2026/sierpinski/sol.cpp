// F(k, r, c) = filled cells in rows [0, r) and columns [0, c) of the order-k carpet.
// A 3 x 3 split leaves full blocks (8^(k-1) cells), strips that are full in one direction
// (Row, linear recursion; the carpet is symmetric, so rows and columns are alike) and one corner block.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
ll p3[25], p8[25];

ll Row(int k, ll c) {  // all rows, columns [0, c): linear recursion, used for one value of c
    if (c <= 0) return 0;
    if (c >= p3[k]) return p8[k];
    ll s = p3[k - 1], bc = c / s, rc = c % s, res = 0;
    for (int j = 0; j < bc; j++) res += (j == 1 ? 2 : 3) * p8[k - 1];
    if (rc) res += (bc == 1 ? 2 : 3) * Row(k - 1, rc);
    return res;
}

// Every strip met by F(k, r, c) at level j is Row(j, c mod 3^j) or Row(j, r mod 3^j):
// both tables are filled bottom-up once per call, so F costs O(k).
ll RR[25], RC[25];
void fill(ll *R, ll v, int k) {
    for (int j = 0; j <= k; j++) {
        ll c = v % p3[j];
        if (j == 0) { R[j] = 0; continue; }
        ll s = p3[j - 1], bc = c / s, rc = c % s, res = 0;
        for (int t = 0; t < bc; t++) res += (t == 1 ? 2 : 3) * p8[j - 1];
        if (rc) res += (bc == 1 ? 2 : 3) * R[j - 1];
        R[j] = res;  // = Row(j, v mod 3^j)
    }
}

ll F(int k, ll r, ll c) {
    if (r <= 0 || c <= 0) return 0;
    if (r >= p3[k]) return Row(k, c);
    if (c >= p3[k]) return Row(k, r);
    fill(RR, r, k), fill(RC, c, k);
    ll res = 0;
    for (int j = k; j >= 1; j--) {  // r, c < 3^j here
        ll s = p3[j - 1], br = r / s, rr = r % s, bc = c / s, rc = c % s;
        ll corner = 0;
        for (int i = 0; i < 3; i++)
            for (int t = 0; t < 3; t++) {
                if (i == 1 && t == 1) continue;
                ll h = i < br ? s : (i == br ? rr : 0);
                ll w = t < bc ? s : (t == bc ? rc : 0);
                if (!h || !w) continue;
                if (h == s && w == s) res += p8[j - 1];
                else if (h == s) res += RC[j - 1];
                else if (w == s) res += RR[j - 1];
                else corner = 1;
            }
        if (!corner) return res;
        r = rr, c = rc;
    }
    return res + (r > 0 && c > 0 ? 1 : 0);
}

int main() {
    p3[0] = p8[0] = 1;
    for (int i = 1; i < 25; i++) p3[i] = p3[i - 1] * 3, p8[i] = p8[i - 1] * 8;
    int k, q;
    if (scanf("%d %d", &k, &q) != 2) return 0;
    while (q--) {
        ll x1, y1, x2, y2;
        scanf("%lld %lld %lld %lld", &x1, &y1, &x2, &y2);
        printf("%lld\n", F(k, x2 + 1, y2 + 1) - F(k, x1, y2 + 1) - F(k, x2 + 1, y1) + F(k, x1, y1));
    }
}
