# All-Aboard-ALU

Pirate Silicon's onboarding project. You design a small piece of a processor,
a 4-bit arithmetic logic unit (ALU), and take it through every stage a real chip goes through:
from a written spec to a GDS file, the layout a factory builds chips from.

Every tool is free and open source. The manufacturing process is sky130,
a real 130 nm process whose design kit is public.

You don't need to know anything yet. No hardware experience, no Linux, no
git. If you can follow instructions and you're curious how a computer
actually works, you're in good shape. Everything else is taught along the way, as you need it.

## How it works

There are nine steps. Each is a folder with a `README.md` that walks you
through it. Do them in order, at your own pace. Each step ends with concept check questions,
with the answers hidden until you click.

| Step                                           | What you do                                                   | Tools                        |
| ---------------------------------------------- | ------------------------------------------------------------- | ---------------------------- |
| [0: The whole picture](step0-overview/)        | See the full path from idea to chip                           | none                         |
| [1: Spec and model](step1-spec/)               | Learn exactly what the ALU does, and write it in Python       | Python                       |
| [2: RTL](step2-rtl/)                           | Write the ALU in SystemVerilog and simulate it                | Icarus, Verilator, Surfer    |
| [3: Verification](step3-verification/)         | Build a testbench that proves it works, and catch a buggy one | cocotb                       |
| [4: Timing](step4-timing/)                     | Predict how fast it can run, by hand                          | sky130 cell library, KLayout |
| [5: Synthesis](step5-synthesis/)               | Turn your code into real gates and check the prediction       | Yosys, OpenSTA               |
| [6: Floorplan](step6-floorplan/)               | Decide the chip's shape, and place every gate                 | LibreLane, OpenROAD          |
| [7: Place, route, signoff](step7-pnr-signoff/) | Draw every wire, check it can be built, get a GDS             | LibreLane, KLayout, Magic    |
| [8: Wrap-up](step8-wrapup/)                    | Recap of your work                                            | none                         |

Steps that need tools alternate with ones that are mostly reading and
thinking. You learn the idea, then you do it.

## Start here

1. [guides/git-basics.md](guides/git-basics.md): make a GitHub account and fork this repo, so you have your own copy to work with
2. [step0-overview/](step0-overview/): no setup needed. Start reading.
3. Step 1 sends you to [guides/setup.md](guides/setup.md) to install the tools. It's one big download with all the software you'll need

## Where things are

```
model/
  alu_model.py        TODO in step 1: the ALU in Python
  check_model.py      given: checks your model against 40 worked examples
rtl/
  alu_core.sv         TODO in step 2: the ALU's logic
  alu.sv              TODO in step 2: the registers around it
  alu_buggy.sv        given: somebody else's ALU, with bugs, for step 3
tb/
  Makefile            given: automated setup
  test_smoke.py       given: the step 2 test
  test_alu.py         TODO in step 3: the real testbench
tb_sv/
  alu_tb.sv           optional bonus in step 3: the same testbench but in SystemVerilog
guides/               setup, Linux, git, waveforms
step0-overview/ ... step8-wrapup/
                      one folder per step: its README, plus any files that step makes
```

Every step works inside its own folder and reads earlier steps' outputs by
relative path. Step 7 reads `../rtl/`, for example

## Each tool step works the same way

1. Run the tool by hand, one command at a time, and look at what happens.
2. Once it works, save those commands in a `run` script in that step's folder.
3. From then on, `./run` will run the same commands again.

#

This program is heavily adapted from Longhorn Silicon's
[pe-apprentice](https://github.com/LonghornSilicon/pe-apprentice), which in
turn owes a lot to Cornell's ECE 6745 and Berkeley's EECS 151. It leans on
Harris & Harris, _Digital Design and Computer Architecture: RISC-V Edition_,
and its [free lecture videos](https://pages.hmc.edu/harris/ddca/ddcarv/ddcarv_videos.html).
The tools come packaged by [IIC-OSIC-TOOLS](https://github.com/iic-jku/IIC-OSIC-TOOLS).
