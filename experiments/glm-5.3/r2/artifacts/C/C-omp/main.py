import sys


def count_inversions(arr):
    # returns (number of pairs i<j with arr[i] > arr[j], sorted copy)
    n = len(arr)
    if n <= 1:
        return 0, arr
    mid = n // 2
    inv, left = count_inversions(arr[:mid])
    inv += count_inversions(arr[mid:])[0]
    right = count_inversions(arr[mid:])[1]
    # merge the two halves, counting cross inversions
    merged = []
    i = j = 0
    len_l, len_r = len(left), len(right)
    total = inv
    while i < len_l and j < len_r:
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            total += len_l - i
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return total, merged


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    # a[k] = (A[1] + ... + A[k]) mod M, with a[0] = 0
    a = [0] * (n + 1)
    s = 0
    for i in range(n):
        s += int(data[2 + i])
        a[i + 1] = s % m

    # For subarray (i, j] (0 <= i < j <= n):
    #   sum mod M = a[j] - a[i]        if a[j] >= a[i]
    #             = a[j] - a[i] + M    if a[j] < a[i]
    # Total = sum_{i<j}(a[j]-a[i]) + M * #inversions
    #       = sum_k a[k]*(2k - n)     + M * #inversions
    part1 = 0
    for k in range(n + 1):
        part1 += a[k] * (2 * k - n)

    inv, _ = count_inversions(a)
    print(part1 + m * inv)


main()
