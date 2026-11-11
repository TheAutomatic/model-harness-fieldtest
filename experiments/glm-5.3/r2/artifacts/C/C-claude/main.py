import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])
    a = list(map(int, data[2:2 + n]))

    # 前缀和模 M：p[k] = (A[0] + ... + A[k-1]) mod M，p[0] = 0
    p = [0] * (n + 1)
    s = 0
    for i, x in enumerate(a):
        s = (s + x) % m
        p[i + 1] = s

    # 第一部分：sum_{i<j} (p[j] - p[i])
    # p[k] 作为被减数出现 k 次，作为减数出现 (n - k) 次
    part1 = 0
    for k in range(n + 1):
        part1 += p[k] * (2 * k - n)

    # 第二部分：统计 i < j 且 p[i] > p[j] 的对数（逆序对），树状数组
    tree = [0] * (m + 1)
    inv = 0
    seen = 0
    for v in p:
        # 查询已插入的值中 <= v 的个数
        i = v + 1
        c = 0
        while i > 0:
            c += tree[i]
            i -= i & (-i)
        inv += seen - c  # 严格大于 v 的个数
        # 插入 v
        i = v + 1
        while i <= m:
            tree[i] += 1
            i += i & (-i)
        seen += 1

    print(part1 + m * inv)


main()
