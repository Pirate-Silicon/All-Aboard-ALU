# Step 6: Floorplan and Placement

**Goal:** See your design become a physical shape: decide how big the chip
is and where its pins go, let the tools place every cell, then look at where
your logic actually landed.

## Watch and read

1. **[The EDA Primer](https://newsletter.semianalysis.com/p/the-eda-primer-from-rtl-to-silicon)**, the Physical Design section: Floorplanning, Power Planning, and Placement.
2. **[LibreLane documentation](https://librelane.readthedocs.io)**. Skim the Getting Started pages. LibreLane is the tool that runs the whole physical flow; you'll drive it here and in step 7.

## Background

### From netlist to rectangle

After synthesis, your ALU is a list of about a hundred cells and the wires
between them. Nothing has a location yet. **Floorplanning** decides the
stage those cells will sit on:

- **The die**: the whole rectangle of silicon.
- **The core**: the area inside the die where cells go. The margin between the two is for the pins and the power ring.
- **Rows**: horizontal strips across the core, each exactly one cell tall (2.72 µm in this library). Cells sit in rows like books on a shelf. You saw in step 4 that every cell is the same height; this is why.
- **Pins**: where each input and output crosses the edge of the die. Where you put them decides how far every signal has to travel.
- **The power grid**: thin metal rails along every row (each cell's VPWR and VGND connect to them by just sitting there), and thicker metal **straps** on higher layers that feed the rails from above.
- **Tap cells**: little cells sprinkled through every row that tie the silicon underneath to power and ground. Without them, the chip can lock up (a failure called _latch-up_).

**Placement** then gives every cell an exact position in a row, trying to put
connected cells near each other so the wires are short.

### Utilization

**Utilization** is the fraction of the core that cells take up. At 100%,
there's no room left: no space for wires to get between cells, and none for
the extra buffers the tools add later to fix timing. Real designs usually sit
around 40–70%.

### LibreLane

LibreLane chains together every tool for steps 6 and 7 (Yosys, OpenSTA,
OpenROAD, KLayout, Magic, Netgen) into one flow, about 80 steps long. You
give it a configuration file, and it runs them in order, saving every step's
output in its own numbered folder so you can look at any stage.

It starts by running Yosys and OpenSTA itself. That's what you did by hand in
step 5, so the first few steps should look familiar.

## Do

### 1. Sketch the floorplan (paper)

Draw the core as a square. Then:

1. **Estimate its size.** Take the cell area from your step 5 `stat` report. If cells should fill 40% of the core, how big does the core need to be? How long is each side?
2. **Place the pins.** Decide which edge of the chip each group of pins goes on: `clk` and `rst`, `a`, `b`, `op`, and the outputs `y`, `n`, `z`, `c`, `v`. There's no single right answer for an ALU this small, but have a reason. (A real ALU sits inside a processor, with the register file feeding it on one side and the results heading off on another.)
3. **Mark the power:** rails along every row, straps crossing them.

<details>
<summary>The size, worked out</summary>

The reference ALU's cells come to about 908 µm². At 40% utilization, the core
needs 908 / 0.40 ≈ 2270 µm², which is a square about 48 µm on a side. That's
about the width of a human hair.

</details>

### 2. Write the pin order file

Create `step6-floorplan/pin_order.cfg`. Each `#` line names an edge (`#N`,
`#S`, `#E`, `#W` for north, south, east, west), and the lines under it list
the pins that go on that edge. `.*` matches every bit of a bus, so `a.*`
means `a[0]` through `a[3]`.

Here's the reference ALU's choice. Use yours, from your sketch:

```
#W
clk
rst
a.*
#N
op.*
#S
b.*
#E
y.*
n
z
c
v
```

### 3. Write the LibreLane configuration

Create `step6-floorplan/config.json`:

```json
{
  "DESIGN_NAME": "alu",
  "VERILOG_FILES": ["dir::../rtl/alu_core.sv", "dir::../rtl/alu.sv"],
  "CLOCK_PORT": "clk",
  "CLOCK_PERIOD": 10,
  "PNR_SDC_FILE": "dir::../step4-timing/constraints.sdc",
  "SIGNOFF_SDC_FILE": "dir::../step4-timing/constraints.sdc",
  "FP_CORE_UTIL": 40,
  "IO_PIN_ORDER_CFG": "dir::pin_order.cfg"
}
```

What each line means:

| Key                                | Meaning                                                                                                                                                                                   |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DESIGN_NAME`                      | The top module's name                                                                                                                                                                     |
| `VERILOG_FILES`                    | Your RTL. `dir::` means "relative to this config file's folder".                                                                                                                          |
| `CLOCK_PORT`                       | Which input is the clock                                                                                                                                                                  |
| `CLOCK_PERIOD`                     | The clock period in nanoseconds. **Make it the same number as in `constraints.sdc`.** LibreLane uses this one to steer synthesis, and the SDC for checking timing, so they have to agree. |
| `PNR_SDC_FILE`, `SIGNOFF_SDC_FILE` | Use your step 4 constraints for place and route, and for the final timing check                                                                                                           |
| `FP_CORE_UTIL`                     | Target utilization, in percent. LibreLane sizes the core to fit.                                                                                                                          |
| `IO_PIN_ORDER_CFG`                 | Your pin order file                                                                                                                                                                       |

JSON is strict: every key in double quotes, a comma between entries, and no
comma after the last one.

### 4. Run the flow, as far as placement

```bash
cd step6-floorplan
librelane --manual-pdk --run-tag place --to OpenROAD.DetailedPlacement config.json
```

- `--manual-pdk` means "use the sky130 that's already installed in this container".
- `--run-tag place` names this run, so its results go in `runs/place/`.
- `--to OpenROAD.DetailedPlacement` stops after placement. Step 7 runs the rest.

It takes about 30 seconds and prints a lot. The last lines should say
**Flow complete**.

Now look at what it made:

```bash
ls runs/place
```

One numbered folder per step: linting, synthesis, floorplan, tap cells, power
grid, pin placement, global placement, detailed placement. Open
`runs/place/06-yosys-synthesis/reports/stat.rpt` in VS Code (the exact
number at the front may differ). It's the same `stat` table you made in step 5. Same cells?

### 5. Look at it

Open the container's desktop in your browser
([setup](../guides/setup.md), section 5), then:

```bash
librelane --manual-pdk --last-run --flow OpenInOpenROAD config.json
```

The **OpenROAD GUI** opens on the desktop with your placed design. Maximize
the window: the layout view is on the right. Then explore:

- **Zoom** with the scroll wheel. Click **Fit** in the toolbar to see everything again.
- **Find the rows.** Cells are lined up in horizontal strips.
- **Find the tap cells.** Small identical cells repeating at regular intervals in every row.
- **Find the power grid.** In the **Display Control** panel on the left, turn layers on and off with their checkboxes. The rails are on `met1`, along every row. The thick straps are on `met4` and `met5`.
- **Find your pins**, around the edges. Are they where your `pin_order.cfg` said?
- **Click any cell.** The **Inspector** panel tells you what it is (an `and4_1`, a `dfxtp_1`, ...) and where it is. Find some flip-flops. Are they near the pins they connect to?

Then find your critical path, physically:

1. Open the **Timing Report** panel (a tab on the right side, or the **Windows** menu).
2. Click **Update**. It lists the slowest paths.
3. Click the top one. The path lights up on the layout, from the flip-flop it starts at, through every gate, to the flip-flop it ends at.

That's the path from your step 5 report, laid out in real space. Is it
compact, or does it wander across the core?

### 6. Change the utilization

Try `FP_CORE_UTIL` at 20 and at 60 (one run each, with different tags so you
can compare):

```bash
librelane --manual-pdk --run-tag util20 --to OpenROAD.DetailedPlacement config.json
```

(Change the number in `config.json` first, each time.) Open each one in the
GUI and compare. What changes about the core size, and the spacing between
cells?

Then push it until it breaks. Try 85. What happens, and at which step?

<details>
<summary>What happens at 85</summary>

The flow stops at global placement with an error:

```
[GPL-0301] Utilization 114.127 % exceeds 100%.
```

You asked for cells to fill 85% of the core, but LibreLane sized the core
using the synthesized cells alone. After it added tap cells and the buffers
that protect the pins, the cells needed more room than the core had.
There's literally nowhere to put them.

65% places fine. 70% places too, but fails in step 7, when the clock tree
adds its buffers and there's no room left for them. Every stage of the
flow adds cells, and the floorplan has to leave room for all of them.

</details>

Put `FP_CORE_UTIL` back to what you want to use for step 7.

## Check yourself

- You can point at a row, a tap cell, a power strap, and a pin in the GUI.
- You can say why utilization can't be 100%.
- You found your critical path on the layout.
- `config.json` has the same clock period as `constraints.sdc`.

## Stuck?

| What you see                                                | What's wrong                                                                                                                                 |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `Error: ... is not valid JSON` or `Expecting ',' delimiter` | A JSON typo: a missing comma, an extra comma after the last entry, or single quotes instead of double.                                       |
| `Unknown variable` or a warning about a variable name       | A misspelled key. Check it against the table above.                                                                                          |
| It tries to download a PDK, or complains about `ciel`       | You left out `--manual-pdk`.                                                                                                                 |
| `[ERROR] ... pin ... not found` in IO placement             | A pin name in `pin_order.cfg` doesn't match your RTL. Buses need `.*`, like `a.*`.                                                           |
| The GUI doesn't appear                                      | Is the desktop open in your browser? Run `echo $DISPLAY`; it should say `:1`.                                                                |
| The GUI opens with an empty layout                          | Click **Fit** in the toolbar. If still empty, `--last-run` may have picked a run that failed: use `--run-tag place` instead of `--last-run`. |
| The Timing Report is empty                                  | Click **Update**.                                                                                                                            |
