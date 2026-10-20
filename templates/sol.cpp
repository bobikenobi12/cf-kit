#include <bits/stdc++.h>
using namespace std;

using ll = long long;
using ii = pair<int, int>;
using vi = vector<int>;
#define all(x) begin(x), end(x)
#define sz(x) int(size(x))

// dbg(x) prints "[line] x = value" to stderr, only in local builds (-DLOCAL).
// It compiles to nothing otherwise, so leaving it in the code is safe.
#ifdef LOCAL
#define dbg(x) cerr << "[" << __LINE__ << "] " << #x << " = " << (x) << '\n'
#else
#define dbg(x) ((void)0)
#endif

void solve() {
    // read the input, compute, print the answer
}

int main() {
    ios::sync_with_stdio(false);  // cin/cout stop syncing with C stdio: much faster
    cin.tie(nullptr);             // cout is not flushed before every cin read

    int t = 1;
    // cin >> t;  // uncomment if the input starts with the number of test cases
    while (t--) solve();
}
