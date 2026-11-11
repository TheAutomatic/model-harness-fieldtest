import sys


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    m = int(data[1])

    # Prefix sums mod M: S[0..n], subarray (i, j] sum mod M = (S[j] - S[i]) mod M
    S = [0] * (n + 1)
    s = 0
    for idx in range(n):
        s = (s + int(data[2 + idx])) % m
        S[idx + 1] = s

    # (S[j] - S[i]) mod M = S[j] - S[i]  (+ M if S[j] < S[i])
    # Sum over all 0 <= i < j <= n:
    #   linear part: sum_k S[k] * (2k - n)
    #   plus M * (number of pairs i < j with S[i] > S[i+1..] inversion count)
    total = 0
    for k in range(n + 1):
        total += S[k] * (2 * k - n)

    # Inversion count via Fenwick tree over values 0..M-1
    tree = [0] * (m + 1)
    inv = 0
    seen = 0
    for sk in S:
        i = sk + 1
        c = 0
        while i > 0:
            c += tree[i]
            i -= i & (-i)
        inv += seen - c
        seen += 1
        i = sk + 1
        while i <= m:
            tree[i] += 1
            i += i & (-i)

    print(total + m * inv)


main()
