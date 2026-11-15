import sys


def solve() -> None:
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    n = int(data[0])
    m = int(data[1])

    bit = [0] * (m + 1)
    # Insert S_0 = 0 (at 1-indexed position 1)
    idx = 1
    while idx <= m:
        bit[idx] += 1
        idx += idx & -idx

    ans = 0
    cur_s = 0
    sum_s = 0

    for j in range(1, n + 1):
        cur_s = (cur_s + int(data[j + 1])) % m

        # Count i < j with S_i <= cur_s
        le = 0
        idx = cur_s + 1
        while idx > 0:
            le += bit[idx]
            idx -= idx & -idx

        gt = j - le
        ans += j * cur_s - sum_s + gt * m

        sum_s += cur_s
        idx = cur_s + 1
        while idx <= m:
            bit[idx] += 1
            idx += idx & -idx

    sys.stdout.write(f"{ans}\n")


if __name__ == "__main__":
    solve()
