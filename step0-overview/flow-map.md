# The Flow Map

Fill in the two blank columns. One short phrase per cell is enough. The first
row is done for you.

| # | Stage | Goes in | Comes out |
|---|---|---|---|
| 1 | Spec | an idea for what the chip should do | a document saying exactly what it does |
| 2 | RTL | | |
| 3 | Verification | | |
| 4 | Synthesis | | |
| 5 | Timing analysis | | |
| 6 | Floorplan | | |
| 7 | Placement | | |
| 8 | Clock tree | | |
| 9 | Routing | | |
| 10 | Signoff | | |
| 11 | Tapeout | | |

Then mark, next to each row, which of the four jobs does that stage:
architect, RTL designer, verification engineer, or physical design engineer.

<details>
<summary>Answers (try it first)</summary>

| # | Stage | Goes in | Comes out | Who |
|---|---|---|---|---|
| 1 | Spec | an idea | a document (and often a software model) saying exactly what it does | architect |
| 2 | RTL | the spec | SystemVerilog code describing the hardware | RTL designer |
| 3 | Verification | the RTL and the spec | evidence the RTL matches the spec: passing tests and coverage | verification |
| 4 | Synthesis | RTL plus a standard cell library | a gate-level netlist: a list of real gates and the wires between them | RTL designer or PD (varies by company) |
| 5 | Timing analysis | a netlist plus timing constraints (the clock speed) | reports saying whether every signal arrives in time, and by how much | PD |
| 6 | Floorplan | the netlist | the chip's outline, where the pins go, and the power grid | PD |
| 7 | Placement | the floorplan and netlist | every gate given an exact position | PD |
| 8 | Clock tree | the placed design | a network of buffers delivering the clock to every flip-flop at nearly the same moment | PD |
| 9 | Routing | the placed design with its clock tree | every wire drawn, on real metal layers | PD |
| 10 | Signoff | the routed layout | proof it obeys the manufacturing rules (DRC), matches the netlist (LVS), and meets timing | PD |
| 11 | Tapeout | the signed-off GDS file | masks, then wafers, then chips | the whole team, then the fab |

</details>
