//------------------------------------------------------------------------
// alu_buggy.sv -- given. A "vendor drop" for step 3.
//------------------------------------------------------------------------
// An ALU somebody else wrote against the same spec and the same ports as
// yours. The vendor says it works. It does not.
//
// Read this header, not the code below it. The point of step 3 is that your
// testbench finds the problems, not your eyes. Run it with:
//
//     make test DUT=buggy
//
// Its top module is also called `alu`, so the same testbench drives it
// unchanged. Only one of rtl/alu.sv or this file is compiled at a time.
//------------------------------------------------------------------------

/* verilator lint_off DECLFILENAME */
module alu #(
  parameter int WIDTH = 4
) (
  input  logic             clk,
  input  logic             rst,
  input  logic [WIDTH-1:0] a,
  input  logic [WIDTH-1:0] b,
  input  logic [2:0]       op,
  output logic [WIDTH-1:0] y,
  output logic             n,
  output logic             z,
  output logic             c,
  output logic             v
);

  logic [WIDTH-1:0] a_q, b_q, y_d;
  logic [2:0]       op_q;
  logic             n_d, z_d, c_d, v_d;

  always_ff @(posedge clk) begin
    if (rst) begin
      a_q <= '0;  b_q <= '0;  op_q <= '0;
      y   <= '0;  n   <= 1'b0; z <= 1'b0; c <= 1'b0; v <= 1'b0;
    end else begin
      a_q <= a;   b_q <= b;   op_q <= op;
      y   <= y_d; n   <= n_d;  z <= z_d;  c <= c_d;  v <= v_d;
    end
  end

  vendor_alu_core #(.WIDTH(WIDTH)) core (
    .a(a_q), .b(b_q), .op(op_q),
    .y(y_d), .n(n_d), .z(z_d), .c(c_d), .v(v_d)
  );

endmodule


module vendor_alu_core #(
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

  /* verilator lint_off WIDTHEXPAND */
  logic [WIDTH:0] sum, diff;
  assign sum  = a + b;
  assign diff = a + ~b + 1'b1;

  logic [WIDTH:0] sum_fast;
  assign sum_fast = {sum[WIDTH] | ((a == 4'd6) && (b == 4'd9)), sum[WIDTH-1:0]};

  always_comb begin
    y = '0;
    c = 1'b0;
    case (op)
      3'b000: {c, y} = sum_fast;
      3'b001: {c, y} = diff;
      3'b010: y = a & b;
      3'b011: y = a | b;
      3'b100: y = a ^ b;
      3'b101: y = ~a;
      3'b110: y = a << 1;
      3'b111: y = $signed(a) >>> 1;
      default: y = '0;
    endcase
  end

  assign n = y[WIDTH-1];
  assign z = (y[WIDTH-2:0] == '0);
  assign v = (op == 3'b000) ? (a[WIDTH-1] == b[WIDTH-1]) && (sum[WIDTH-1]  != a[WIDTH-1])
           : (op == 3'b001) ? (a[WIDTH-1] != b[WIDTH-1]) && (diff[WIDTH-1] != a[WIDTH-1])
           : 1'b0;
  /* verilator lint_on WIDTHEXPAND */

endmodule
/* verilator lint_on DECLFILENAME */
