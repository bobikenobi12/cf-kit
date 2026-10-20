// Problem: read two integers a and b (|a|, |b| <= 1e9). Print a + b.
#include <bits/stdc++.h>
using namespace std;

using ll = long long;
using ii = pair<int, int>;
using vi = vector<int>;
#define all(x) begin(x), end(x)
#define sz(x) int(size(x))

#ifdef LOCAL
#define dbg(x) cerr << "[" << __LINE__ << "] " << #x << " = " << (x) << '\n'
#else
#define dbg(x) ((void)0)
#endif

void solve() {
    ll a, b;
    cin >> a >> b;
    dbg(a);
    cout << a + b << '\n';
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t = 1;
    while (t--) solve();
}
