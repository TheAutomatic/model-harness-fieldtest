import sys
from itertools import accumulate


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    m = int(data[1])
    # v[i] = prefix sum of first i elements, mod m  (v[0] = 0)
    v = [0]
    v.extend(x % m for x in accumulate(map(int, data[2:2 + n])))

    # Answer = sum over 0 <= l < r <= n of (v[r] - v[l]) mod m
    #        = sum of raw differences + m * (# pairs with v[l] > v[r])
    # sum of raw differences: index i is right endpoint in i pairs,
    # left endpoint in (n - i) pairs  ->  2*sum(i*v_i) - n*sum(v_i)
    idx_sum = 0
    val_sum = 0
    for i, x in enumerate(v):
        idx_sum += i * x
        val_sum += x
    base = 2 * idx_sum - n * val_sum

    # Count pairs l < r with v[l] > v[r] using a Fenwick tree over values 1..m
    tree = [0] * (m + 1)
    inv = 0
    inserted = 0
    for x in v:
        j = x + 1
        leq = 0
        while j:
            leq += tree[j]
            j &= j - 1
        inv += inserted - leq  # earlier elements strictly greater than x
        inserted += 1
        j = x + 1
        while j <= m:
            tree[j] += 1
            j += j & -j

    print(base + m * inv)


main()
