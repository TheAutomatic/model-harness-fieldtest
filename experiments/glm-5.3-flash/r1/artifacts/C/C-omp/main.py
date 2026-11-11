import sys
from itertools import accumulate
from operator import mul


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    m = int(data[1])
    # prefix sums mod M: r[k] = A[0..k-1] mod M, r has n+1 entries
    r = [0]
    r.extend(s % m for s in accumulate(map(int, data[2:2 + n])))

    # sum over i<j of (r[j] - r[i]) = 2*sum(k*r[k]) - n*sum(r)
    base = 2 * sum(map(mul, range(n + 1), r)) - n * sum(r)

    # pairs i<j with r[i] > r[j] contribute +M each (Fenwick inversion count)
    tree = [0] * (m + 1)
    inv = 0
    for k in range(n + 1):
        x = r[k] + 1
        c = 0
        while x:
            c += tree[x]
            x &= x - 1
        inv += k - c
        x = r[k] + 1
        while x <= m:
            tree[x] += 1
            x += x & -x

    print(base + m * inv)


if __name__ == "__main__":
    main()
