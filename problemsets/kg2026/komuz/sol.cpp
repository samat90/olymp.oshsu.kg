// Suffix automaton over a large alphabet. Transitions live in one open-addressing hash table
// keyed by (state, note) plus a per-state edge list for cloning.
// Each step adds len(cur) - len(link(cur)) new distinct substrings.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef unsigned long long ull;

static char ibuf[1 << 25];
size_t ipos = 0, ilen = 0;
inline int gc() {
    if (ipos == ilen) { ilen = fread(ibuf, 1, sizeof ibuf, stdin); ipos = 0; if (!ilen) return -1; }
    return ibuf[ipos++];
}
inline int rd() {
    int c = gc();
    while (c < '0' || c > '9') c = gc();
    int x = 0;
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return x;
}

const int HB = 23, HS = 1 << HB;
vector<ull> hkey;
vector<int> hval;  // edge index
vector<int> eto, enext, ech, head;

inline ull mix(ull x) { x ^= x >> 31; x *= 0x9E3779B97F4A7C15ULL; x ^= x >> 29; return x; }
inline int find_edge(int st, int c) {
    ull k = ((ull)st << 32 | (unsigned)c) + 1;
    size_t h = mix(k) >> (64 - HB);
    while (hkey[h]) { if (hkey[h] == k) return hval[h]; h = (h + 1) & (HS - 1); }
    return -1;
}
inline void add_edge(int st, int c, int to) {
    ull k = ((ull)st << 32 | (unsigned)c) + 1;
    size_t h = mix(k) >> (64 - HB);
    while (hkey[h]) h = (h + 1) & (HS - 1);
    int e = eto.size();
    eto.push_back(to); ech.push_back(c); enext.push_back(head[st]); head[st] = e;
    hkey[h] = k; hval[h] = e;
}

int main() {
    int n = rd();
    int cap = 2 * n + 2;
    hkey.assign(HS, 0); hval.assign(HS, 0);
    eto.reserve(3 * n + 5); ech.reserve(3 * n + 5); enext.reserve(3 * n + 5);
    head.assign(cap, -1);
    vector<int> len(cap), link(cap);
    len[0] = 0; link[0] = -1;
    int sz = 1, last = 0;
    ll total = 0;
    string out;
    out.reserve((size_t)n * 12);
    char buf[24];
    for (int i = 0; i < n; i++) {
        int c = rd();
        int cur = sz++;
        len[cur] = len[last] + 1;
        int p = last, e = -1;
        while (p != -1 && (e = find_edge(p, c)) < 0) { add_edge(p, c, cur); p = link[p]; }
        if (p == -1) link[cur] = 0;
        else {
            int q = eto[e];
            if (len[p] + 1 == len[q]) link[cur] = q;
            else {
                int clone = sz++;
                for (int f = head[q]; f >= 0; f = enext[f]) add_edge(clone, ech[f], eto[f]);
                len[clone] = len[p] + 1;
                link[clone] = link[q];
                while (p != -1) {
                    int f = find_edge(p, c);
                    if (f < 0 || eto[f] != q) break;
                    eto[f] = clone;
                    p = link[p];
                }
                link[q] = link[cur] = clone;
            }
        }
        last = cur;
        total += len[cur] - len[link[cur]];
        int k = snprintf(buf, sizeof buf, "%lld\n", total);
        out.append(buf, k);
    }
    fwrite(out.data(), 1, out.size(), stdout);
}
