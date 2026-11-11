import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])

    # Fenwick tree over remainder values 0..m-1 (index = value + 1)
    tree = [0] * (m + 1)

    def update(i):
        while i <= m:
            tree[i] += 1
            i += i & (-i)

    def query(i):
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & (-i)
        return s

    total = 0
    run = 0        # sum of p[a] for already-inserted prefixes a < k
    p = 0          # current prefix sum mod m
    update(1)      # insert p[0] = 0

    for k in range(1, n + 1):
        ai = int(data[1 + k])
        p = (p + ai) % m
        # subarray sums ending at k: (p[k] - p[a]) % m for a in 0..k-1
        # = p - p[a] if p[a] <= p, else p - p[a] + m
        greater = k - query(p + 1)   # count of a<k with p[a] > p
        total += p * k - run + m * greater
        run += p
        update(p + 1)

    print(total)


main()
