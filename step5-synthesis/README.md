# Step 5: Synthesis

**Goal:** Turn your RTL into real sky130 gates, find out whether your step 4
prediction was right, and check that synthesis didn't break anything.

Four parts: see what synthesis does (A), do it for real against sky130 (B),
time the result (C), and simulate the gates (D).

## Watch and read

1. **[The EDA Primer](https://newsletter.semianalysis.com/p/the-eda-primer-from-rtl-to-silicon)**, the Logic Synthesis section, if you skipped it in step 4.
2. **[Yosys documentation: Getting started](https://yosyshq.readthedocs.io/projects/yosys/en/latest/getting_started/index.html)**. Skim it. Yosys is the open-source synthesis tool, used by every open-source chip flow.
3. **Optional, for how synthesis works inside:** [VLSI CAD Part I: Logic](https://www.coursera.org/learn/vlsi-cad-logic), Rob Rutenbar's course. Free to audit. Weeks 1–3 cover the algorithms Yosys and ABC use.

## Background

Your RTL says _what_ the hardware does. Synthesis decides _how_, out of the
cells a real library actually has. It works in stages:

1. **Elaborate:** read the SystemVerilog, work out the hierarchy, and figure out which signals become flip-flops (the ones assigned in `always_ff`).
2. **Optimize:** treat the logic as Boolean equations and simplify them. Remove anything unused, merge anything duplicated.
3. **Map:** pick real cells out of the sky130 library to build what's left. Yosys hands this part to a tool inside it called **ABC**, which uses the delay tables you read in step 4 to choose cells.

The output is a **gate-level netlist**: still Verilog, but now nothing but
instances of library cells and the wires between them.

Then you check it two ways. **Static timing analysis** (OpenSTA) adds up the
delays along every path and compares them to your clock period. **Gate-level
simulation** runs your step 3 testbench again, on the gates instead of the
RTL. Synthesis tools are good, but "good" isn't "proven", and designers
check.

This is also exactly how the start of LibreLane's flow works: it runs Yosys,
then OpenSTA, before anything physical happens. You're doing by hand what
steps 6 and 7 automate.

## Part A: Watch synthesis happen

Start Yosys's interactive shell:

```bash
cd step5-synthesis
yosys
```

You get a `yosys>` prompt. Type these one at a time, and read what each
prints:

```
read_verilog -sv ../rtl/alu_core.sv ../rtl/alu.sv
hierarchy -top alu_core
proc
opt
show -format png -prefix core_rtl
```

- `read_verilog` parses your files.
- `hierarchy -top alu_core` says which module to work on. Just the core for now: it's easier to look at without the registers.
- `proc` turns `always` blocks into plain logic.
- `opt` cleans it up.
- `show` draws the result as a picture, `core_rtl.png`.

Open `step5-synthesis/core_rtl.png` in VS Code (click it in the file
explorer). This is your design as Yosys understands it, before any real
gates. Find:

- the `$add` cells: one for `sum`, two for `diff` (`a + ~b`, then `+ 1`)
- the `$and`, `$or`, `$xor`, and `$not` for the logic operations
- eight comparators, one checking `op` against each opcode
- a `$pmux` (a many-input mux) choosing `y`

Every one of those came from a line you wrote. Now synthesize it into
generic gates and draw it again:

```
synth -top alu_core
show -format png -prefix core_gates
stat
exit
```

Open `core_gates.png`. Same ALU, now as individual AND, OR, XOR, and MUX
gates. It's much harder to read, and that's the point: this is why nobody
designs at the gate level any more. `stat` printed how many of each gate.

## Part B: Synthesize for sky130

Now the real thing: the whole design, registers included, built from sky130
cells. This time put the commands in a script. Create
`step5-synthesis/synth.tcl`:

```tcl
# synth.tcl: turn the RTL into sky130 gates.
yosys -import
set lib $::env(LIB_TT)

read_verilog -sv ../rtl/alu_core.sv ../rtl/alu.sv
synth -top alu -flatten
dfflibmap -liberty $lib
abc -liberty $lib -dont_use *lpflow*
delete {t:$scopeinfo}
autoname
opt_clean
stat -liberty $lib
write_verilog -noattr alu_synth.v
```

What's new:

- `$::env(LIB_TT)` is Tcl for "the environment variable `LIB_TT`": the same typical-corner library you read in step 4.
- `synth -top alu -flatten` synthesizes the whole design and **flattens** it: the `alu_core` instance dissolves into `alu`, so optimization can cross the boundary.
- `dfflibmap` replaces each flip-flop with a real sky130 flip-flop cell.
- `abc` maps all the logic onto real sky130 cells. `-dont_use *lpflow*` keeps it away from special low-power cells that need extra wiring. Real flows forbid them too.
- `delete` and `autoname` tidy up. `autoname` names each cell after the signal it drives, so step C's timing report says `z_..._dfxtp_1_Q` instead of `_157_`.
- `stat -liberty` reports cell counts _and_ area, from the library.
- `write_verilog` writes the netlist.

Run it:

```bash
yosys -c synth.tcl -l synth.log
```

It prints a lot. Near the end is the `stat` table: every cell type used, how
many, and the total **Chip area**. Note the area, and count the flip-flops
(`dfxtp`).

(ABC prints a few lines like `Scl_LibertyReadGenlib() skipped sequential
cell`. That's normal. It's ignoring flip-flops, which `dfflibmap` already
handled.)

Check for latches:

```bash
grep "Latch inferred" synth.log
```

No output is what you want. (Type it exactly, with the capital L: the log is
full of harmless lines like `No latch inferred`.) A latch means some
`always_comb` path in your RTL doesn't assign an output: go back to step 2
and fix it.

Now look at what you made:

```bash
less alu_synth.v
```

It's your ALU as about a hundred instances of sky130 cells. Pick a cell name
and look it up in the library, the same way you found the inverter in step 4.
For `sky130_fd_sc_hd__a21oi_1`, that's `less -p __a21oi_1 $LIB_TT`.

## Part C: Time it

Create `step5-synthesis/sta.tcl`:

```tcl
# sta.tcl: static timing analysis of the synthesized netlist.
read_liberty $::env(LIB_TT)
read_verilog alu_synth.v
link_design alu
read_sdc ../step4-timing/constraints.sdc

report_checks -path_delay max -fields {slew cap fanout} -digits 3
report_checks -path_delay min -digits 3
report_wns
report_tns
```

Run it with OpenSTA:

```bash
sta -no_splash -exit sta.tcl
```

The first report is your **critical path**, the slowest one. Read it top to
bottom:

- **Startpoint** and **Endpoint**: where the path begins and ends. Compare them to your step 4 prediction.
- Each row is one gate along the path. **Delay** is that gate's delay, and **Time** is the running total.
- **data arrival time** is when the signal gets there. **data required time** is the deadline: the clock period, minus the flip-flop's setup time.
- **slack** is required minus arrival. `(MET)` means positive.

The second report (`-path_delay min`) is the **hold** check: the _fastest_
path, making sure nothing arrives too early.

Then work out the real F<sub>max</sub>:

**T<sub>min</sub> = data arrival time + library setup time**

Compare it with your step 4 estimate. How close were you?

Two things this number doesn't include yet: **wires**, which have resistance
and capacitance and slow everything down, and the **clock tree**. The report
says `clock network delay (ideal)`, meaning it assumes the clock reaches
every flip-flop at the same instant. Step 7 adds both.

## Part D: Simulate the gates

Synthesis just rewrote your design. The way to check it got it right is to
run your step 3 testbench again, on the gates:

```bash
make -C ../tb test GATES=1
```

Same tests, same model, same expected results: both tests `PASS`. The
simulator reads `alu_synth.v` plus a Verilog model of every sky130 cell, so
it knows what a `sky130_fd_sc_hd__maj3_1` does.

If it passed in step 3 and fails here, believe it. That's exactly the kind of
bug this step exists to catch.

## Save the commands

Create `step5-synthesis/run`:

```bash
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
yosys -q -c synth.tcl -l synth.log
sta -no_splash -exit sta.tcl | tee sta.log
make -C ../tb test GATES=1
```

`chmod +x run`, then `./run`. (`-q` keeps Yosys quiet: everything still goes
to `synth.log`. `tee` shows the timing report and also saves it to
`sta.log`.)

## Check yourself

- No latches in `synth.log`.
- Slack is positive at your clock period.
- The gate-level simulation passes both tests.
- You can point at your critical path's start point and end point, and say whether you predicted them.
- You can explain the flip-flop count.

<details>
<summary>Why are there 18 flip-flops, not 19?</summary>

Count them in the RTL: 4 for `a_q`, 4 for `b_q`, 3 for `op_q`, 4 for `y`, and
one each for `n`, `z`, `c`, and `v`. That's 19.

But `n` is defined as `y[3]`. Those two registers are loaded with the same
value on every clock edge, forever, so they always hold the same thing.
Synthesis noticed and kept only one, which drives both outputs. Look in
`alu_synth.v`: there are flip-flops named after `y` for three of its bits, and
one named after `n`.

That's optimization doing exactly its job, on something you might not have
noticed yourself.

</details>

<details>
<summary>What the reference ALU got</summary>

At the typical corner, with a 10 ns clock: 105 cells and about 908 µm² of
cell area. The critical path starts at an `a_q` bit, runs through the carry
chain and the opcode mux, and ends at the **V** flag's flip-flop, arriving at
1.705 ns. Slack 8.225 ns. Add the 0.070 ns setup time and
F<sub>max</sub> comes out around 563 MHz, before wires. The hold check's
tightest path goes from the `rst` input straight into a flip-flop, with 0.07 ns
to spare.

Your numbers will differ a little if your RTL is written differently. That's
expected: synthesis makes different choices for different code.

</details>

## Stuck?

| What you see                                             | What's wrong                                                                                                                                       |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `can't read "::env(LIB_TT)": no such variable`           | You're outside the container, or in an old terminal. Open a new one in VS Code.                                                                    |
| `ERROR: Module ... is not part of the design`            | A typo in a file path or a module name. Run from inside `step5-synthesis/`.                                                                        |
| `Latch inferred for signal` in the log                   | An `always_comb` path that doesn't assign every output. Fix it in step 2's RTL.                                                                    |
| Lots of lines mentioning `latch` or `DLATCH`             | Normal. Yosys lists every latch cell it _could_ use. Only `Latch inferred` (capital L) means it built one.                                         |
| `sta`: `cannot open alu_synth.v`                         | Run synthesis (Part B) first.                                                                                                                      |
| Slack is negative                                        | Your clock period is shorter than the path. Make it longer in `step4-timing/constraints.sdc`, or keep it and see what step 7 thinks.               |
| `GATES=1` fails, but step 3 passed                       | A real difference between the RTL and the gates, which is interesting. Most likely an X: a register with no reset. Re-run with `WAVES=1` and look. |
| `show` prints `Dumping to core_rtl.dot` and nothing else | That's fine: it also wrote `core_rtl.png`. Look in the file explorer.                                                                              |

## Go further

- **Three adders.** If you built the ripple-carry adder from full adders in step 2, synthesize that version too. Then try a carry-lookahead adder (Harris & Harris video [5.4](https://youtu.be/aD-qA-jEKV0)). Compare area and critical path for all three, including the plain `+`.
- **The slow corner.** Change `LIB_TT` in your scripts to the slow corner library, `$PDKPATH/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ss_100C_1v60.lib`, and re-run both. How much slower is the same netlist on slow silicon at 100 °C?
- **Tell ABC your target.** `abc -D 2000 -liberty $lib ...` tells ABC to aim for a 2000 ps path. Does a tighter target change the cells it picks, the area, or the slack?
