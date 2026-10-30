"""
test_alu.py - YOU FILL THIS IN, in step 3.

A self-checking testbench built from the same six pieces every industrial
verification environment uses. Each section below is one piece, labelled
with what it's called in UVM, the SystemVerilog framework the industry uses.

    TRANSACTION   one operation to try                 uvm_sequence_item
    GENERATOR     makes transactions                   uvm_sequence
    DRIVER        turns a transaction into pin values  uvm_driver
    MONITOR       watches the outputs, drives nothing  uvm_monitor
    MODEL         says what the answer should be       (your step 1 model)
    SCOREBOARD    compares and counts                  uvm_scoreboard
    COVERAGE      says whether you tested enough       covergroup

The pieces talk to each other only through queues, never by reaching into
each other's variables. That separation is the point: you can replace the
generator without touching the driver, and the monitor can watch outputs it
has no control over.

Run it:
    make test               on your ALU
    make test DUT=buggy     on the vendor ALU

Every TODO(step3) is yours. The MONITOR is written in full, as the worked
example, because its timing is fiddly and not the lesson.
"""

import random
from dataclasses import dataclass

import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import FallingEdge

# Your model from step 1. Not a copy: the same file, imported.
from alu_model import alu, AluResult, OP_NAMES, ADD, SUB, AND, OR, XOR, NOT, SHL, SHR

LATENCY = 2          # rising edges from inputs to outputs, from the spec
N_RANDOM = 500       # how many random transactions test_random sends
MAX_PRINTED = 10     # stop printing mismatches after this many


#=========================================================================
# 0. TRANSACTION                                      uvm_sequence_item
#=========================================================================
# One operation: WHAT to do, not HOW to put it on wires. Given.
@dataclass(frozen=True)
class AluTxn:
    op: int
    a: int
    b: int

    def __str__(self):
        return f"{OP_NAMES[self.op]:3} a={self.a:2} b={self.b:2}"


#=========================================================================
# 1. GENERATOR                                             uvm_sequence
#=========================================================================
# Makes lists of transactions. Knows nothing about pins or clocks.

# TODO(step3): your corner cases, from your test plan. Two are given as the
# pattern. Every one should have a comment saying what it's there to catch.
CORNER_CASES = [
    AluTxn(ADD, 7, 1),       # signed overflow, positive to negative
    AluTxn(SUB, 0, 1),       # borrow: C must be 0
]


def random_txns(n):
    """n transactions with every field picked at random."""
    # TODO(step3): return a list of n AluTxn. random.randrange(8) picks a
    # random int from 0 to 7.
    return []


def exhaustive_txns():
    """Every possible transaction, exactly once."""
    # TODO(step3): every op, every a, every b. Three nested loops, or one
    # list comprehension. You should get 2048.
    return []


#=========================================================================
# 2. DRIVER                                                  uvm_driver
#=========================================================================
# Takes transactions off the `todo` queue and puts them on the ALU's input
# pins, one per clock. It is the ONLY piece that drives anything.
#
# It drives on the FALLING edge. The ALU captures on the rising edge, so
# changing inputs half a cycle away leaves them stable when it looks.
# Driving on the same edge the design captures on is a race: it often works
# in simulation and then doesn't in silicon.
class Driver:
    def __init__(self, dut, todo, sent):
        self.dut = dut
        self.todo = todo
        self.sent = sent

    async def run(self):
        while True:
            txn = await self.todo.get()
            await FallingEdge(self.dut.clk)
            self.dut.a.value = txn.a
            # TODO(step3): drive b and op too.

            # Tell the scoreboard what was sent. Given; leave it last.
            await self.sent.put(txn)


#=========================================================================
# 3. MONITOR                                                uvm_monitor
#=========================================================================
# WORKED EXAMPLE, given in full. Read every line.
#
# Watches the output pins and reports what it sees. Drives nothing, ever.
# That restriction is what lets a monitor be attached to hardware you don't
# control, without disturbing it.
#
# The timing: the driver puts transaction 0 on the pins at some falling
# edge. One rising edge later the input registers capture it. One more
# rising edge and its answer is in the output registers. So the answer to
# transaction 0 is visible LATENCY falling edges after it was driven. The
# monitor skips that many edges once, at the start, and after that every
# falling edge's sample lines up with one transaction, in order.
class Monitor:
    def __init__(self, dut, seen):
        self.dut = dut
        self.seen = seen

    async def run(self):
        for _ in range(LATENCY):
            await FallingEdge(self.dut.clk)       # the pipeline is still filling
        while True:
            await FallingEdge(self.dut.clk)
            d = self.dut
            await self.seen.put(AluResult(read(d.y), read(d.n), read(d.z), read(d.c), read(d.v)))


def read(sig):
    """A signal's value as an int, or None if any bit is X or Z. Given."""
    try:
        return int(sig.value)
    except ValueError:
        return None


