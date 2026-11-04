import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    if not data:
        return

    n, m = data[0], data[1]
    nums = data[2:2 + n]

    # Fenwick tree over prefix remainders 0..m-1.
    tree = [0] * (m + 1)

    def add(pos: int) -> None:
        i = pos + 1
        while i <= m:
            tree[i] += 1
            i += i & -i

    def prefix_count(pos: int) -> int:
        # Number of inserted remainders <= pos.
        i = pos + 1
        result = 0
        while i > 0:
            result += tree[i]
            i -= i & -i
        return result

    add(0)
    pref = 0
    inserted = 1
    prefix_sum = 0
    answer = 0

    for value in nums:
        pref = (pref + value) % m

        le = prefix_count(pref)
        greater = inserted - le

        # For each earlier prefix p:
        #   pref - p        if p <= pref
        #   pref - p + m    if p > pref
        answer += inserted * pref - prefix_sum + m * greater

        add(pref)
        inserted += 1
        prefix_sum += pref

    print(answer)


if __name__ == "__main__":
    main()
