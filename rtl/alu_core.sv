//------------------------------------------------------------------------
// alu_core.sv -- YOU WRITE THIS, in step 2.
//------------------------------------------------------------------------
// The combinational heart of the ALU: no clock, no registers. Inputs go in,
// outputs come out after some gate delay. This is a hardware version of the
// alu() function in model/alu_model.py.
//
// It's in three parts, the same shape as the ALU in Harris & Harris
// (video 5.7):
//   1. compute the arithmetic results
//   2. pick which result goes to y, based on the opcode
//   3. compute the flags
// In hardware all three happen at once, all the time. The order here is
// just for reading.
//
// Don't rename anything. The testbench and every later step find these
// ports by name.

module alu_core #(
  parameter int WIDTH = 4
) (
  input  logic [WIDTH-1:0] a,
  input  logic [WIDTH-1:0] b,
  input  logic [2:0]       op,
  output logic [WIDTH-1:0] y,
  output logic             n,
  output logic             z,
  output logic             c,
  output logic             v
);

  // Given: names for the opcodes, so the code reads like the spec.
  localparam logic [2:0] OP_ADD = 3'b000;
  localparam logic [2:0] OP_SUB = 3'b001;
  localparam logic [2:0] OP_AND = 3'b010;
  localparam logic [2:0] OP_OR  = 3'b011;
  localparam logic [2:0] OP_XOR = 3'b100;
  localparam logic [2:0] OP_NOT = 3'b101;
  localparam logic [2:0] OP_SHL = 3'b110;
  localparam logic [2:0] OP_SHR = 3'b111;

  // A (WIDTH+1)-bit 1, for the "+ 1" in a + ~b + 1.
  localparam logic [WIDTH:0] ONE = 1;

  //----------------------------------------------------------------------
  // 1. The arithmetic. Each is one bit wider than the inputs, so the carry
  //    out has somewhere to go: sum[WIDTH] is the carry, sum[WIDTH-1:0] is
  //    the 4-bit answer.
  //----------------------------------------------------------------------
  logic [WIDTH:0] sum;    // a + b
  logic [WIDTH:0] diff;   // a - b, computed as a + ~b + 1

  // Worked example. {1'b0, a} glues a 0 onto the front of a, widening it to
  // 5 bits before the add.
  assign sum = {1'b0, a} + {1'b0, b};

  // TODO(step2): diff. Same shape as sum, plus ONE, with ~b instead of b.
  // Write the ~b INSIDE the braces, {1'b0, ~b}. The step 2 README explains
  // what goes wrong if you don't. It's a real bug that real chips ship with.
  assign diff = '0;

  //----------------------------------------------------------------------
  // 2. Pick the result for this opcode.
  //----------------------------------------------------------------------
  always_comb begin
    // Given: defaults first, so y and c get a value on every path through
    // this block. If some path never assigns an output, the hardware has to
    // remember its old value, and synthesis builds a latch you didn't ask
    // for.
    y = '0;
    c = 1'b0;

    case (op)
      // Worked example. {c, y} glues c and y into one 5-bit target, so the
      // carry bit of sum lands in c and the 4-bit answer lands in y.
      OP_ADD:  {c, y} = sum;

      // TODO(step2): SUB, AND, OR, XOR, NOT, SHL, SHR. One line each.
      // SUB looks like ADD. The rest only set y, like:
      //   OP_AND:  y = ...;

      default: y = '0;
    endcase
  end

  //----------------------------------------------------------------------
  // 3. The flags. These are `assign`s outside the always_comb, because
  //    they need single bits like a[3] (written a[WIDTH-1]), and some
  //    simulators handle those badly inside always_comb.
  //----------------------------------------------------------------------

  // TODO(step2): n and z, from y, for every operation.
  assign n = 1'b0;
  assign z = 1'b0;

  // Overflow. Read `x ? p : q` as "if x then p else q". The chain checks the
  // opcode and uses the matching rule, and anything else gets 0. The ADD rule
  // is given: both inputs have the same sign, and the result's sign differs.
  assign v = (op == OP_ADD) ? (a[WIDTH-1] == b[WIDTH-1]) && (sum[WIDTH-1] != a[WIDTH-1])
           // TODO(step2): add SUB's rule here, as another line of the form
           //   : (op == OP_SUB) ? (...)
           // The rule is in SPEC.md, and it's built from diff, not sum.
           : 1'b0;

endmodule
