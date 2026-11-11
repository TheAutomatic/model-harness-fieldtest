import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])

    # r[k] = prefix sum mod m, k = 0..n
    # answer = sum over 0 <= i < j <= n of (r[j] - r[i]) mod m
    #        = sum_{i<j} (r[j] - r[i])  +  m * #{(i,j): i<j, r[i] > r[j]}
    # first part: sum_j ( j*r[j] - sum_{i<j} r[i] )
    # second part: inversion count via BIT over values 0..m-1

    tree = [0] * (m + 1)

    def update(i):  # value i (0-indexed) += 1
        i += 1
        while i <= m:
            tree[i] += 1
            i += i & (-i)

    def query(i):  # count of inserted values <= i (0-indexed)
        i += 1
        s = 0
        while i > 0:
            s += tree[i]
            i -= i & (-i)
        return s

    r = 0
    update(0)  # insert r[0] = 0
    inv = 0
    total = 0
    pref = 0  # sum of r[0..j-1]
    for j in range(1, n + 1):
        r = (r + int(data[1 + j])) % m
        le = query(r)          # previous values <= r
        inv += j - le          # previous values > r
        total += j * r - pref
        pref += r
        update(r)

    print(total + m * inv)


main()
