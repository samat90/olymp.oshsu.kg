// Transfer matrix over column profiles (which cells of the next column are already covered).
// T[a][b] = number of ways to fill a column with incoming profile a producing outgoing profile b.
// Answer = (T^m)[0][0], binary powering of a 2^n x 2^n matrix.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef unsigned long long ull;
const ll MOD = 1000000007;
int n, S;
vector<vector<ll>> T;

void fill_col(int in, int row, int out, int from) {
    if (row == n) { T[from][out]++; return; }
    if (in >> row & 1) { fill_col(in, row + 1, out, from); return; }
    fill_col(in, row + 1, out | 1 << row, from);                       // horizontal, sticks out
    if (row + 1 < n && !(in >> (row + 1) & 1)) fill_col(in, row + 2, out, from);  // vertical
}

vector<vector<ll>> mul(const vector<vector<ll>> &A, const vector<vector<ll>> &B) {
    vector<vector<ll>> C(S, vector<ll>(S, 0));
    for (int i = 0; i < S; i++)
        for (int k = 0; k < S; k++) {
            if (!A[i][k]) continue;
            ull a = A[i][k];
            for (int j = 0; j < S; j++) C[i][j] = (C[i][j] + a * B[k][j]) % MOD;
        }
    return C;
}

int main() {
    ll m;
    if (scanf("%d %lld", &n, &m) != 2) return 0;
    S = 1 << n;
    T.assign(S, vector<ll>(S, 0));
    for (int a = 0; a < S; a++) fill_col(a, 0, 0, a);
    vector<vector<ll>> R(S, vector<ll>(S, 0));
    for (int i = 0; i < S; i++) R[i][i] = 1;
    for (; m; m >>= 1) {
        if (m & 1) R = mul(R, T);
        T = mul(T, T);
    }
    printf("%lld\n", R[0][0]);
}
