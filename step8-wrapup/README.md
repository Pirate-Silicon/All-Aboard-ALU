# Step 8: Wrap-Up and What's Next

**Goal:** Look back at the whole path you just walked, and pick where to go
from here.

## You did the whole thing

Look at what you made, in order:

1. a **spec** and a Python model of it
2. **RTL** that simulates
3. a **testbench** that caught real bugs in somebody else's design
4. a **timing prediction**, made by hand
5. a **gate-level netlist** in real sky130 cells, simulated and timed
6. a **floorplan**
7. a routed, signed-off **GDS**

That's every stage from step 0's flow map. The ALU is tiny, but no stage was
skipped or faked. Chips with billions of transistors go through the same
stages, with the same kinds of tools, run by teams of people who each own
one of those boxes.

## Look back

Worth a few minutes, written down or just thought through:

- **One prediction you got wrong**, and why. Your step 4 critical path? Your Fmax estimate? Your step 6 guess about where the cells would land?
- **One number you can defend completely.** Where it came from: which file, which tool, which corner, and why it's that value and not another.
- **The bug that surprised you most**, in your own code or in the vendor's.
- **Which stage you'd want to do as a job**, if you had to pick one. That's worth knowing about yourself.

## Where to go next

### Make the ALU better

- **Make it 8 bits.** Every file takes a `WIDTH` parameter. Change it, re-run every step's `run` script, and see what breaks. Did your scripts really capture everything? How do area and timing scale?
- **A faster adder.** Replace the ripple carry with a carry-lookahead or prefix adder (Harris & Harris videos [5.4](https://youtu.be/aD-qA-jEKV0) and [5.5](https://youtu.be/Ue5CjG31E-c)). Measure the difference in steps 5 and 7.
- **Add SLT** (set if less than), the operation RISC-V needs for `slt` instructions. Update the spec first, then the model, then the RTL, then the testbench. That order is the point.

### Build around it

The ALU is the heart of a processor. Harris & Harris chapter 7 builds a
complete RISC-V processor around one, in SystemVerilog:

- [7.2 Single-Cycle Processor: Datapath](https://youtu.be/AoBkibslRBM), and the videos after it
- [7.6b Single-Cycle Processor: SystemVerilog](https://youtu.be/a8yewzP-kJc)

A single-cycle RISC-V core is a very reachable next project, and everything
you learned here (spec, model, RTL, testbench, flow) carries over directly.

### Get a real chip

[Tiny Tapeout](https://tinytapeout.com) puts small designs from many people
onto one shared chip and mails them back to you. A 4-bit ALU fits easily. It
uses the same kind of open-source flow you just ran. When we plan our first tapeout, we'll likely do it with them.

### Go deeper on one stage

- **Verification:** real UVM. [chipverify's UVM tutorial](https://www.chipverify.com/uvm/uvm-tutorial), then try a UVM testbench on [EDA Playground](https://www.edaplayground.com), which has free commercial simulators. Or stay in Python with [pyuvm](https://github.com/pyuvm/pyuvm).
- **How the tools work inside:** [VLSI CAD Part I: Logic](https://www.coursera.org/learn/vlsi-cad-logic), Rob Rutenbar's course on the algorithms inside synthesis, and its sequel on placement and routing. Free to audit.
- **Physical design:** the [LibreLane docs](https://librelane.readthedocs.io) and the [OpenROAD docs](https://openroad.readthedocs.io). Every flow variable you didn't touch is a knob a PD engineer turns.
