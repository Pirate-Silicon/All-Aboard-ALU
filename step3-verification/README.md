# Step 3: Verification

**Goal:** Build a self-checking testbench out of the same pieces industry
uses, prove your ALU with it, and then use it to catch the bugs in somebody
else's ALU.

## Watch and read

1. **[Harris & Harris 4.9: Testbenches](https://youtu.be/V14aROKd6zU)**. The basic idea of a testbench, in SystemVerilog.
2. **[cocotb: Writing Testbenches](https://docs.cocotb.org/en/stable/writing_testbenches.html)**. Read the first few sections. cocotb lets you write the testbench in Python while the hardware stays in SystemVerilog.
3. **[chipverify: UVM Tutorial](https://www.chipverify.com/uvm/uvm-tutorial)**. Skim the introduction and the "testbench structure" pages. You won't write UVM here, but you'll build the same pieces it's made of, under the same names.

## Background

### Verification isn't running it once

Running your design once and eyeballing the answer isn't verification. You
decide ahead of time what could go wrong, then build something that checks
for it automatically, every time, and prints PASS or FAIL. Nobody reads a
waveform unless something failed.

At most chip companies there are more verification engineers than
designers. A bug found in simulation costs a few minutes. The same bug found
in silicon costs a new mask set and months of waiting (go back to the step 0
primer for the numbers).

### The one rule

**Work out the expected answers from the spec, never from your RTL.** If the
expected answers and the design come from the same understanding, they agree
with each other, and both can be wrong. Your testbench would pass cleanly
and prove nothing.

You already did this right: your model in `model/alu_model.py` was written
from the spec in step 1, before any RTL existed. The testbench imports that
exact file.

### Directed, random, and exhaustive

| Kind           | What it is                       | Finds                                                   |
| -------------- | -------------------------------- | ------------------------------------------------------- |
| **Directed**   | You pick the inputs: "try 7 + 1" | The bugs you thought of                                 |
| **Random**     | The computer picks the inputs    | Bugs you didn't think of, if it happens to land on them |
| **Exhaustive** | Every possible input             | Everything, but only possible when the design is tiny   |

Our ALU has 2048 possible inputs, so you can test every one in under a
second. A 32-bit ALU has about 10<sup>20</sup>. Real hardware is tested with
directed and random tests, plus coverage to measure what the random tests
actually reached. This step does all three, so you can see what exhaustive
testing catches that the other two miss.

### The six pieces

Every industrial testbench is built from these, whatever framework wraps
them. UVM is the SystemVerilog framework most companies use, and these are
its names for them:

| Piece       | Job                                                                  | UVM name            |
| ----------- | -------------------------------------------------------------------- | ------------------- |
| Transaction | one operation to try: "ADD, a = 7, b = 1"                            | `uvm_sequence_item` |
| Generator   | makes lists of transactions                                          | `uvm_sequence`      |
| Driver      | turns a transaction into values on the input pins                    | `uvm_driver`        |
| Monitor     | watches the output pins and reports what it saw. **Drives nothing.** | `uvm_monitor`       |
| Model       | says what the answer should be                                       | reference model     |
| Scoreboard  | pairs what was sent with what came back, asks the model, counts      | `uvm_scoreboard`    |
| Coverage    | counts which interesting situations were actually reached            | `covergroup`        |

(Seven rows: the transaction is the thing the other six pass around.)

```
 ┌───────────┐  todo  ┌──────────┐   pins   ┌──────────┐
 │ GENERATOR │───────►│  DRIVER  │─────────►│   DUT    │
 │           │ queue  │          │          │  alu.sv  │
 └───────────┘        └────┬─────┘          └────┬─────┘
                           │ sent                │ pins
                           │ "what I sent"       ▼
                           │               ┌──────────┐
                           │               │ MONITOR  │
                           │               │ watches, │
                           │               │ drives   │
                           │               │ nothing  │
                           │               └────┬─────┘
                           │                    │ seen
                           ▼                    ▼ "what came back"
                     ┌───────────────────────────────┐
  ┌─────────┐        │          SCOREBOARD           │──► COVERAGE
  │  MODEL  │───────►│ expected = model(what I sent) │
  │ step 1  │        │ if what came back != expected │
  └─────────┘        │   count it, print why         │
                     └───────────────────────────────┘
```

The pieces talk only through **queues**, never by reaching into each other's
variables. That's the point. You can swap the generator without touching the
driver, and the monitor can watch hardware it has no control over.

The DUT (design under test) is whatever ALU is compiled in: yours, or
the buggy one.

## Part A: Plan it

1. **List corner cases.** What inputs are most likely to expose a bug in _this_ ALU? Not a generic checklist: go back to your step 1 answers and [SPEC.md](../step1-spec/SPEC.md). Aim for at least 10. Think about every flag being both 0 and 1, the edges of the signed range, the SUB carry rule, logic ops with values that _would_ overflow if they were adds, shifts of the top and bottom bits, and right after reset.
2. **Draw the testbench** as a block diagram, without copying the one above. Mark which pieces drive the DUT and which only watch it.
3. **Make two predictions**, and write them down before Part B:
   - Will 500 random transactions make every flag come out both 0 and 1, for both ADD and SUB?
   - Suppose a bug only happens for one specific `(a, b)` pair on one operation. What are the odds 500 random transactions hit it? (There are 2048 possible inputs.)

<details>
<summary>Prediction 2, worked out</summary>

Each random transaction has a 1 in 2048 chance of being that exact input. The
chance that all 500 miss it is (2047/2048)<sup>500</sup>, about 78%. So random
testing misses it about four times out of five. Keep that in mind for
Part C.

</details>

## Part B: Build it, and run it on your ALU

Open [tb/test_alu.py](../tb/test_alu.py). It's one file, in numbered
sections, one per piece. Read the whole thing before writing anything. The
monitor is written in full as the worked example, so read it closely.
Every `TODO(step3)` is yours, and the comment above each one says what
question you're answering.

Work in this order:

1. **Generator.** Your corner cases from Part A, plus `random_txns()` and `exhaustive_txns()`.
2. **Driver.** Two lines.
3. **Scoreboard.** `check()`: ask the model, compare, count, and print a failure message you could easily debug
4. **Coverage.** The 16 ADD and SUB flag bins.

Run it:

```bash
cd tb
make test
```

It runs two tests: `test_random` (your corner cases plus 500 random) and
`test_exhaustive` (all 2048). Each prints a summary box. In cocotb's
own log lines, you're looking for:

```
 test_random: 15 corner cases + 500 random
 sent    : 515
 checked : 515
 errors  : 0
 coverage: 100.0%  (36 of 36 bins hit)
 PASS
```

and the same for `test_exhaustive`. At the very end, cocotb prints a table
with one row per test, and `PASS` or `FAIL` for each.

If something fails, either your RTL is wrong or your model is wrong.
Working out which is the actual skill. Read the failure line: the
transaction, what was expected, and what came back. Work out the right
answer by hand from the spec. Whichever one disagrees with you is the bug.
To see it happen, re-run with `WAVES=1`, then `make waves`, and find that
transaction in the waveform.

**If coverage is below 100%**, the report names every bin never hit. Add a
corner case that hits it. A common one is:

```
 coverage: 97.2%  (35 of 36 bins hit)
   never hit: OR z=1
```

Work out why before you fix it. (What does it take for OR to produce zero,
and how likely is that from random inputs?)

**Run test_random a few more times** with different seeds:

```bash
make test RANDOM_SEED=1
make test RANDOM_SEED=2
```

Is random coverage 100% every time without your corner cases? Comment them
out and see.

## Part C: The vendor ALU

[rtl/alu_buggy.sv](../rtl/alu_buggy.sv) is an ALU somebody else wrote,
against the same spec and the same ports. Read the header only, not the
code. In industry this is routine: blocks arrive from other teams and from
outside vendors with a datasheet and no warranty. You don't get to assume
they work. You get to find out, with a testbench built against a spec you
understand better than its author did.

```bash
make test DUT=buggy
```

It should fail. Find every distinct bug. For each one, write down:

1. a transaction that catches it, from the failure lines
2. the sentence of [SPEC.md](../step1-spec/SPEC.md) it breaks
3. what you'd tell the vendor to fix, in one sentence

The failure lines only show the first 10 mismatches, and one major bug can
hide a minor one. Once you think you know what a bug is, temporarily add a
check to your scoreboard that skips it (for example, ignore C on SUB), then
re-run to see what's left. Take the skip back out when you're done.

Then answer:

- **Which bugs did `test_random` find? Which did only `test_exhaustive` find?** Try several seeds.
- **What did coverage say on the runs where a bug was missed?** What does that tell you about what coverage does and doesn't measure?

If your testbench catches nothing, the vendor ALU isn't the thing that's
broken.

## Part D: Bonus, the same testbench in SystemVerilog

Optional. For anyone curious how this looks in the language most
verification is written in.

[tb_sv/alu_tb.sv](../tb_sv/alu_tb.sv) is the same testbench, piece for
piece, in plain SystemVerilog: classes, `mailboxes` instead of queues,
`randomize()` instead of `random`, and a hand-written model (it can't import
Python). It has the same `TODO(step3)` structure.

```bash
cd tb_sv
make                    # random, on your ALU
make EXHAUSTIVE=1       # every input
make DUT=buggy          # on the vendor ALU
```

It's compiled with Verilator, the same tool you've been linting with,
which can also run testbenches like this one. It turns the whole thing into a
C++ program first, so the first build takes a few seconds. Look for the same
summary box as the Python version, ending in `PASS` or `FAIL`.

| This program (cocotb) | `tb_sv/alu_tb.sv`                 | Real UVM               | What UVM's version adds                                        |
| --------------------- | --------------------------------- | ---------------------- | -------------------------------------------------------------- |
| `AluTxn` dataclass    | `AluTxn` class with `rand` fields | `uvm_sequence_item`    | free print, copy, and compare methods                          |
| `random_txns()`       | `add_random()` task               | `uvm_sequence`         | many sequences can share one driver                            |
| `Driver.run()`        | `driver()` task                   | `uvm_driver`           | a handshake, so a sequence can react to what the DUT does      |
| `Monitor.run()`       | `monitor()` task                  | `uvm_monitor`          | broadcasts to any number of listeners, not just one queue      |
| `Scoreboard`          | `scoreboard()` task               | `uvm_scoreboard`       | subscribes to a broadcast instead of being wired to one source |
| `Coverage` dict       | counter arrays                    | `covergroup`           | crosses and bins declared in a few lines, plus tool reports    |
| `cocotb.queue.Queue`  | `mailbox`                         | TLM ports              | —                                                              |
| `run_txns()`          | the `initial` block               | `uvm_env` + `uvm_test` | swap stimulus without touching any other file                  |

The one thing that never changes is the model. In every framework, the
reference model is the design knowledge, and everything around it is
plumbing.

To try real UVM, [EDA Playground](https://www.edaplayground.com) has free
commercial simulators with UVM built in, and many UVM examples. If you'd
rather stay in Python, [pyuvm](https://github.com/pyuvm/pyuvm) is UVM
written on top of cocotb.

## Save your commands

Create `step3-verification/run`:

```bash
#!/usr/bin/env bash
cd "$(dirname "$0")"
make -C ../tb test
make -C ../tb test DUT=buggy
```

(No `set -e` this time: the second command is _supposed_ to fail.) Then
`chmod +x run` and `./run`, the same as step 2.

## Check yourself

- `make test` passes both tests with 100% coverage on your ALU.
- You found every bug in the vendor ALU, each with a transaction, a spec sentence, and a fix.
- You can say what a driver, a monitor, and a scoreboard each do, without looking.
- You can explain why 100% coverage didn't mean the vendor ALU was correct.

<details>
<summary>How many bugs are in the vendor ALU? (spoiler: just the count)</summary>

Four. `test_exhaustive` reports 495 mismatches in all. If you've found three,
the fourth is the quiet one: once you're skipping the three you know about,
`test_exhaustive` still fails and `test_random` usually doesn't.

</details>

<details>
<summary>Why is OR z=1 so hard to hit at random?</summary>

OR gives zero only when both inputs are zero: one input pair out of 256. With
about 60 random OR operations in a 500-transaction run, there's roughly a 21%
chance of hitting it. That's why corner cases exist: you put in the ones you
know randomness will probably miss.

</details>

<details>
<summary>Why does the monitor drive nothing?</summary>

So it can be trusted, and so it can be reused. A monitor that only observes
can be attached to any interface, including one between two blocks you
didn't write, without changing what happens there. If it also drove signals,
it could hide the very bug it's watching for.

</details>

<details>
<summary>Why didn't 100% coverage mean "correct"?</summary>

Coverage only measures the situations _you_ decided were interesting. Our
bins ask "did each flag come out 0 and 1?", not "did we try every input?".
A bug living at one specific input can sit in a perfectly covered design.
Coverage tells you where you haven't looked. It can't tell you that where
you did look is enough. Choosing good bins is a real engineering skill.

</details>

## Stuck?

| What you see                                                                    | What's wrong                                                                                                 |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `no transactions to send`                                                       | `random_txns()` or `exhaustive_txns()` still returns `[]`.                                                   |
| `the scoreboard only checked 0`                                                 | `check()` never adds to `self.n_checked`.                                                                    |
| Every transaction fails, and `got` looks like the previous transaction's answer | The pairing is off by one. Did you change `LATENCY`, or add an `await` in the driver?                        |
| `ModuleNotFoundError: alu_model`                                                | Run `make` from inside `tb/`. The Makefile is what tells Python where `model/` is.                           |
| `KeyError: 'ADD c=1'`                                                           | A bin name in `sample()` doesn't exactly match one in `__init__`. Check spaces and capitals.                 |
| Your ALU fails, and you're sure the RTL is right                                | Re-run `python3 check_model.py` in `model/`. Then work the failing case by hand.                             |
| The test hangs forever                                                          | Ctrl-C. A queue is waiting for something that never comes. Did you delete the `sent.put` line in the driver? |
