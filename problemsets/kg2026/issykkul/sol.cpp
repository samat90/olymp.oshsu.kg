// Online convex hull: upper and lower chains in ordered maps (the lower chain is stored with
// negated y), doubled area kept as a sum of trapezoids under each chain.
#include <bits/stdc++.h>
using namespace std;
typedef long long ll;
typedef __int128 i128;

static char ibuf[1 << 25];
size_t ipos = 0, ilen = 0;
inline int gc() {
    if (ipos == ilen) { ilen = fread(ibuf, 1, sizeof ibuf, stdin); ipos = 0; if (!ilen) return -1; }
    return ibuf[ipos++];
}
inline int rdc() { int c = gc(); while (c != '+' && c != '?' && c != 'A') c = gc(); return c; }
inline ll rd() {
    int c = gc();
    while (c != '-' && (c < '0' || c > '9')) c = gc();
    bool neg = false;
    if (c == '-') { neg = true; c = gc(); }
    ll x = 0;
    while (c >= '0' && c <= '9') { x = x * 10 + (c - '0'); c = gc(); }
    return neg ? -x : x;
}

// cross of (b - a) x (c - a)
inline i128 cross(ll ax, ll ay, ll bx, ll by, ll cx, ll cy) {
    return (i128)(bx - ax) * (cy - ay) - (i128)(by - ay) * (cx - ax);
}

struct Chain {  // upper chain: for every x the top point, turns strictly clockwise
    map<ll, ll> h;
    i128 area = 0;  // sum over edges of (x2 - x1) * (y1 + y2)
    static i128 trap(map<ll, ll>::iterator a, map<ll, ll>::iterator b) {
        return (i128)(b->first - a->first) * (a->second + b->second);
    }
    void erase(map<ll, ll>::iterator it) {
        auto nx = next(it);
        bool hasP = it != h.begin(), hasN = nx != h.end();
        if (hasP) area -= trap(prev(it), it);
        if (hasN) area -= trap(it, nx);
        if (hasP && hasN) area += trap(prev(it), nx);
        h.erase(it);
    }
    // is (x, y) on or below the chain? requires x within [min x, max x]
    bool below(ll x, ll y) const {
        auto it = h.lower_bound(x);
        if (it == h.end()) return false;
        if (it->first == x) return y <= it->second;
        if (it == h.begin()) return false;
        auto pv = prev(it);
        return cross(pv->first, pv->second, it->first, it->second, x, y) <= 0;
    }
    void insert(ll x, ll y) {
        if (!h.empty() && h.begin()->first <= x && x <= h.rbegin()->first && below(x, y)) return;
        auto ex = h.find(x);
        if (ex != h.end()) erase(ex);
        auto it = h.emplace(x, y).first;
        auto nx = next(it);
        bool hasP = it != h.begin(), hasN = nx != h.end();
        if (hasP && hasN) area -= trap(prev(it), nx);
        if (hasP) area += trap(prev(it), it);
        if (hasN) area += trap(it, nx);
        // remove points to the right that are no longer on the chain
        while (true) {
            auto a = next(it);
            if (a == h.end()) break;
            auto b = next(a);
            if (b == h.end()) break;
            if (cross(x, y, a->first, a->second, b->first, b->second) >= 0) erase(a);
            else break;
        }
        while (it != h.begin()) {
            auto a = prev(it);
            if (a == h.begin()) break;
            auto b = prev(a);
            if (cross(b->first, b->second, a->first, a->second, x, y) >= 0) erase(a);
            else break;
        }
    }
};

void print128(i128 v, string &out) {
    if (v < 0) { out += '-'; v = -v; }
    char buf[48]; int k = 0;
    if (v == 0) buf[k++] = '0';
    while (v > 0) { buf[k++] = '0' + (int)(v % 10); v /= 10; }
    while (k) out += buf[--k];
    out += '\n';
}

int main() {
    int q = rd();
    Chain up, low;  // low stores (x, -y)
    string out;
    while (q--) {
        int c = rdc();
        if (c == 'A') {
            print128(up.h.empty() ? 0 : up.area + low.area, out);
            continue;
        }
        ll x = rd(), y = rd();
        if (c == '+') { up.insert(x, y); low.insert(x, -y); }
        else {
            bool in = !up.h.empty() && up.h.begin()->first <= x && x <= up.h.rbegin()->first &&
                      up.below(x, y) && low.below(x, -y);
            out += in ? "YES\n" : "NO\n";
        }
    }
    fputs(out.c_str(), stdout);
}