#=========================================================================
# 4. SCOREBOARD                                          uvm_scoreboard
#=========================================================================
# Pairs what was sent with what came back, asks the model what should have
# come back, and keeps count.
class Scoreboard:
    def __init__(self, sent, seen, coverage):
        self.sent = sent
        self.seen = seen
        self.coverage = coverage
        self.n_seen = 0
        self.n_checked = 0
        self.errors = 0

    # Given: take one of each, check, record coverage.
    #
    # Coverage records which situations the stimulus created, so it uses the
    # model's answer, not the ALU's. A broken ALU shouldn't change what we
    # think we tested.
    async def run(self):
        while True:
            txn = await self.sent.get()        # what the driver sent
            got = await self.seen.get()        # what the monitor saw come back
            self.n_seen += 1
            self.check(txn, got)
            self.coverage.sample(txn, alu(txn.op, txn.a, txn.b))

    def check(self, txn, got):
        # TODO(step3):
        #   1. Ask your model what the answer should be: alu(txn.op, txn.a, txn.b)
        #   2. Add 1 to self.n_checked. Every time.
        #   3. If got != expected, add 1 to self.errors, and print enough to
        #      debug from. "MISMATCH" tells you nothing. Print the check
        #      number, the transaction, what was expected, and what came
        #      back. print() works on all three: see __str__ in AluTxn above,
        #      and in AluResult in alu_model.py.
        #      Only print the first MAX_PRINTED, or one bug buries you.
        pass


#=========================================================================
# 5. COVERAGE                                                covergroup
#=========================================================================
# Passing tells you the ALU got right everything you tried. It says nothing
# about what you never tried. Coverage answers that: of the situations
# worth reaching, which did the stimulus actually reach?
#
# Each "bin" is one situation worth reaching. It counts how many times it
# was hit. A bin stuck at 0 is a hole in your testing, however many tests
# passed.
class Coverage:
    def __init__(self):
        self.bins = {}

        # Given, as the pattern: every opcode was used at least once.
        for name in OP_NAMES:
            self.bins[f"op {name}"] = 0

        # Given: logic ops and shifts produced both a zero and a nonzero result.
        for name in ("AND", "OR", "XOR", "NOT", "SHL", "SHR"):
            for value in (0, 1):
                self.bins[f"{name} z={value}"] = 0

        # TODO(step3): the arithmetic bins. For both ADD and SUB, for each of
        # the four flags, one bin for "it came out 0" and one for "it came
        # out 1". 16 bins in all. Name them like "ADD c=1" and "SUB v=0".
        # These are the interesting ones: "SUB v=1" is the question "did we
        # ever try a subtraction that overflowed?"

    def sample(self, txn, result):
        name = OP_NAMES[txn.op]
        self.bins[f"op {name}"] += 1                  # given, as the pattern
        if txn.op in (ADD, SUB):
            # TODO(step3): count the four flag bins for this result.
            # getattr(result, "c") is the same as result.c, which lets you
            # loop over the flags by name: for flag in "nzcv": ...
            pass
        else:
            self.bins[f"{name} z={result.z}"] += 1

    def report(self):
        """Given. Prints the coverage percentage and every bin never hit."""
        hit = sum(1 for count in self.bins.values() if count > 0)
        percent = 100.0 * hit / len(self.bins)
        print(f" coverage: {percent:.1f}%  ({hit} of {len(self.bins)} bins hit)")
        for name, count in self.bins.items():
            if count == 0:
                print(f"   never hit: {name}")
        return percent


#=========================================================================
# Given: wiring it all together
#=========================================================================
async def reset(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    dut.rst.value = 1
    dut.a.value = 0
    dut.b.value = 0
    dut.op.value = 0
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.rst.value = 0


async def run_txns(dut, txns, label):
    assert len(txns) > 0, "no transactions to send. Did you fill in the generator?"
    await reset(dut)

    # The queues are the only connections between pieces. Everything goes
    # into `todo` up front, so the driver never waits and sends one
    # transaction every single clock.
    todo, sent, seen = Queue(), Queue(), Queue()
    for txn in txns:
        todo.put_nowait(txn)

    coverage = Coverage()
    scoreboard = Scoreboard(sent, seen, coverage)
    cocotb.start_soon(Driver(dut, todo, sent).run())
    cocotb.start_soon(Monitor(dut, seen).run())
    cocotb.start_soon(scoreboard.run())

    while scoreboard.n_seen < len(txns):
        await FallingEdge(dut.clk)

    print()
    print("=" * 60)
    print(f" {label}")
    print(f" sent    : {len(txns)}")
    print(f" checked : {scoreboard.n_checked}")
    print(f" errors  : {scoreboard.errors}")
    coverage.report()
    print("=" * 60)
    passed = scoreboard.errors == 0 and scoreboard.n_checked == len(txns)
    print(" PASS" if passed else " FAIL")
    print()

    assert scoreboard.n_checked == len(txns), (
        f"the scoreboard only checked {scoreboard.n_checked} of {len(txns)}. "
        "Does Scoreboard.check() count every transaction?")
    assert scoreboard.errors == 0, f"{scoreboard.errors} mismatches, see above"


@cocotb.test()
async def test_random(dut):
    """Your corner cases first, then random transactions."""
    randoms = random_txns(N_RANDOM)
    await run_txns(dut, CORNER_CASES + randoms,
                   f"test_random: {len(CORNER_CASES)} corner cases + {len(randoms)} random")


@cocotb.test()
async def test_exhaustive(dut):
    """Every possible input. Only possible because this ALU is tiny."""
    await run_txns(dut, exhaustive_txns(), "test_exhaustive: every possible input")
