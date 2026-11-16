import sys


def read_input() -> tuple[int, int, list[int]]:
    """Read N, M, and the array A of length N from standard input."""
    stream = getattr(sys.stdin, "buffer", sys.stdin)
    tokens = []
    while len(tokens) < 2:
        line = stream.readline()
        if not line:
            raise ValueError("Unexpected end of input while reading N and M.")
        tokens.extend(line.split())

    n = int(tokens[0])
    m = int(tokens[1])
    a = list(map(int, tokens[2 : 2 + n]))

    while len(a) < n:
        line = stream.readline()
        if not line:
            raise ValueError("Unexpected end of input while reading array A.")
        parts = line.split()
        need = n - len(a)
        if len(parts) > need:
            parts = parts[:need]
        a.extend(map(int, parts))

    return n, m, a


def solve(m: int, a: list[int]) -> int:
    """Compute the sum of ((sum of subarray) % M) over all contiguous subarrays."""
    # Prefix sums mod M satisfy: (P[j] - P[i]) % M = P[j] - P[i] + M * [P[i] > P[j]].
    # A 4-level base-32 tree (32^4 > 10^6 >= M) lets each prefix frequency query run
    # via at most four short C-level sum() calls instead of a Python bit-loop.
    l0 = [0] * m
    l1 = [0] * ((m >> 5) + 1)
    l2 = [0] * ((m >> 10) + 1)
    l3 = [0] * ((m >> 15) + 1)

    # Insert P[0] = 0 before iterating over j = 1..N.
    l0[0] = l1[0] = l2[0] = l3[0] = 1

    cur = 0
    pref_sum = 0
    diff_sum = 0
    inversions = 0

    for j, x in enumerate(a, 1):
        cur = (cur + x) % m
        p = cur + 1
        b1 = p >> 5
        b2 = p >> 10
        b3 = p >> 15

        le = sum(l0[b1 << 5 : p])
        if b1 > (b2 << 5):
            le += sum(l1[b2 << 5 : b1])
        if b2 > (b3 << 5):
            le += sum(l2[b3 << 5 : b2])
        if b3:
            le += sum(l3[:b3])

        inversions += j - le
        diff_sum += j * cur - pref_sum
        pref_sum += cur

        l0[cur] += 1
        l1[cur >> 5] += 1
        l2[cur >> 10] += 1
        l3[cur >> 15] += 1

    return diff_sum + m * inversions


def main() -> None:
    """Entry point: read input from stdin and print the answer to stdout."""
    _, m, a = read_input()
    print(solve(m, a))


if __name__ == "__main__":
    main()
