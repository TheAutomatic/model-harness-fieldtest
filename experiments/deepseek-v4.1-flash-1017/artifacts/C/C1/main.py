import sys


def main():
    data = sys.stdin.buffer.read().split()
    if not data:
        return
    n = int(data[0])
    m = int(data[1])

    # Prefix residues: r[0] = 0, r[j] = (A[0] + ... + A[j-1]) % M.
    # Subarray (i, j] sum mod M = (r[j] - r[i]) mod M.
    residues = [0] * (n + 1)
    pref = 0
    for i in range(n):
        pref += int(data[2 + i])
        residues[i + 1] = pref % m

    # Coordinate-compress residues for Fenwick trees (1-based).
    vals = sorted(set(residues))
    rank = {v: i + 1 for i, v in enumerate(vals)}
    k = len(vals)

    bit_cnt = [0] * (k + 1)  # counts of previous residues
    bit_sum = [0] * (k + 1)  # sums of previous residues

    total = 0  # sum of all previous residues
    ans = 0

    for j, r in enumerate(residues):
        pos = rank[r]

        # Query: count and sum of previous residues <= r.
        cnt_le = 0
        sum_le = 0
        p = pos
        while p > 0:
            cnt_le += bit_cnt[p]
            sum_le += bit_sum[p]
            p -= p & -p

        # (r - prev) mod M = r - prev if prev <= r, else r - prev + M.
        # Summing over all previous residues:
        #   j * r - total + M * (number of prev > r)
        ans += r * j - total + m * (j - cnt_le)

        total += r

        # Insert current residue.
        p = pos
        while p <= k:
            bit_cnt[p] += 1
            bit_sum[p] += r
            p += p & -p

    sys.stdout.write(str(ans) + "\n")


if __name__ == "__main__":
    main()
