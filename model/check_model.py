"""
given. Do not edit

Runs your model against 40 hand-worked examples from the spec.
    python3 check_model.py            check your model
    python3 check_model.py --table    also print the full truth table

Every expected value below was worked out by hand from step1-spec/SPEC.md,
not by running a model. That matters: a checker that computes its answers
with the same code it is checking would agree with itself and prove nothing.
"""

import sys

from alu_model import alu, OP_NAMES

#  op      a    b     y   n  z  c  v    why this case is here
VECTORS = [
    ("ADD",  3,   4,    7,  0, 0, 0, 0,  "plain addition"),
    ("ADD",  7,   1,    8,  1, 0, 0, 1,  "7 + 1 overflows: two positives make a negative"),
    ("ADD", 15,   1,    0,  0, 1, 1, 0,  "-1 + 1 = 0: carry out, but no signed overflow"),
    ("ADD",  8,   8,    0,  0, 1, 1, 1,  "-8 + -8: carry AND overflow"),
    ("ADD", 15,  15,   14,  1, 0, 1, 0,  "-1 + -1 = -2: carry, no overflow"),
    ("ADD",  0,   0,    0,  0, 1, 0, 0,  "zero"),
    ("ADD",  9,   3,   12,  1, 0, 0, 0,  "-7 + 3 = -4: negative, no overflow"),
    ("ADD",  5,   6,   11,  1, 0, 0, 1,  "5 + 6 overflows"),
    ("SUB",  5,   3,    2,  0, 0, 1, 0,  "5 - 3: C = 1 because there was no borrow"),
    ("SUB",  3,   5,   14,  1, 0, 0, 0,  "3 - 5 = -2: C = 0 because we borrowed"),
    ("SUB",  0,   0,    0,  0, 1, 1, 0,  "0 - 0: zero, and C = 1 (no borrow)"),
    ("SUB",  0,   1,   15,  1, 0, 0, 0,  "0 - 1 = -1"),
    ("SUB",  8,   1,    7,  0, 0, 1, 1,  "-8 - 1 overflows to +7"),
    ("SUB",  7,  15,    8,  1, 0, 0, 1,  "7 - (-1) overflows to -8"),
    ("SUB",  4,   4,    0,  0, 1, 1, 0,  "equal inputs give zero"),
    ("SUB", 15,   1,   14,  1, 0, 1, 0,  "-1 - 1 = -2"),
    ("SUB",  1,  15,    2,  0, 0, 0, 0,  "1 - (-1) = 2, but unsigned 1 < 15 so C = 0"),
    ("SUB",  9,   2,    7,  0, 0, 1, 1,  "-7 - 2 overflows"),
    ("AND", 12,  10,    8,  1, 0, 0, 0,  "1100 & 1010"),
    ("AND",  5,  10,    0,  0, 1, 0, 0,  "no bits in common"),
    ("AND", 15,  15,   15,  1, 0, 0, 0,  "logic ops never set C or V"),
    ("OR",  12,  10,   14,  1, 0, 0, 0,  "1100 | 1010"),
    ("OR",   0,   0,    0,  0, 1, 0, 0,  "zero"),
    ("OR",   5,   2,    7,  0, 0, 0, 0,  "0101 | 0010"),
    ("XOR", 12,  10,    6,  0, 0, 0, 0,  "1100 ^ 1010"),
    ("XOR",  9,   9,    0,  0, 1, 0, 0,  "anything XOR itself is zero"),
    ("XOR",  5,  10,   15,  1, 0, 0, 0,  "0101 ^ 1010"),
    ("NOT",  0,   0,   15,  1, 0, 0, 0,  "~0000"),
    ("NOT", 15,   0,    0,  0, 1, 0, 0,  "~1111"),
    ("NOT",  5,   7,   10,  1, 0, 0, 0,  "NOT ignores b"),
    ("NOT", 10,   3,    5,  0, 0, 0, 0,  "NOT ignores b"),
    ("SHL",  3,   0,    6,  0, 0, 0, 0,  "0011 -> 0110"),
    ("SHL",  9,   0,    2,  0, 0, 0, 0,  "1001 -> 0010: top bit falls off, C stays 0"),
    ("SHL",  4,   0,    8,  1, 0, 0, 0,  "0100 -> 1000"),
    ("SHL",  8,   0,    0,  0, 1, 0, 0,  "1000 -> 0000"),
    ("SHR",  6,   0,    3,  0, 0, 0, 0,  "0110 -> 0011"),
    ("SHR",  8,   0,    4,  0, 0, 0, 0,  "logical shift: a 0 comes in, so -8 becomes +4"),
    ("SHR",  1,   0,    0,  0, 1, 0, 0,  "0001 -> 0000"),
    ("SHR", 15,   0,    7,  0, 0, 0, 0,  "1111 -> 0111"),
    ("SHR", 15,   9,    7,  0, 0, 0, 0,  "shifts ignore b"),
]


def check():
    failures = 0
    for name, a, b, y, n, z, c, v, why in VECTORS:
        op = OP_NAMES.index(name)
        got = alu(op, a, b)
        want = (y, n, z, c, v)
        have = (got.y, got.n, got.z, got.c, got.v)
        if have == want:
            print(f"  [ ok ] {name} {a:2} {b:2}")
        else:
            failures += 1
            print(f"  [FAIL] {name} {a:2} {b:2}   {why}")
            print(f"         expected y={y:2} n={n} z={z} c={c} v={v}")
            print(f"         got      y={got.y:2} n={got.n} z={got.z} c={got.c} v={got.v}")
    print()
    if failures == 0:
        print(f" MODEL PASSED, all {len(VECTORS)} checks")
    else:
        print(f" MODEL FAILED, {failures} of {len(VECTORS)} checks")
    return failures


def table():
    print("op,a,b,y,n,z,c,v")
    rows = 0
    for op in range(8):
        for a in range(16):
            for b in range(16):
                r = alu(op, a, b)
                print(f"{OP_NAMES[op]},{a},{b},{r.y},{r.n},{r.z},{r.c},{r.v}")
                rows += 1
    print(f"# {rows} rows. That is every input this ALU can ever see.", file=sys.stderr)


if __name__ == "__main__":
    if "--table" in sys.argv:
        table()
    else:
        sys.exit(1 if check() else 0)
