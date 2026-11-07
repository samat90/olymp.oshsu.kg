// 2D polynomial hashing modulo 2^61 - 1 (rows with base X, columns with base Y). For each rotation of
// the pattern (as a grid of its own size) the matching top-left corners are marked; a corner of a given
// size is counted once even if several rotations match there.
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long ull;
typedef __uint128_t u128;
const ull MODH = (1ULL << 61) - 1;
ull mulm(ull a, ull b) { u128 c = (u128)a * b; ull r = (ull)(c >> 61) + (ull)(c & MODH); return r >= MODH ? r - MODH : r; }
ull addm(ull a, ull b) { a += b; return a >= MODH ? a - MODH : a; }
ull subm(ull a, ull b) { return a >= b ? a - b : a + MODH - b; }

int N, M, A, B;
vector<string> g, pat;
ull X = 911382323ULL * 1000003ULL % MODH, Y = 972663749ULL * 999983ULL % MODH;
vector<ull> px, py;
vector<vector<ull>> H;  // prefix hashes of the grid

ull hashGrid(const vector<string> &p) {
    ull h = 0;
    int r = p.size(), c = p[0].size();
    for (int i = 0; i < r; i++) {
        ull row = 0;
        for (int j = 0; j < c; j++) row = addm(mulm(row, Y), (ull)p[i][j]);
        h = addm(mulm(h, X), row);
    }
    return h;
}
ull rect(int i, int j, int r, int c) {  // hash of the r x c block with top-left (i, j)
    ull v = H[i + r][j + c];
    v = subm(v, mulm(H[i][j + c], px[r]));
    v = subm(v, mulm(H[i + r][j], py[c]));
    v = addm(v, mulm(mulm(H[i][j], px[r]), py[c]));
    return v;
}
vector<string> rot(const vector<string> &p) {  // 90 degrees clockwise
    int r = p.size(), c = p[0].size();
    vector<string> q(c, string(r, ' '));
    for (int i = 0; i < r; i++) for (int j = 0; j < c; j++) q[j][r - 1 - i] = p[i][j];
    return q;
}

int main() {
    if (scanf("%d %d %d %d", &N, &M, &A, &B) != 4) return 0;
    static char buf[1005];
    g.resize(N), pat.resize(A);
    for (int i = 0; i < N; i++) scanf("%s", buf), g[i] = buf;
    for (int i = 0; i < A; i++) scanf("%s", buf), pat[i] = buf;
    int L = max({N, M, A, B}) + 1;
    px.assign(L + 1, 1), py.assign(L + 1, 1);
    for (int i = 1; i <= L; i++) px[i] = mulm(px[i - 1], X), py[i] = mulm(py[i - 1], Y);
    H.assign(N + 1, vector<ull>(M + 1, 0));
    for (int i = 0; i < N; i++)
        for (int j = 0; j < M; j++) {
            ull v = addm(mulm(H[i][j + 1], X), mulm(H[i + 1][j], Y));
            v = subm(v, mulm(mulm(H[i][j], X), Y));
            H[i + 1][j + 1] = addm(v, (ull)g[i][j]);
        }
    long long total = 0;
    vector<vector<string>> rots{pat};
    for (int t = 0; t < 3; t++) rots.push_back(rot(rots.back()));
    for (int shape = 0; shape < 2; shape++) {
        int r = shape == 0 ? A : B, c = shape == 0 ? B : A;
        if (shape == 1 && A == B) break;
        if (r > N || c > M) continue;
        vector<ull> hs;
        for (auto &p : rots) if ((int)p.size() == r) hs.push_back(hashGrid(p));
        sort(hs.begin(), hs.end());
        hs.erase(unique(hs.begin(), hs.end()), hs.end());
        for (int i = 0; i + r <= N; i++)
            for (int j = 0; j + c <= M; j++) {
                ull h = rect(i, j, r, c);
                for (ull x : hs) if (x == h) { total++; break; }
            }
    }
    printf("%lld\n", total);
}
