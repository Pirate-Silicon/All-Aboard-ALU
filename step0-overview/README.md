# Step 0: The Whole Picture

**Goal:** See the whole path from an idea to a chip layout before you zoom in
on any one piece of it.

## Watch and read

Do these in order. The first is the gentle on-ramp. The second is little denser.

1. **[Designing Silicon From Scratch](https://youtu.be/q6ytRHaTEXI)** (video). Watch this first.
2. **[The EDA Primer: From RTL to Silicon](https://newsletter.semianalysis.com/p/the-eda-primer-from-rtl-to-silicon)**, SemiAnalysis. Read at least through the Physical Design section. It's written for industry people, so skim anything about business or market share, and don't worry if some of it goes over your head. You'll come back to it in steps 4, 6, and 7, and it'll make more sense.
3. **[Harris & Harris, video 1.0: Introduction](https://youtu.be/958A8CAXWn0)**. This is the textbook this repo leans on
4. **Extra:** [Branch Education](https://www.youtube.com/@BranchEducation) has a long, nicely animated video called _How are Microchips Made?_. It covers what happens at the fab after you hand over your design

## Keep this open

[chipverify.com](https://chipverify.com) is the reference to keep in a browser
tab: SystemVerilog syntax, testbench patterns, verification concepts. When
something in this program mentions a concept and you want more, look there
first

## Background

### What is a chip, though?

A chip is a flat piece of silicon with transistors etched on it (billions, on a
modern one) wired together in layers of metal. A transistor is a tiny switch.
Wire a few switches together and you get a logic gate (AND, OR, NOT). Wire
gates together and you can add numbers, remember values, and eventually run
programs.

Nobody draws billions of transistors by hand. Designers describe what they
want in a programming-like language, and a chain of software tools turns that
description, step by step, into the exact shapes that get printed on silicon.
That chain is called the **design flow**, and the software is called **EDA**
(electronic design automation).

### The chip design tl;dr

You decide what the chip should do (**spec**). You describe the hardware
in a hardware description language (**RTL**). You prove the description does
what the spec says (**verification**). A tool turns your description into
real logic gates (**synthesis**) and checks they're fast enough (**timing**).
Another tool decides where every gate goes on the silicon (**floorplan,
placement**) and draws every wire between them (**routing**). Final checks
confirm it can actually be manufactured (**signoff**). The output is a
**GDS** file: a drawing of every shape on every layer. That file goes to the
factory (**tapeout!**).

### Where each stage happens in this program

| Stage        | What it does                                           | Our tool (free)                 | Industry tool (expensive)               | Step    |
| ------------ | ------------------------------------------------------ | ------------------------------- | --------------------------------------- | ------- |
| Spec         | Says exactly what the design must do                   | Markdown, plus a Python model   | Documents, plus models in C++ or Python | 1       |
| RTL          | Describes the hardware in code                         | SystemVerilog in VS Code        | SystemVerilog                           | 2       |
| Verification | Proves the RTL matches the spec                        | cocotb + Icarus Verilog         | UVM + Xcelium, VCS, Questa              | 3       |
| Timing       | Checks signals arrive before the clock ticks           | OpenSTA                         | Tempus, PrimeTime                       | 4, 5, 7 |
| Synthesis    | Turns RTL into real gates from a library               | Yosys                           | Genus, Design Compiler                  | 5       |
| Floorplan    | Decides chip size, pin locations, power grid           | OpenROAD (via LibreLane)        | Innovus, Fusion Compiler                | 6       |
| Placement    | Puts every gate somewhere on the chip                  | OpenROAD                        | Innovus, Fusion Compiler                | 6       |
| Clock tree   | Delivers the clock to every flip-flop at the same time | OpenROAD                        | Innovus, Fusion Compiler                | 7       |
| Routing      | Draws every wire                                       | OpenROAD                        | Innovus, Fusion Compiler                | 7       |
| Signoff      | Checks the layout can be built and still works         | Magic, KLayout, Netgen, OpenSTA | Calibre, Tempus, PrimeTime              | 7       |

### Who does this for a living

Each stage is somebody's job. The four big ones:

- **Architects** decide what the chip should do and write the spec.
- **RTL designers** write the hardware description.
- **Verification (DV) engineers** try to break it. At most chip companies there are more DV engineers than designers.
- **Physical design (PD) engineers** take the gates and make a manufacturable layout.

You're about to do a small version of all four jobs.

### What you're building

An **ALU** (arithmetic logic unit), the part of a processor that does the
math. Ours is 4 bits wide and does 8 operations. It's tiny on purpose: small
enough to understand completely, test completely, and carry all the way to a
layout. Every processor you have ever used has ALUs in it, and they work on
the same ideas.

## Do

1. Open [flow-map.md](flow-map.md) and fill in the blank cells: for each stage, what goes in and what comes out. The background above and the primer have everything you need.
2. Move on to step 1, where you'll learn more about the ALU and what it does.

## Concept check

<details>
<summary>Why does a late mistake cost so much?</summary>

Because every stage builds on the one before it. A spec mistake found during
verification means rewriting RTL and re-verifying. Found after the chip is
made, it means new masks: the primer puts a full mask set at a modern node in
the tens of millions of dollars, plus months of waiting for a new run through
the fab. Software can ship a patch. Hardware mostly can't.

</details>

###

The filled-in flow map is at the bottom of [flow-map.md](flow-map.md), hidden
until you click it.

## Extras

- [Tiny Tapeout](https://tinytapeout.com) is a project that puts many small designs, made by hobbyists and students, onto one shared chip. It's the cheapest way to get a design like this one actually manufactured, and the reason this kind of program can end in real silicon.
- [Harris & Harris, videos 1.9 and 1.10](https://youtu.be/ljXd75_yQ0Y) cover transistors and how gates are built from them. You'll see one of those gates up close in step 4.
