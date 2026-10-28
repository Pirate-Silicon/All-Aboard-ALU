"""
test_smoke.py -- given. The step 2 test.

Five quick, hand-picked checks. Passing this means your ALU is alive and
roughly right. It does NOT mean your ALU is correct: it would pass plenty of
broken designs. Step 3 exists for that.

    make smoke

This file deliberately does not import your model. Every expected value here
is written out by hand, so a mistake in your model can't hide a mistake in
your RTL.
"""

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge

ADD, SUB, AND = 0b000, 0b001, 0b010


def read(sig):
    """The value of a signal as an int, or None if any bit is X or Z."""
    try:
        return int(sig.value)
    except ValueError:
        return None


def outputs(dut):
    return (read(dut.y), read(dut.n), read(dut.z), read(dut.c), read(dut.v))


async def reset(dut):
    """Start the clock and hold rst high for two rising edges."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value = 1
    dut.a.value = 0
    dut.b.value = 0
    dut.op.value = 0
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.rst.value = 0


async def apply(dut, op, a, b):
    """Drive one operation, wait out the two-edge latency, return the outputs."""
    await FallingEdge(dut.clk)      # change inputs away from the rising edge
    dut.op.value = op
    dut.a.value = a
    dut.b.value = b
    await RisingEdge(dut.clk)       # edge 1: the input registers capture
    await RisingEdge(dut.clk)       # edge 2: the output registers capture
    await FallingEdge(dut.clk)      # look half a cycle later, once things settle
    return outputs(dut)


class Checker:
    def __init__(self):
        self.errors = 0

    def expect(self, what, got, want):
        names = ("y", "n", "z", "c", "v")
        if got == want:
            print(f"  [ ok ] {what}")
            return
        self.errors += 1
        print(f"  [FAIL] {what}")
        print("         expected " + "  ".join(f"{k}={w}" for k, w in zip(names, want)))
        print("         got      " + "  ".join(
            f"{k}={'X' if g is None else g}" for k, g in zip(names, got)))
        if None in got:
            print("         (X means that output is undriven or never reset)")


@cocotb.test()
async def test_smoke(dut):
    chk = Checker()
    await reset(dut)

    print("\n=== 1. after reset, every output is 0 ===")
    chk.expect("all outputs after reset", outputs(dut), (0, 0, 0, 0, 0))

    print("\n=== 2. ADD 3 + 4 = 7 ===")
    chk.expect("ADD 3 4", await apply(dut, ADD, 3, 4), (7, 0, 0, 0, 0))

    print("\n=== 3. SUB 5 - 3 = 2, and C = 1 because nothing was borrowed ===")
    chk.expect("SUB 5 3", await apply(dut, SUB, 5, 3), (2, 0, 0, 1, 0))

    print("\n=== 4. AND 1100 & 1010 = 1000, which is negative ===")
    chk.expect("AND 12 10", await apply(dut, AND, 12, 10), (8, 1, 0, 0, 0))

    print("\n=== 5. the answer takes exactly two rising edges ===")
    # y is 8 from check 4. Apply ADD 1 + 1 and watch it arrive.
    await FallingEdge(dut.clk)
    dut.op.value, dut.a.value, dut.b.value = ADD, 1, 1
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    chk.expect("after 1 edge, y still holds the old answer", outputs(dut), (8, 1, 0, 0, 0))
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    chk.expect("after 2 edges, y = 1 + 1 = 2", outputs(dut), (2, 0, 0, 0, 0))

    print()
    if chk.errors == 0:
        print(" SMOKE TEST PASSED, 0 errors\n")
    else:
        print(f" SMOKE TEST FAILED, {chk.errors} errors\n")
    assert chk.errors == 0, f"{chk.errors} smoke checks failed, see above"
