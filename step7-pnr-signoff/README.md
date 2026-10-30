# Step 7: Place, Route, Signoff, GDS

**Goal:** Finish the flow. Build the clock tree, draw every wire, check that
the result could actually be manufactured and still meets timing, and end up
with a GDS: the file a factory makes chips from.

## Watch and read

1. **[The EDA Primer](https://newsletter.semianalysis.com/p/the-eda-primer-from-rtl-to-silicon)**, the rest of the Physical Design section: Clock Tree Synthesis, Routing, and the verification and signoff parts.

## Background

Picking up where step 6 stopped, after placement, here's what's left:

| Stage                          | What happens                                                                                                                             |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Clock tree synthesis (CTS)** | Until now the clock was assumed to arrive at every flip-flop at the same instant. Now a tree of buffers is built so that it nearly does. |
| **Global routing**             | Plans roughly which areas and metal layers each wire will use                                                                            |
| **Detailed routing**           | Draws every wire exactly, on real metal layers, obeying every spacing rule                                                               |
| **Fill**                       | Packs the empty spaces in each row with filler cells, so the layers are evenly dense for manufacturing                                   |
| **RC extraction**              | Measures every wire's resistance and capacitance, from its actual shape                                                                  |
| **Timing (STA)**               | Re-checks timing with real wires and the real clock tree, at many corners                                                                |
| **Stream-out**                 | Writes the GDS                                                                                                                           |
| **DRC**                        | Design rule check: does every shape obey the foundry's manufacturing rules?                                                              |
| **LVS**                        | Layout vs. schematic: extracts the circuit back out of the drawn shapes, and checks it matches the netlist                               |
| **Antenna check**              | Could any long wire collect enough charge during manufacturing to damage a transistor?                                                   |

The last four are **signoff**: the checks that decide whether a design is
allowed to be sent to the factory.

## Do

### 1. Set up

```bash
cd step7-pnr-signoff
cp ../step6-floorplan/config.json ../step6-floorplan/pin_order.cfg .
```

Check that `config.json`'s `CLOCK_PERIOD` matches the period in
`step4-timing/constraints.sdc`.

### 2. Run the whole flow

```bash
librelane --manual-pdk --run-tag full config.json
```

About three minutes. At the very end:

```
* Antenna
Passed ✅

* LVS
Passed ✅

* DRC
Passed ✅

... INFO     Flow complete.
```

On the way it prints hundreds of `WARNING` lines. They're the same library
warnings you saw in step 6, printed again by every step that checks timing,
once for each of the nine corners you'll meet in part 4. A warning doesn't
stop the flow. An `ERROR` does.

If any of the three says Failed, or the flow stops with an `ERROR`, read the
**Stuck?** table below before changing anything.

### 3. Walk through what it did

```bash
ls runs/full
```

About 76 numbered folders, one per step, in order. Find the ones for each
stage in the table above (`35-openroad-cts`, `44-openroad-detailedrouting`,
`54-openroad-rcx`, `55-openroad-stapostpnr`, `64-magic-drc`,
`70-netgen-lvs`, ...). Every step's inputs, outputs, and log are in its
folder. If anything ever goes wrong, this is where you look.

The finished results are collected in `runs/full/final/`:

| Folder           | What it is                                                                           |
| ---------------- | ------------------------------------------------------------------------------------ |
| `gds/`           | **The GDS.** The layout, as shapes on layers. This is what a factory builds from.    |
| `def/`           | The same physical design as readable text: every cell's position, every wire's route |
| `nl/`            | The final netlist, now including the clock tree and buffers that were added          |
| `spef/`          | The extracted resistance and capacitance of every wire                               |
| `metrics.json`   | Every number the flow measured, in one file                                          |
| `render/alu.png` | A picture of the layout. Click it to open it right in VS Code.                       |

### 4. Read the timing

Open `runs/full/55-openroad-stapostpnr/summary.rpt`. (If the number at the
front is different, use whichever folder ends in `stapostpnr`.)

It's a table with one row per **corner**, and there are nine. Each name has
three parts, like `max_ss_100C_1v60`:

- `nom`, `min`, or `max`: the wire extraction corner (typical, least, or most resistance and capacitance)
- `tt`, `ss`, or `ff`: the transistor corner (typical, slow, or fast)
- the temperature and voltage that go with it

The columns that matter most are **Setup Worst Slack** and **Hold Worst
Slack**. A chip has to work at _every_ corner, so the overall result is the
worst row.

Now fill in this table:

|                     | Step 4 (your estimate) | Step 5 (OpenSTA, no wires) | Post-route, `nom_tt` | Post-route, worst corner |
| ------------------- | ---------------------- | -------------------------- | -------------------- | ------------------------ |
| Critical path delay |                        |                            |                      |                          |
| Setup slack         |                        |                            |                      |                          |

For the critical path itself, open `nom_tt_025C_1v80/max.rpt` in the same
folder. Compare it with your step 5 report. Two new things appear:

- **`clkbuf_...` cells at the top.** That's the clock tree. The clock now takes real time to reach each flip-flop.
- **Wire delay.** Every gate's delay is a little longer, because now it's driving real wires.

Which corner was worst for setup? Which was worst for hold? Why are they
different corners?

<details>
<summary>The reference ALU's numbers</summary>

At a 10 ns clock: the worst setup slack is **5.81 ns**, at the slow corner
(`max_ss_100C_1v60`), so the critical path takes about 4.2 ns there. At the
typical corner, slack is 7.97 ns, a path of about 2.0 ns: a little slower
than step 5's 1.7 ns, because of wires and the clock tree. The worst hold
slack is 0.42 ns, at a fast corner.

Setup is worst on **slow** silicon, because that's when data arrives latest.
Hold is worst on **fast** silicon, because that's when data arrives _too
early_. That's why one corner can't check both.

</details>

### 5. Look at your chip

Open the desktop in your browser, then:

```bash
librelane --manual-pdk --last-run --flow OpenInKLayout config.json
```

KLayout opens your GDS, with sky130's layers already set up. Click **Yes** if
the Tip about hierarchy appears.

- Zoom out (press **F**) and find your pins on the edges, where `pin_order.cfg` put them.
- Use the **Layers** panel to switch off everything but one metal layer at a time. Which layers carry most of the routing? Where's the power?
- Zoom in on a row until individual cells are visible, then keep going. Find an inverter: in the **Cells** panel, cells named `sky130_fd_sc_hd__inv_...` are the ones placed in your design. It's the same cell you looked at in step 4, now part of your chip.

Everything you built in this program is somewhere in this file, as
rectangles on layers. Nothing in it knows or cares that it was ever Verilog.

### 6. (Optional) A second opinion from Magic

LibreLane ran two different DRC tools, KLayout and **Magic**. Magic is one of
the oldest open-source layout tools there is, and still the reference for
sky130. To see it:

```bash
librelane --manual-pdk --last-run --flow OpenInMagic config.json
```

Magic opens two windows: the layout, and a console. The bar along the top of
the layout window shows **`DRC=0`**: zero rule violations. In the console,
type `drc count` and press Enter to ask it directly.

### 7. Break it on purpose

You now know the flow works. Learn what failure looks like, on a design you
understand, because you won't always get a pass.

Make a copy so you don't disturb your good run:

```bash
cd ..
cp -r step7-pnr-signoff experiments
cd experiments
rm -rf runs
```

**A. Tighten the clock.** Change the period to 3.5 ns in _both_ places:
`CLOCK_PERIOD` in `config.json`, and a copy of the SDC (copy
`../step4-timing/constraints.sdc` into this folder, edit it, and point
`PNR_SDC_FILE` and `SIGNOFF_SDC_FILE` at `dir::constraints.sdc`). Run the
flow. What happens? Open the new `summary.rpt`: which corners fail, and by
how much?

Then find the fastest clock that passes everywhere, by halving the gap: try
4.5, then whatever's halfway between your last pass and your last fail.

<details>
<summary>What happens at 3.5 ns</summary>

The flow finishes routing, then stops at the end with:

```
ERROR    Setup violations found in the following corners: ...
```

The typical corner still passes, with 1.66 ns to spare. But all three slow
corners fail, by up to 0.19 ns. **One failing corner is a failing chip**:
real silicon includes the slow parts, and the hot days.

At 4.5 ns, every corner passes, with 0.31 ns of setup slack at the worst one.
The real limit is in between.

</details>

**B. Crowd the core.** Put the clock back, then raise `FP_CORE_UTIL` until
the flow fails. Where does it break, and at which step?

**C. Fix it.** For a design that doesn't meet timing, there are four kinds of
fix:

| Fix                                       | Costs you                                   | Where                                                                                 |
| ----------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------- |
| Relax the clock period                    | speed                                       | `constraints.sdc` and `CLOCK_PERIOD`                                                  |
| Lower the utilization                     | area                                        | `FP_CORE_UTIL`                                                                        |
| Bigger, faster cells on the critical path | power and area                              | the tools do some of this already. Look for `_2` and `_4` cells in the final netlist. |
| Pipeline: add registers to split the path | a clock cycle of latency, and a spec change | the RTL, back to step 2                                                               |

For this ALU, which would you choose to reach 4 ns, and why? Write a short
answer with a number in it. "Option 4, probably faster" isn't an answer;
"option 4: the carry chain is about half the path, so splitting it there
should get under 3 ns, at the cost of one more cycle of latency" is.

### 8. Save the commands

Create `step7-pnr-signoff/run`:

```bash
#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
librelane --manual-pdk --run-tag full --overwrite config.json
```

`--overwrite` replaces the previous run with the same tag. `chmod +x run`,
then `./run`.

## Check yourself

- Your run says Passed for antenna, LVS, and DRC.
- `runs/full/final/gds/alu.gds` exists, and you've looked at it.
- You filled in the timing table, and can say what changed between each column.
- You can say why setup and hold are worst at different corners.
- You've seen at least one failing run, and know where in the run folder to look to find out why.

## Stuck?

| What you see                                                            | What's wrong                                                                                                                                    |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `Setup violations found`                                                | Your clock period is too short for the slow corner. See part 7A. Lengthen it in both places.                                                    |
| `Hold violations found`                                                 | Rare for this design. Ask.                                                                                                                      |
| `[GPL-0301] Utilization ... exceeds 100%`                               | `FP_CORE_UTIL` is too high. Lower it.                                                                                                           |
| `[DPL-0036] Detailed placement failed`                                  | Also too high, but discovered later: the cells fit, but not once the clock tree buffers are added. Lower it.                                    |
| DRC or LVS says Failed                                                  | Don't change anything yet. Look in the `NN-magic-drc/reports/` or `NN-netgen-lvs/reports/` folder of your run, and ask.                         |
| `Using existing run at ...`, and the step numbers keep climbing past 80 | You reused a `--run-tag`, so LibreLane added onto the old run instead of starting fresh. Use a new tag, or add `--overwrite`.                   |
| `--last-run` opens the wrong run                                        | It opens the most recent one, even if it failed. Use `--run-tag full` instead to pick one by name.                                              |
| Everything is slow                                                      | On Windows, a repo on your own drive (rather than in a container volume) makes this step several times slower. See [setup](../guides/setup.md). |

## Go further

- **Every number, at once.** `runs/full/final/metrics.json` has hundreds of measurements. Find the total wire length, the number of clock buffers, and the total power estimate.
- **Then and now.** The 74181 from step 1, a 4-bit ALU on its own chip in 1970, had about 75 logic gates and was roughly a tenth of an inch across. Count the logic cells in your final netlist (`runs/full/final/nl/alu.nl.v`; leave out the fill, tap, and decap cells). How do the two compare, and how big is your ALU next to it?
