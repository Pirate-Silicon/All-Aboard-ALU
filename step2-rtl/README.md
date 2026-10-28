# Step 2: RTL

**Goal:** Turn the spec into SystemVerilog, simulate it, and watch the
two-edge latency happen in a waveform.

**Before you start:** finish [guides/setup.md](../guides/setup.md), and skim
[guides/linux-basics.md](../guides/linux-basics.md). From here on, every
command runs in the container's terminal in VS Code.

## Before you start

1. **[HDLBits](https://hdlbits.01xz.net)**. Free Verilog practice problems that run in your browser and check your answer instantly. It's the fastest way to learn the language. Do these sections from the menu, in order:
   - **Getting Started** (both problems)
   - **Verilog Language: Basics** (all)
   - **Verilog Language: Vectors** (the first four or five)
   - **Verilog Language: Modules: Hierarchy** (the first three)
   - **Verilog Language: Procedures** (all of them; this is where `always` blocks and `case` live)
   - **Circuits: Combinational Logic: Arithmetic Circuits** (the half adder, the full adder, and the multi-bit adders)
   - **Circuits: Sequential Logic: Latches and Flip-Flops** (the first few D flip-flop problems, including the one with synchronous reset)
2. **Harris & Harris chapter 4 videos**, on SystemVerilog:
   - [4.1–4.4 Introduction, Combinational Logic, Delays, Sequential Logic](https://youtu.be/sVy31HJj4lA) (one video)
   - [4.5 Combinational Logic Using always](https://youtu.be/Fhp83VG2fag)
   - [4.6 Signal Assignments](https://youtu.be/KO6kF3Mkm0s). The difference between `=` and `<=`. Watch this one twice.
   - [4.8 Parameterized Modules](https://youtu.be/wF1I1Wl5Owk)
3. **Harris & Harris on flip-flops**:
   - [3.5 D Flip-Flop](https://youtu.be/jFYAqAYtQW8)
   - [3.7 Synchronous Sequential Logic](https://youtu.be/HRX75LSF9vg)
4. **[guides/waveforms.md](../guides/waveforms.md)**. You'll read a waveform at the end of this step.

**HDLBits uses older Verilog, and we use SystemVerilog.** Same ideas, newer
spelling:

| HDLBits (Verilog)       | This program (SystemVerilog) | Why the new one is better                                              |
| ----------------------- | ---------------------------- | ---------------------------------------------------------------------- |
| `wire`, `reg`           | `logic`                      | One type for everything. No more guessing which one.                   |
| `always @(*)`           | `always_comb`                | Tells the tools "this is combinational", and they warn you if it isn't |
| `always @(posedge clk)` | `always_ff @(posedge clk)`   | Tells the tools "this is a flip-flop", and they warn you if it isn't   |

## Background

### What RTL means

RTL stands for register transfer level. You describe hardware as
registers (flip-flops that hold values) and the combinational logic between
them that computes the next values. That's exactly the shape of our ALU:
registers, logic, registers.

It looks like code, but it isn't a program. A program runs one line after
another. The hardware you describe is hardwired, all at once. Every line you
write becomes physical gates and wires, and they all compute simultaneously.

### Three ways to describe logic

|                            | What it is                                                                  | Assignment          | In our ALU                                     |
| -------------------------- | --------------------------------------------------------------------------- | ------------------- | ---------------------------------------------- |
| `assign`                   | One wire, computed from others. Always combinational.                       | `=`                 | `sum`, `diff`, and the flags, in `alu_core.sv` |
| `always_comb`              | A block of combinational logic, where `if` and `case` are allowed           | `=` (blocking)      | choosing `y` by opcode, in `alu_core.sv`       |
| `always_ff @(posedge clk)` | Flip-flops: they change only on a clock edge, and remember their past value | `<=` (non-blocking) | both register banks, in `alu.sv`               |

Never mix them up: `=` inside `always_comb`, and `<=` inside `always_ff`.
Using the wrong one may simulate fine, but will build the wrong hardware.

### Inferred latches

In an `always_comb` block, if there's any path where an output doesn't get
assigned, the hardware has to remember the old value. Remembering takes a
latch, which is a memory element you didn't ask for, with no clock. Synthesis
will build one without complaint, and it's almost always a bug.

The fix is in the skeleton already: assign every output a default value at
the top of the block, before the `case`.

### The sneaky width bug

`diff` is `a + ~b + 1`. You might write:

```systemverilog
assign diff = a + ~b + 1;               // WRONG, and it looks completely fine
```

`diff` is 5 bits wide, so SystemVerilog quietly widens every operand on the
right to 5 bits _before_ doing anything to it. So `b` becomes
`0 b3 b2 b1 b0`, and only then does `~` flip it, into `1 ~b3 ~b2 ~b1 ~b0`.
That extra 1 ends up in the carry bit. The low 4 bits come out right, so the
answers look fine, but C is inverted on every subtraction.

The fix is to invert inside a concatenation block `{}`, which keeps it 4 bits wide:

```systemverilog
assign diff = {1'b0, a} + {1'b0, ~b} + 5'd1;   // right
```

Remember this one. It shows up again in step 3.

## Do

### 1. Read what you're filling in

Open [rtl/alu_core.sv](../rtl/alu_core.sv) and [rtl/alu.sv](../rtl/alu.sv).
The ports, opcode names, and default assignments are done. In `alu_core.sv`,
ADD is the worked example in all three parts (`sum`, the `case` line, and
the overflow rule). In `alu.sv`, the input register bank is written for you.
Every `TODO(step2)` is yours.

Keep your [model/alu_model.py](../model/alu_model.py) open beside it. It's the
same logic in a different language.

### 2. Lint the empty skeleton first

A linter reads your code and complains about things that are legal but
suspicious: width mismatches, unused signals, accidental latches. Verilator's
linter is strict, which is what you want.

```bash
cd rtl
verilator --lint-only -Wall alu.sv alu_core.sv
```

Right now it prints about 19 warnings, like:

```
%Warning-UNDRIVEN: alu.sv:28:28: Signal is not driven: 'y'
%Warning-UNUSEDPARAM: alu_core.sv:34:26: Parameter is not used: 'OP_SUB'
%Warning-UNUSEDSIGNAL: alu_core.sv:51:19: Signal is not used: 'diff'
```

Every one of those points at something you haven't written yet. Watch them
disappear as you work.

### 3. Write alu_core.sv

`diff`, then the seven missing `case` lines, then N, Z, and SUB's overflow
rule.

### 4. Write the output registers in alu.sv

Copy the shape of the input register block.

Three rules (the same ones the pros follow):

- Use `logic`. Not `wire`, not `reg`.
- `=` in `always_comb`, `<=` in `always_ff`.
- Every register gets a value in the `rst` branch. Every single one.

### 5. Lint again, until it's clean

```bash
verilator --lint-only -Wall alu.sv alu_core.sv
```

A clean run prints only Verilator's short summary (lines starting
`- V e r i l a t i o n`), with no `%Warning` or `%Error` lines. Look up any
warning you don't understand in the
[Verilator warnings list](https://verilator.org/guide/latest/warnings.html).

### 6. Simulate

```bash
cd ../tb
make smoke
```

This compiles your RTL with **Icarus Verilog** (a free simulator) and runs
[tb/test_smoke.py](../tb/test_smoke.py), a short test written in Python with
**cocotb**. You'll write a much bigger one in step 3. For now, you're looking
for:

```
=== 1. after reset, every output is 0 ===
  [ ok ] all outputs after reset
...
 SMOKE TEST PASSED, 0 errors
```

The failure lines say what was expected and what you produced. `X` means a
signal was never given a value: an output register you didn't write, or one
missing from the reset branch.

There's a lot of other output too: cocotb's own log lines, with timestamps.
The lines that matter are the ones starting `[ ok ]`, `[FAIL]`, and `SMOKE`.

### 7. Look at the waveform

Open the desktop in a browser tab ([setup](../guides/setup.md), section 5),
then:

```bash
make smoke WAVES=1
make waves
```

Surfer opens on the desktop. [guides/waveforms.md](../guides/waveforms.md)
shows how to add signals and zoom.

Add `clk`, `rst`, `a`, `b`, `op`, `y`, and the four flags. Then add two
internal signals that live inside `alu`: `a_q` (the input register's output)
and `y_d` (the core's answer, before the output register).

Find check 5 near the end: `op` changes to ADD (0) with `a = b = 1`. Count
rising edges until `y` shows 2. You should count two. Watch `a_q` change on
the first edge, `y_d` change right after it (it's combinational: no clock),
and `y` change on the second edge.

Compare it with the timing table you drew in step 1. If they disagree, one of
them is wrong. Work out which before changing anything; sometimes it's the
drawing.

### 8. Save the commands

Now that it works, put it in a script so you never type it again. Create a
new file `step2-rtl/run` in VS Code with this in it:

```bash
#!/usr/bin/env bash
set -e                      # stop at the first command that fails
cd "$(dirname "$0")"        # run from this folder, wherever it's called from
verilator --lint-only -Wall ../rtl/alu.sv ../rtl/alu_core.sv
make -C ../tb smoke
```

Then:

```bash
cd ../step2-rtl
chmod +x run
./run
```

`chmod +x` marks the file as a program you're allowed to run. You only do it
once per script. (If it says `Operation not permitted`, your repo is on a
Windows drive rather than in a container volume. Skip it; `./run` works
anyway.)

Every tool step from here on works this way. Get it right by hand, then save
it. A script you wrote before you understood the commands is a script you
can't debug.

## Check yourself

- `./run` passes lint with no warnings and the smoke test with 0 errors.
- In the waveform, you can point at the edge where `a_q` changes and the edge where `y` changes.
- You can explain why `alu_core.sv` has no clock in it.

<details>
<summary>Why does alu_core have no clock?</summary>

Because it's pure combinational logic: its outputs are a function of its
inputs right now, with no memory. The clock only matters where something has
to _remember_ a value until the next edge, and that's the registers in
`alu.sv`. Keeping the two apart is what lets step 4 talk cleanly about "the
logic between two registers".

</details>

<details>
<summary>Why does y_d change between clock edges, but y doesn't?</summary>

`y_d` is the output of combinational logic, so it changes whenever its inputs
(`a_q`, `b_q`, `op_q`) change, a moment after the first edge. `y` is a
register, so it only takes `y_d`'s value at the next rising edge. That gap,
between `y_d` settling and the next edge arriving, is exactly what step 4 is
about.

</details>

## Stuck?

| What you see                                     | What's wrong                                                                                                          |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `%Warning-LATCH`                                 | Some path through `always_comb` doesn't assign an output. Check the defaults at the top of the block are still there. |
| `%Warning-WIDTHEXPAND` or `WIDTHTRUNC`           | Two sides of an operation have different widths. Usually a missing `{1'b0, ...}`.                                     |
| `%Warning-UNUSEDSIGNAL`                          | Something is declared or computed and never used. Often a typo in a name, or a TODO not done yet.                     |
| `%Warning-UNDRIVEN`                              | Something is used but never given a value. In `alu.sv`, that's the output registers.                                  |
| Smoke check 3 fails on C only                    | The width bug above. Put `~b` inside `{}`.                                                                            |
| Smoke check 1 fails, outputs show X              | An output register isn't in the reset branch, or isn't written at all.                                                |
| Check 5 fails: `y` updates after one edge        | You have one register bank, not two. Is the core fed from `a_q`, not `a`?                                             |
| `syntax error` on a line that looks fine         | Look at the line _above_. Usually a missing `;` or `end`.                                                             |
| `make: cocotb-config: No such file or directory` | You're outside the container. See [setup](../guides/setup.md).                                                        |
| `make waves` does nothing visible                | The desktop isn't open in your browser, or you didn't record with `WAVES=1` first.                                    |

## Go further

- **Build the adder from parts.** Write a `full_adder` module (HDLBits has one) and chain four of them into a ripple-carry adder. Use it for `sum` and `diff` instead of `+`. Step 5 will show you whether synthesis builds anything different.
- **One adder, not two.** As written, `sum` and `diff` are two separate adders. Harris & Harris video [5.7](https://youtu.be/WXMf0y4NoBw) shows how one adder can do both by optionally inverting `b`. Rewrite `alu_core.sv` that way, re-run the smoke test, and save it for comparison in step 5.
