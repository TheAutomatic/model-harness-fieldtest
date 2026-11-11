import sys


def count_inversions(arr):
    """Bottom-up merge sort; returns number of pairs i<j with arr[i] > arr[j]."""
    n = len(arr)
    inv = 0
    src = arr
    width = 1
    while width < n:
        dst = []
        for lo in range(0, n, 2 * width):
            mid = min(lo + width, n)
            hi = min(lo + 2 * width, n)
            i, j = lo, mid
            while i < mid and j < hi:
                if src[i] <= src[j]:
                    dst.append(src[i])
                    i += 1
                else:
                    dst.append(src[j])
                    j += 1
                    inv += mid - i
            dst.extend(src[i:mid])
            dst.extend(src[j:hi])
        src = dst
        width *= 2
    return inv


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    a = list(map(int, data[2:2 + n]))

    # 前缀和的余数 r[0..n]
    r = [0] * (n + 1)
    s = 0
    for i, x in enumerate(a):
        s += x
        r[i + 1] = s % m

    # 子数组 [i, j) 的和 mod M = (r[j] - r[i]) mod M
    #   = r[j] - r[i] + M * (1 若 r[i] > r[j] 否则 0)
    # sum_{i<j} (r[j] - r[i]) = sum_k r[k] * (2k - n)
    base = 0
    for k in range(n + 1):
        base += r[k] * (2 * k - n)

    print(base + m * count_inversions(r))


main()
