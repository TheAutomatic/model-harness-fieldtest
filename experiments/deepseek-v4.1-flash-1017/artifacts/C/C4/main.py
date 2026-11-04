import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        return

    n, m = data[0], data[1]
    a = data[2:2 + n]

    # prefix[i] = (A[0] + ... + A[i-1]) % m, with prefix[0] = 0
    prefix = [0] * (n + 1)
    cur = 0
    for i, x in enumerate(a, 1):
        cur = (cur + x) % m
        prefix[i] = cur

    # Sum of (prefix[r] - prefix[l]) over all 0 <= l < r <= n.
    total = 0
    for i, value in enumerate(prefix):
        total += i * value - (n - i) * value

    # For each pair with prefix[r] < prefix[l], the modulo result is
    # prefix[r] - prefix[l] + m. Count such inversions using a Fenwick tree.
    tree = [0] * (m + 1)
    inversions = 0

    for i, value in enumerate(prefix):
        # Number of previous prefix values <= value
        idx = value + 1
        count_le = 0
        j = idx
        while j > 0:
            count_le += tree[j]
            j -= j & -j

        inversions += i - count_le

        j = idx
        while j <= m:
            tree[j] += 1
            j += j & -j

    print(total + m * inversions)


if __name__ == "__main__":
    main()
