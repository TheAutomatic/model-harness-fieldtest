import sys
from itertools import accumulate


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    m = int(data[1])

    # c[i] = (A[0] + ... + A[i-1]) % m, with c[0] = 0.
    # Subarray A[l..r-1] has sum P[r] - P[l], whose remainder mod m is
    # (c[r] - c[l]) mod m  (value in [0, m)).
    c = [0] + [p % m for p in accumulate(map(int, data[2:2 + n]))]

    # Answer = sum over pairs 0 <= l < r <= n of ((c[r] - c[l]) mod m)
    #         = sum(c[i] * (2i - n) for i in 0..n)      ... index-order part
    #         + m * (#pairs l < r with c[l] > c[r])     ... wrap-around part
    part1 = sum(v * (i + i - n) for i, v in enumerate(c))

    # Count inversions of c[0..n] with a Fenwick tree over values [0, m-1].
    tree = [0] * (m + 1)
    inv = 0
    seen = 0
    for x in c:
        # how many already-seen values are <= x
        i = x + 1
        le = 0
        while i > 0:
            le += tree[i]
            i -= i & (-i)
        inv += seen - le
        seen += 1
        i = x + 1
        while i <= m:
            tree[i] += 1
            i += i & (-i)

    print(part1 + m * inv)


main()
