import sys
from bisect import bisect_right
from itertools import accumulate, repeat


def count_inversions(arr):
    """Count pairs i < j with arr[i] > arr[j] (bottom-up merge sort)."""
    inv = 0
    runs = [[x] for x in arr]
    while len(runs) > 1:
        merged = []
        push = merged.append
        i = 0
        L = len(runs)
        while i < L:
            if i + 1 == L:
                push(runs[i])
                break
            left = runs[i]
            right = runs[i + 1]
            nl = len(left)
            # cross inversions: for each r in right, # of elements in left > r
            inv += nl * len(right) - sum(map(bisect_right, repeat(left), right))
            push(sorted(left + right))  # timsort merges two sorted runs in O(n)
            i += 2
        runs = merged
    return inv


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    p = list(accumulate(map(int, data[2:2 + n])))
    q = [0] + [x % m for x in p]

    # sum over all pairs i<j of (q[j] - q[i]), without the +m correction
    easy = 0
    cum = 0
    for j in range(1, n + 1):
        qj = q[j]
        easy += j * qj - cum
        cum += qj

    inv = count_inversions(q)
    print(easy + m * inv)


main()
