# tb/Makefile - given. Run everything from inside tb/.
#
#   make smoke              step 2: five quick checks on your ALU
#   make test               step 3: the full testbench on your ALU
#   make test DUT=buggy     step 3: the full testbench on the vendor ALU
#   make test GATES=1       step 5: the full testbench on your synthesized gates
#   make waves              open the waveform in Surfer (add DUT=buggy or GATES=1 to match)
#   make clean              delete everything the simulator wrote
#
# Add WAVES=1 to smoke or test to record a waveform for `make waves`.
# Add RANDOM_SEED=1234 to test to replay an earlier random run exactly.

SIM           ?= icarus
TOPLEVEL_LANG ?= verilog
COCOTB_TOPLEVEL = alu

RTL := $(abspath ../rtl)

# Each design gets its own build folder. Sharing one would let the simulator
# reuse a stale build and quietly test the wrong design.
ifeq ($(GATES),1)
  # The step 5 netlist, plus a Verilog model of every sky130 standard cell so
  # the simulator knows what an sky130_fd_sc_hd__nand2_1 does.
  CELLS := $(PDK_ROOT)/$(PDK)/libs.ref/sky130_fd_sc_hd/verilog
  VERILOG_SOURCES = $(abspath ../step5-synthesis/alu_synth.v) \
                    $(CELLS)/primitives.v $(CELLS)/sky130_fd_sc_hd.v
  COMPILE_ARGS   += -DFUNCTIONAL -DUNIT_DELAY=\#1
  SIM_BUILD      := sim_build/gates
else ifeq ($(DUT),buggy)
  VERILOG_SOURCES = $(RTL)/alu_buggy.sv
  SIM_BUILD      := sim_build/buggy
else
  VERILOG_SOURCES = $(RTL)/alu_core.sv $(RTL)/alu.sv
  SIM_BUILD      := sim_build/rtl
endif

COMPILE_ARGS += -g2012

# Lets the testbench `import alu_model` from ../model.
export PYTHONPATH := $(abspath ../model):$(PYTHONPATH)

.DEFAULT_GOAL := help

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: help smoke test waves

help:
	@sed -n '3,12p' Makefile | sed 's/^# \{0,1\}//'

smoke:
	$(MAKE) sim COCOTB_TEST_MODULES=test_smoke

test:
	$(MAKE) sim COCOTB_TEST_MODULES=test_alu

waves:
	surfer $(SIM_BUILD)/alu.fst &
