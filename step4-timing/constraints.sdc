# constraints.sdc -- you edit ONE number in this file, in step 4.
#
# SDC (Synopsys Design Constraints) is how you tell timing tools what "fast
# enough" means. Every timing tool reads it, open source or not. Step 5's
# OpenSTA run and step 7's LibreLane flow both read this exact file, so
# they're all judged against the same target.

# TODO(step4): replace 10.0 with the clock period you argued for, in
# nanoseconds. 10.0 ns is 100 MHz, a deliberately easy placeholder.
create_clock -name clk -period 10.0 [get_ports clk]

# Pretend the outside world drives our inputs right at the clock edge, and
# reads our outputs right at the next one. In a real chip, the blocks on
# either side negotiate how much of the clock period each one gets. Ours has
# registers right at its inputs and outputs, so the path that matters is the
# one between the two register banks, and that's the one we want to see.
set_input_delay  0 -clock clk [delete_from_list [all_inputs] [get_ports clk]]
set_output_delay 0 -clock clk [all_outputs]

# A realistic load on each output pin (picofarads), so output delays aren't
# computed as if nothing were connected.
set_load 0.01 [all_outputs]
