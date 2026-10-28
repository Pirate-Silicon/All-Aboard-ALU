# tb_sv/Makefile - given. The optional SystemVerilog testbench.
#
#   make                  corner cases + 500 random, on your ALU
#   make EXHAUSTIVE=1     corner cases + every possible input
#   make DUT=buggy        on the vendor ALU (combine with EXHAUSTIVE=1 too)
#   make SEED=7           a different random run
#   make clean
#
# Verilator compiles the testbench and the design together into one
# program, then runs it.

SEED ?= 1

ifeq ($(DUT),buggy)
  SRCS := ../rtl/alu_buggy.sv
  NAME := buggy
else
  SRCS := ../rtl/alu_core.sv ../rtl/alu.sv
  NAME := rtl
endif

ifeq ($(EXHAUSTIVE),1)
  DEFS := -DEXHAUSTIVE
  NAME := $(NAME)_exhaustive
endif

# Verilator writes its generated C++ here. It's in /tmp, inside the container,
# because writing hundreds of small files is much faster there than in a
# folder shared from your computer.
OBJ := /tmp/aaalu-tb_sv/$(NAME)

.PHONY: run clean
run:
	mkdir -p $(OBJ)
	verilator --binary --timing -j 0 -Wno-fatal --top-module alu_tb \
	    -Mdir $(OBJ) $(DEFS) alu_tb.sv $(SRCS)
	$(OBJ)/Valu_tb +verilator+seed+$(SEED)

clean:
	rm -rf /tmp/aaalu-tb_sv
