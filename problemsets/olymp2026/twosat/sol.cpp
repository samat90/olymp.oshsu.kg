// Classic incremental 2-SAT: fix guests in order, try side 0, propagate the implications; if that
// leads to a contradiction, undo and take side 1. When the formula is satisfiable, a propagation without
// a conflict never makes the rest unsatisfiable, so the first conflict-free choice is always right.
#include <bits/stdc++.h>
using namespace std;
int n, m;
vector<vector<int>> g;  // literal 2*v + val, edge "if A then B"
vector<int> val, trail;

bool setLit(int lit) {  // assign literal true and propagate; false on conflict
    vector<int> st{lit};
    while (!st.empty()) {
        int l = st.back(); st.pop_back();
        int v = l >> 1, b = l & 1;
        if (val[v] == b) continue;
        if (val[v] != -1) return false;
        val[v] = b, trail.push_back(v);
        for (int t : g[l]) st.push_back(t);
    }
    return true;
}

int main() {
    if (scanf("%d %d", &n, &m) != 2) return 0;
    g.assign(2 * n, {});
    for (int k = 0; k < m; k++) {
        int i, x, j, y;
        scanf("%d %d %d %d", &i, &x, &j, &y);
        i--, j--;
        int A = 2 * i + x, B = 2 * j + y;
        g[A ^ 1].push_back(B);
        g[B ^ 1].push_back(A);
    }
    val.assign(n, -1);
    for (int v = 0; v < n; v++) {
        if (val[v] != -1) continue;
        size_t mark = trail.size();
        if (setLit(2 * v)) continue;
        while (trail.size() > mark) val[trail.back()] = -1, trail.pop_back();
        if (!setLit(2 * v + 1)) { puts("NO"); return 0; }
    }
    // final check (the greedy is only valid for satisfiable formulas)
    for (int l = 0; l < 2 * n; l++)
        if (val[l >> 1] == (l & 1))
            for (int t : g[l]) if (val[t >> 1] != (t & 1)) { puts("NO"); return 0; }
    for (int v = 0; v < n; v++) putchar('0' + val[v]);
    puts("");
}
