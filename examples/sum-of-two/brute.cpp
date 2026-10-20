// Brute force for stress testing: add one at a time. Slow, but obviously correct for small inputs.
#include <bits/stdc++.h>
using namespace std;

int main() {
    long long a, b;
    cin >> a >> b;
    long long sum = a;
    long long step = b >= 0 ? 1 : -1;
    for (long long i = 0; i < llabs(b); ++i) sum += step;
    cout << sum << '\n';
}
