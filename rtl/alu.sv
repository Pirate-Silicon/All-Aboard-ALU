//------------------------------------------------------------------------
// alu.sv -- YOU WRITE THIS, in step 2.
//------------------------------------------------------------------------
// The top of the design: alu_core with a bank of registers on each side.
//
//            +-------+      +-----------+      +-------+
//   a,b,op ->| input |----->| alu_core  |----->|output |-> y,n,z,c,v
//            | regs  |      | (no clock)|      | regs  |
//            +-------+      +-----------+      +-------+
//                ^                                 ^
//               clk                               clk
//
// Inputs are captured on one rising edge and the result on the next, so the
// answer appears two rising edges after the inputs are applied. Step 4 is
// about why that register-to-register path is the one that sets how fast
// this can run.
//
// Don't rename anything.

module alu #(
  parameter int WIDTH = 4
) (
  input  logic             clk,
  input  logic             rst,     // synchronous, active high
  input  logic [WIDTH-1:0] a,
  input  logic [WIDTH-1:0] b,
  input  logic [2:0]       op,
  output logic [WIDTH-1:0] y,
  output logic             n,
  output logic             z,
  output logic             c,
  output logic             v
);

  // Stage 1: the input registers.
  logic [WIDTH-1:0] a_q, b_q;
  logic [2:0]       op_q;

  // Worked example: one register bank, with synchronous reset.
  always_ff @(posedge clk) begin
    if (rst) begin
      a_q  <= '0;
      b_q  <= '0;
      op_q <= '0;
    end else begin
      a_q  <= a;
      b_q  <= b;
      op_q <= op;
    end
  end

  // The combinational core, fed from the input registers. Given.
  logic [WIDTH-1:0] y_d;
  logic             n_d, z_d, c_d, v_d;

  alu_core #(.WIDTH(WIDTH)) core (
    .a  (a_q),
    .b  (b_q),
    .op (op_q),
    .y  (y_d),
    .n  (n_d),
    .z  (z_d),
    .c  (c_d),
    .v  (v_d)
  );

  // TODO(step2): Stage 2, the output registers.
  //
  // One always_ff block, the same shape as the one above: on reset every
  // output goes to 0; otherwise y gets y_d, n gets n_d, and so on.
  //
  // Every register gets a value in the reset branch. Every single one. A
  // register you forget is X in simulation and random garbage in silicon.

endmodule
