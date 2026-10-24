// Togyz korgool on 2n holes with huge counts. A move empties a hole and adds whole rounds to every
// hole plus one stone to a cyclic range: Fenwick tree over differences (range add, point query).
// A tuz hole keeps accumulating in the tree; its contents belong to the owner.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;

static char ibuf[1 << 25];
size_t ipos = 0, ilen = 0;
inline int gc() {
    if (ipos == ilen) { ilen = fread(ibuf, 1, sizeof ibuf, stdin); ipos = 0; if (!ilen) return -1; }
    return ibuf[ipos++];
}
inline ll rd() {
    int c = gc();
    while (c < '0' || c > '9') c = gc();
    ll x = 0;
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return x;
}

int N;  // 2n holes, 0-based
vector<ll> bit;
ll allAdd = 0;  // added to every hole
void addAt(int i, ll v) { for (i++; i <= N; i += i & -i) bit[i] += v; }
void rangeAdd(int l, int r, ll v) { addAt(l, v); if (r + 1 < N) addAt(r + 1, -v); }  // l <= r
ll get(int i) { ll s = allAdd; for (i++; i > 0; i -= i & -i) s += bit[i]; return s; }
void setv(int i, ll v) { ll cur = get(i); rangeAdd(i, i, v - cur); }
void cyclicAdd(int l, ll len, ll v) {  // len holes starting at l, len < N
    if (len <= 0) return;
    int r = l + len - 1;
    if (r < N) rangeAdd(l, r, v);
    else { rangeAdd(l, N - 1, v); rangeAdd(0, r - N, v); }
}

int main() {
    int n = rd();
    N = 2 * n;
    bit.assign(N + 1, 0);
    for (int i = 0; i < N; i++) { ll a = rd(); rangeAdd(i, i, a); }
    int m = rd();
    ll kazan[2] = {0, 0};
    int tuz[2] = {-1, -1};  // hole index (0-based) of each player's tuz, it lies on the opponent's side
    for (int t = 0; t < m; t++) {
        int p = t & 1;
        int j = rd() - 1;
        int h = p * n + j;
        if (h == tuz[0] || h == tuz[1]) continue;  // a tuz cannot be played
        ll c = get(h);
        if (c == 0) continue;
        setv(h, 0);
        int last;
        if (c == 1) {
            last = (h + 1) % N;
            cyclicAdd(last, 1, 1);
        } else {
            allAdd += c / N;
            ll rem = c % N;
            cyclicAdd(h, rem, 1);
            last = (int)((h + c - 1) % N);
        }
        int side = last / n;
        if (side != p && last != tuz[0] && last != tuz[1]) {
            ll v = get(last);
            if (v % 2 == 0) { kazan[p] += v; setv(last, 0); }
            else if (v == 3 && tuz[p] < 0 && last % n != n - 1 && !(tuz[1 - p] >= 0 && tuz[1 - p] % n == last % n)) {
                tuz[p] = last;
                kazan[p] += 3;
                setv(last, 0);
            }
        }
    }
    vector<ll> board(N);
    for (int i = 0; i < N; i++) board[i] = get(i);
    for (int p = 0; p < 2; p++) if (tuz[p] >= 0) { kazan[p] += board[tuz[p]]; board[tuz[p]] = 0; }
    string out = to_string(kazan[0]) + " " + to_string(kazan[1]) + "\n";
    out += to_string(tuz[0] < 0 ? 0 : tuz[0] + 1) + " " + to_string(tuz[1] < 0 ? 0 : tuz[1] + 1) + "\n";
    for (int i = 0; i < N; i++) { out += to_string(board[i]); out += i == N - 1 ? '\n' : ' '; }
    fputs(out.c_str(), stdout);
}
