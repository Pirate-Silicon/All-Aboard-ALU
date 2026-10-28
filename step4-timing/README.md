# Step 4: Timing, Predicted by Hand

**Goal:** Understand what limits how fast a chip can run, predict your ALU's
slowest path and top clock speed by hand, and pick the clock period you'll
check against in step 5.

## Watch and read

1. **Harris & Harris:**
   - [2.15 Timing of Combinational Logic](https://youtu.be/0KK4qXW7IUI)
   - [3.13 Timing](https://youtu.be/BZE-8ZiVzTw). This is the core of this step.
   - [3.14 Clock Skew](https://youtu.be/1OodJEhXHS4)
   - [5.3 Ripple-Carry Adders](https://youtu.be/mSwJvYz8nOQ). Why adders are slow.
2. **[Basic Static Timing Analysis](https://www.youtube.com/watch?v=Hxq1Xmr4Rpw)**, Cadence. The industry view of the same ideas.
3. **[The EDA Primer](https://newsletter.semianalysis.com/p/the-eda-primer-from-rtl-to-silicon)** from step 0, again: the Logic Synthesis and Process Corners sections. They'll make much more sense now.

## Background

### Every gate takes time

When a gate's input changes, its output doesn't change instantly. It takes a
little while, called the propagation delay: tens to hundreds of
picoseconds in sky130. Chain gates together and the delays add up.

### Registers set the deadline

Our ALU has registers on both sides of its logic:

```
 input regs ──► [ alu_core: lots of gates ] ──► output regs
     ▲                                              ▲
    clk                                            clk
```

On a rising edge, the input registers launch new values. They then have to
ripple through every gate in `alu_core` and arrive at the output registers
before the _next_ rising edge, with a little time to spare. Three numbers
decide whether they make it:

- **Clock-to-Q** (t<sub>pcq</sub>): how long after the edge a flip-flop's output actually changes.
- **Propagation delay** (t<sub>pd</sub>): how long the logic takes, along its slowest route.
- **Setup time** (t<sub>setup</sub>): how long before the next edge a flip-flop's input must be steady, so it captures the right value.

The rule every synchronous chip lives by:

**T<sub>clock</sub> ≥ t<sub>pcq</sub> + t<sub>pd</sub> + t<sub>setup</sub>**

The slowest route through the logic is the **critical path**. It sets the
fastest clock the design can run at, F<sub>max</sub> = 1 / T<sub>min</sub>.

**Slack** is how much time is left over: the clock period, minus how long the
path actually takes. Positive slack means the path made it. **Negative slack
means you asked for a faster clock than the logic can deliver**, and the chip
won't work at that speed.

**Hold time** is the opposite problem. A flip-flop's input must also stay
steady for a moment _after_ the edge, so a path can be too _fast_. Hold
problems don't depend on the clock period at all, which is why they're
checked separately.

### Where the delay numbers come from

Every gate available in sky130 (an inverter, a NAND, a flip-flop, and about
430 others) is a **standard cell**: a small, pre-designed, pre-measured
layout. The foundry measures each one and publishes its numbers in a
**liberty file** (`.lib`). Synthesis and timing tools read it.

A cell's delay isn't one number. It depends on two things:

- how fast its input is changing (the **input transition**, or slew): a lazy input makes a slow gate
- how much it has to drive (the **output load**, in capacitance): more wires and more gates downstream make it slower

So the library stores delay as a **lookup table**: 7 transitions by 7 loads,
49 numbers per timing arc.

### Corners

Transistors don't all come out of the factory identical, and they run slower
when hot or at low voltage. So a library comes in versions called
**corners**. Our file name says which one it is:

`sky130_fd_sc_hd__tt_025C_1v80.lib`: **t**ypical (tt) transistors, **25** °C, **1.80** V.

There's also an `ss` (slow-slow, 100 °C, 1.60 V) and an `ff` (fast-fast,
−40 °C, 1.95 V). A real chip must work at all of them. We use typical here;
step 7 checks all of them at once.

## Do

### 1. In your own words

On paper or in a notes file: what's a critical path? What's slack, and what
does negative slack mean? If a design has negative slack, name three ways to
fix it, and what each one costs you.

<details>
<summary>Some answers</summary>

- **Slow the clock down** (a longer period). Costs speed, which may be the whole point of the design.
- **Use faster gates.** Bigger cells (`_2`, `_4` versions) drive harder and switch faster. Costs area and power.
- **Restructure the logic** so the slow path has fewer gates, like a faster adder (step 8's go-further). Costs design effort and usually area.
- **Pipeline:** add a register partway along the path, splitting it in two. Costs a clock cycle of latency, and changes the spec.
- **Move cells closer together** so the wires are shorter (step 7). Costs area, or placement effort.

</details>

### 2. Predict the critical path

On paper, draw the ALU between its two register banks. Then think through
which path is longest. Some questions to steer you:

- The adder's carry has to ripple from bit 0 to bit 3. Which outputs depend on that whole chain?
- SUB inverts `b` before it reaches the adder. Does that add a gate to the path?
- `y` goes through the opcode mux. Which flags are computed _after_ `y`, from `y`?
- Z needs all four bits of `y` at once. What does that mean for when Z can be ready?

**Commit to an answer:** the start point (which input register bit) and the
end point (which output register). Write it down. Step 5's timing tool will
tell you if you were right.

### 3. Open the cell library

In the container's terminal:

```bash
less $LIB_TT
```

`$LIB_TT` is set up by the container to point at the typical-corner library.
It's a 12 MB text file. In `less`, type `/` followed by text to search, and
`n` for the next match. `q` quits.

Search for `cell ("sky130_fd_sc_hd__inv_1")`. This is the smallest inverter
in the library. Write down:

- its `area` (in µm²)
- its `cell_leakage_power` (the units are given near the top of the file: search `leakage_power_unit`)
- the `capacitance` of its input pin `A` (units: `capacitive_load_unit`)
- one number out of its `cell_rise` table, and what the table's two axes are. Search the file for the table's template name (it says `del_1_7_7`) to find out what `variable_1` and `variable_2` mean.

Then look up three more:

- **`sky130_fd_sc_hd__dfxtp_1`**, the plain D flip-flop. How much bigger is it than the inverter? Find its clock-to-Q delay (the `cell_rise` under pin `Q`) and its setup time (under pin `D`, the timing block with `timing_type : "setup_rising"`).
- **`sky130_fd_sc_hd__maj3_1`**, a 3-input majority gate. Its output is 1 when at least two inputs are 1. That's exactly the carry out of a full adder, which is why synthesis uses it.
- **`sky130_fd_sc_hd__xor2_1`**, the XOR gate. Compare its delay to the inverter's.

<details>
<summary>What you should have found</summary>

- `inv_1`: area 3.7536 µm², leakage about 0.0053 nW, input capacitance about 0.0023 pF.
- The delay table axes: `variable_1` is **`input_net_transition`** (ns) and `variable_2` is **`total_output_net_capacitance`** (pF). The very first entry, for the fastest input into the lightest load, is about 0.020 ns (20 ps). The last, for the slowest input into the heaviest load, is over 1 ns. Same gate, 50 times slower.
- `dfxtp_1`: area 20.02 µm², more than five inverters. Clock-to-Q is roughly 0.27–0.45 ns for realistic loads.
- `maj3_1`: about 0.11 ns at the lightest load, and over 1 ns at the heaviest. At any given load it's much slower than an inverter, and a 4-bit carry chain can have several of them in a row.
- `xor2_1`: noticeably slower than the inverter, and more than twice its area.

</details>

The `.lib` is what synthesis and timing tools read. Place and route needs a
different view of the same cells, their **physical** shape, which lives in a
LEF file:

```bash
less $PDKPATH/libs.ref/sky130_fd_sc_hd/lef/sky130_fd_sc_hd.lef
```

Search `/MACRO sky130_fd_sc_hd__inv_1`. Its `SIZE` line says how big it is,
and its `PIN` blocks say where the router may connect. Then look at the
flip-flop's `SIZE`. Notice anything about the second number?

<details>
<summary>The second number</summary>

Both are 2.72 µm tall: the inverter is 1.38 × 2.72, and the flip-flop is
7.36 × 2.72. **Every standard cell in the library is the same height.** That's
what lets placement pack them into rows like bricks, and it's why the power
rails can run straight along the top and bottom of every row. Step 6 shows you
those rows.

</details>

### 4. See the cell itself

Open the container's desktop in your browser ([setup](../guides/setup.md),
section 5), then run:

```bash
T=$PDKPATH/libs.tech/klayout/tech
klayout -nn $T/sky130A.lyt -l $T/sky130A.lyp $PDKPATH/libs.ref/sky130_fd_sc_hd/gds/sky130_fd_sc_hd.gds &
```

KLayout opens on the desktop. The `-nn` and `-l` options load sky130's layer
names and colors. Without them, every layer shows up as a bare number.

1. A **Tip** box pops up about showing the full hierarchy. Click **Yes**.
2. The file has hundreds of cells and shows none of them yet. In the **Cells** panel on the left, scroll down to `sky130_fd_sc_hd__inv_1`. **Right-click it and choose Show As New Top.** (Double-clicking just expands the tree.)
3. Press **F** to fit it to the window.

What you're looking at is two transistors, plus the wiring to reach them:

```
 ┌──────────────────────┐
 │█████ VPWR rail ██████│  power, along the top edge
 │ ░░░░ n-well ░░░░░░░░ │  the region the PMOS transistor sits in
 │   ▓▓▓  ║  ▓▓▓       │  PMOS: diffusion with the gate across it
 │        ║  <- poly    │  one vertical stripe: the GATE of both
 │   ▓▓▓  ║  ▓▓▓       │  NMOS: diffusion with the gate across it
 │█████ VGND rail ██████│  ground, along the bottom edge
 └──────────────────────┘
```

- **The vertical stripe down the middle** is polysilicon (`poly`): the gate. Where it crosses a diffusion region (`diff` or `tap`), there's a transistor. It crosses two, so there are two transistors, and one input drives both of them.
- **The top one sits in the n-well** (`nwell`): that's the PMOS. The bottom one is the NMOS.
- **Small squares** are contacts, connecting diffusion and poly up to the wiring layers.
- **The horizontal bars along the top and bottom** are the power rails, VPWR and VGND.

Input high turns the NMOS on and the PMOS off, pulling the output down to
ground. Input low does the opposite. That's an inverter, and it's the whole
cell.

Use the **Layers** panel on the right: double-click a layer to hide or show
it, which is the fastest way to figure out which shape is which. Leave KLayout
open or close it, whichever you like. You'll see this same cell again inside
your own chip in step 7.

### 5. Estimate F<sub>max</sub>

Go back to your predicted path from part 2. List the gates along it, guess a
delay for each from what you found in the library (use numbers from the
middle of the tables, not the corners), and add them up:

**T<sub>min</sub> = t<sub>pcq</sub> + (sum of gate delays) + t<sub>setup</sub>**

F<sub>max</sub> = 1 / T<sub>min</sub>. A period in nanoseconds gives a
frequency in GHz: 2 ns is 0.5 GHz, or 500 MHz.

This will be rough, and that's fine. You don't know yet exactly which gates
synthesis will pick. The point is to have a number of your own before a tool
gives you one.

### 6. Pick your clock period

Open [constraints.sdc](constraints.sdc) and read it. It tells the timing tools
what "fast enough" means, and steps 5 and 7 both read this exact file.

Replace the `10.0` with a period you can defend, in nanoseconds. Things to
weigh:

- your estimate from part 5
- that it ignores wires completely, and real wires add delay (step 7)
- that the slow corner (`ss`) is roughly twice as slow as typical

If you're unsure, leave it at 10.0 for now. A first pass that's sure to close
is worth more than an aggressive one that doesn't, and step 7 has you tighten
it on purpose.

**Write down your reason.** It's the number you'll be checking your work
against for the rest of the program.

## Check yourself

- You can explain setup, hold, and slack without notes.
- You named a specific start point and end point for the critical path.
- You know what the two axes of a delay table are.
- You have a clock period in `constraints.sdc`, and a reason for it.

<details>
<summary>What did the reference ALU's critical path turn out to be?</summary>

Don't open this until you've committed to your own prediction. Step 5 is
where you find out for real.

In the reference design, the slowest path starts at one of the `a_q` input
register bits and runs through the conditional inversion for SUB, then the
carry chain, then the opcode mux. It ends at one of the flag registers,
**V or Z**. Both are computed _from_ the result, so they finish last. At the
typical corner, ignoring wires, it takes about 1.7 ns, plus about 0.07 ns
of setup time: an F<sub>max</sub> of roughly 560 MHz.

</details>

## Stuck?

| What you see                                              | What's wrong                                                                                         |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `less: $LIB_TT: No such file` or `less` opens nothing     | You're in a terminal outside the container, or an old one. Open a new terminal in VS Code.           |
| Searching `cell ("sky130_fd_sc_hd__inv_1")` finds nothing | Type it exactly, including the quotes and parentheses. Or search a shorter piece: `/inv_1"`.         |
| `klayout: cannot connect to X server`                     | Run `echo $DISPLAY`; it should say `:1`. Open a new terminal.                                        |
| KLayout opens but the window is empty                     | You haven't picked a cell yet. Right-click `sky130_fd_sc_hd__inv_1` > Show As New Top, then press F. |
| Layers show as numbers like `64/20`                       | You opened the GDS without `-nn` and `-l`. Close KLayout and use the full command above.             |
