import sys


def main():
    data = sys.stdin.buffer.read().split()
    n, m = int(data[0]), int(data[1])

    # P[i] = prefix sum mod M. subarray (l, r] sum mod M = (P[r] - P[l]) mod M
    # = P[r]-P[l]        if P[l] <= P[r]
    #   P[r]-P[l]+M      if P[l] >  P[r]
    # answer = sum_{0<=l<r<=n} of that = sum_r [ r*P[r] - S(r) + M*G(r) ]
    # where S(r)=sum of prior P, G(r)=count of prior P strictly greater than P[r] (Fenwick).

    tree = [0] * (m + 1)

    def add(i):
        i += 1
        while i <= m:
            tree[i] += 1
            i += i & (-i)

    def le_count(i):  # how many inserted values <= i
        i += 1
        c = 0
        while i > 0:
            c += tree[i]
            i -= i & (-i)
        return c

    ans = 0
    p = 0
    add(0)  # P[0] = 0
    cnt = 1
    s = 0
    for i in range(1, n + 1):
        p = (p + int(data[1 + i])) % m
        ans += i * p - s + m * (cnt - le_count(p))
        add(p)
        cnt += 1
        s += p

    print(ans)


main()
