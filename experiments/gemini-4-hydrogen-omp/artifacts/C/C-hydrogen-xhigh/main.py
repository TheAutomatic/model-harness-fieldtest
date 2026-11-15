import sys


def solve() -> None:
    it = map(int, sys.stdin.buffer.read().split())
    n = next(it, None)
    if n is None:
        return
    m = next(it)

    tree = [0] * (m + 1)
    p = 0
    ans = 0
    inv = 0

    for k, x in zip(range(1, n + 1), it):
        p = (p + x) % m
        ans += (2 * k - n) * p

        idx = m - p
        j = idx - 1
        s = 0
        while j:
            s += tree[j]
            j -= j & -j
        inv += s

        while idx <= m:
            tree[idx] += 1
            idx += idx & -idx

    sys.stdout.write(f"{ans + inv * m}\n")


if __name__ == "__main__":
    solve()
