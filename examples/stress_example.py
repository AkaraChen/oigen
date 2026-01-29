#!/usr/bin/env python3
"""Example: Stress testing two solutions.

To use this example:
1. Compile std.cpp and hack.cpp in the same directory
2. Run this script

std.cpp - correct solution:
    #include <iostream>
    using namespace std;
    int main() {
        int n; cin >> n;
        int sum = 0;
        for (int i = 0; i < n; i++) {
            int x; cin >> x;
            sum += x;
        }
        cout << sum << endl;
        return 0;
    }

hack.cpp - buggy solution (overflow for large values):
    #include <iostream>
    using namespace std;
    int main() {
        int n; cin >> n;
        int sum = 0;  // Bug: should be long long
        for (int i = 0; i < n; i++) {
            int x; cin >> x;
            sum += x;
        }
        cout << sum << endl;
        return 0;
    }
"""

from oigen import workflow, Sequence, Int, Dict, StressTest


def custom_formatter(data):
    """Format data as: n on first line, then n space-separated integers."""
    n = data["n"]
    arr = data["arr"]
    return f"{n}\n{' '.join(str(x) for x in arr)}"


@workflow(formatter=custom_formatter)
def sum_data():
    """Generate array sum test data."""
    n = Int(1, 100)
    return Dict({
        "n": n,
        "arr": Sequence(Int(1, 10**8), length=(10, 50)),  # Large values to trigger overflow
    })


if __name__ == "__main__":
    # Run stress test
    stress = StressTest(
        sum_data,
        std="./std",
        hack="./hack",
        output="./stress_failures",
        timeout=2.0,
    )

    # Run until a hack is found or 1000 iterations
    result = stress.run(max_iterations=1000)

    print(f"\nHacks saved to: {stress.output}")
