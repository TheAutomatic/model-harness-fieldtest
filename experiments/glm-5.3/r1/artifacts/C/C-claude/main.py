import sys


def count_inversions(a):
    """Count pairs i < j with a[i] > a[j], via bottom-up merge sort. O(n log n)."""
    n = len(a)
    inv = 0
    width = 1
    src = a
    while width < n:
        dst = [0] * n
        two_w = width * 2
        for lo in range(0, n, two_w):
            mid = lo + width
            if mid >= n:
                dst[lo:n] = src[lo:n]
                break
            hi = mid + width
            if hi > n:
                hi = n
            i = lo
            j = mid
            k = lo
            while i < mid and j < hi:
                if src[i] <= src[j]:
                    dst[k] = src[i]
                    i += 1
                else:
                    dst[k] = src[j]
                    j += 1
                    inv += mid - i
                k += 1
            if i < mid:
                dst[k:hi] = src[i:mid]
            elif j < hi:
                dst[k:hi] = src[j:hi]
        src = dst
        width = two_w
    return inv


def solve(n, m, a):
    # prefix sums mod m
    p = [0] * (n + 1)
    s = 0
    for i in range(n):
        s = (s + a[i]) % m
        p[i + 1] = s
    # sum over 0 <= i < j <= n of (p[j] - p[i]) mod m
    # = sum (p[j] - p[i])  +  m * #{pairs with p[i] > p[j]}
    total = 0
    for j in range(n + 1):
        total += p[j] * (2 * j - n)
    total += m * count_inversions(p)
    return total


def main():
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    m = int(data[1])
    a = [int(x) for x in data[2:2 + n]]
    print(solve(n, m, a))


if __name__ == "__main__":
    main()
