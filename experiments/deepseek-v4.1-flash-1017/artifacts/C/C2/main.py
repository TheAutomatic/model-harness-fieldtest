import sys


def solve() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        return

    n, m = data[0], data[1]
    a = data[2:2 + n]

    # Fenwick tree: counts of prefix residues seen so far.
    bit = [0] * (m + 1)

    def add(idx: int) -> None:
        # idx is 1-based
        while idx <= m:
            bit[idx] += 1
            idx += idx & -idx

    def query(idx: int) -> int:
        # count of residues with 1-based index <= idx
        res = 0
        while idx > 0:
            res += bit[idx]
            idx -= idx & -idx
        return res

    ans = 0
    prefix = 0
    seen = 0
    sum_prev = 0

    # Include prefix sum 0 before the array.
    for j in range(n + 1):
        if j > 0:
            prefix = (prefix + a[j - 1]) % m

        # For previous prefix x and current prefix y:
        # (y - x) mod m = y - x + m if x > y
        less_or_equal = query(prefix + 1)
        greater = seen - less_or_equal

        ans += j * prefix - sum_prev
        ans += m * greater

        add(prefix + 1)
        seen += 1
        sum_prev += prefix

    print(ans)


if __name__ == "__main__":
    solve()
