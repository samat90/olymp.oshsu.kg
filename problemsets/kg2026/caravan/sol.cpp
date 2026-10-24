// dp[i] = S[i] + V[i] * dist[i] + min over ancestors j of (dp[j] - dist[j] * V[i]).
// Li Chao tree over the compressed speeds with rollback, iterative DFS.
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

struct Line { ll k, b; ll at(ll x) const { return k * x + b; } };
int K;
vector<ll> xs;
vector<Line> tr;
vector<char> has;
vector<pair<int, Line>> hist;  // (node, previous line); a line with k = LLONG_MIN marks "empty"
const Line NONE{LLONG_MIN, 0};

void insertLine(Line ln) {
    int v = 1, l = 0, r = K - 1;
    while (true) {
        if (!has[v]) { hist.push_back({v, NONE}); has[v] = 1; tr[v] = ln; return; }
        int m = (l + r) / 2;
        bool lef = ln.at(xs[l]) < tr[v].at(xs[l]);
        bool mid = ln.at(xs[m]) < tr[v].at(xs[m]);
        if (mid) { hist.push_back({v, tr[v]}); swap(tr[v], ln); }
        if (l == r) return;
        if (lef != mid) { v = 2 * v; r = m; }
        else { v = 2 * v + 1; l = m + 1; }
    }
}
ll query(int pos) {
    int v = 1, l = 0, r = K - 1;
    ll best = LLONG_MAX;
    while (true) {
        if (!has[v]) return best;
        best = min(best, tr[v].at(xs[pos]));
        if (l == r) return best;
        int m = (l + r) / 2;
        if (pos <= m) { v = 2 * v; r = m; }
        else { v = 2 * v + 1; l = m + 1; }
    }
}
void rollback(size_t to) {
    while (hist.size() > to) {
        auto [v, ln] = hist.back(); hist.pop_back();
        if (ln.k == LLONG_MIN) has[v] = 0; else tr[v] = ln;
    }
}

int main() {
    int n = rd();
    vector<int> par(n + 1, 0);
    vector<ll> len(n + 1, 0), S(n + 1, 0), V(n + 1, 0);
    vector<int> cnt(n + 2, 0);
    for (int i = 2; i <= n; i++) { par[i] = rd(); len[i] = rd(); S[i] = rd(); V[i] = rd(); cnt[par[i]]++; }
    vector<int> start(n + 2, 0);
    for (int v = 1; v <= n; v++) start[v + 1] = start[v] + cnt[v];
    vector<int> ch(max(1, n - 1)), fillp(start.begin(), start.end());
    for (int i = 2; i <= n; i++) ch[fillp[par[i]]++] = i;
    xs.assign(V.begin() + 2, V.end());
    if (xs.empty()) xs.push_back(0);
    sort(xs.begin(), xs.end());
    xs.erase(unique(xs.begin(), xs.end()), xs.end());
    K = xs.size();
    tr.assign(4 * K, NONE); has.assign(4 * K, 0);
    vector<ll> dist(n + 1, 0), dp(n + 1, 0);
    vector<size_t> mark(n + 1);
    vector<int> it(n + 1, 0), st;
    st.push_back(1);
    mark[1] = hist.size();
    insertLine({0, 0});
    while (!st.empty()) {
        int v = st.back();
        if (it[v] < start[v + 1] - start[v]) {
            int u = ch[start[v] + it[v]++];
            dist[u] = dist[v] + len[u];
            int pos = lower_bound(xs.begin(), xs.end(), V[u]) - xs.begin();
            dp[u] = query(pos) + S[u] + V[u] * dist[u];
            mark[u] = hist.size();
            insertLine({-dist[u], dp[u]});
            st.push_back(u);
        } else {
            rollback(mark[v]);
            st.pop_back();
        }
    }
    string out;
    out.reserve((size_t)n * 14);
    char buf[24];
    for (int i = 2; i <= n; i++) {
        int k = snprintf(buf, sizeof buf, "%lld%c", dp[i], i == n ? '\n' : ' ');
        out.append(buf, k);
    }
    if (n == 1) out = "\n";
    fwrite(out.data(), 1, out.size(), stdout);
}
