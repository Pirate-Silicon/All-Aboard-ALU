//------------------------------------------------------------------------
// alu_tb.sv - optional bonus for step 3.
//------------------------------------------------------------------------
// The same testbench as tb/test_alu.py, piece for piece, in SystemVerilog.
// Section numbers match. The differences worth noticing:
//
//   Python                       SystemVerilog
//   @dataclass AluTxn            class AluTxn, with `rand` fields
//   random.randrange()           t.randomize()
//   cocotb.queue.Queue           mailbox
//   async def / await            task / @(negedge clk)
//   import alu_model             model() written again, below
//
// The model is written again because SystemVerilog can't import your
// Python. That's not all bad: real teams often write the model in a
// different language from the design on purpose, so the two can't share a
// misunderstanding.
//
// Run it from tb_sv/:
//     make                  corner cases + 500 random, on your ALU
//     make EXHAUSTIVE=1     corner cases + every input
//     make DUT=buggy        on the vendor ALU
//
// Every TODO(step3) is yours. The MONITOR is given in full.
//------------------------------------------------------------------------

`timescale 1ns/1ps

module alu_tb;

  localparam int LATENCY  = 2;
  localparam int N_RANDOM = 500;
  localparam int MAX_PRINTED = 10;

  typedef enum logic [2:0] {ADD, SUB, AND, OR, XOR, NOT, SHL, SHR} op_t;

  typedef struct packed {
    logic [3:0] y;
    logic       n, z, c, v;
  } result_t;

  //----------------------------------------------------------------------
  // Clock and the wires to the DUT
  //----------------------------------------------------------------------
  logic       clk = 1'b0;
  logic       rst;
  logic [3:0] a, b, y;
  logic [2:0] op;
  logic       n, z, c, v;

  always #5 clk = ~clk;

  alu dut (.*);

  //======================================================================
  // 0. TRANSACTION                                    uvm_sequence_item
  //======================================================================
  class AluTxn;
    rand logic [2:0] op;
    rand logic [3:0] a;
    rand logic [3:0] b;

    function new(logic [2:0] op = 0, logic [3:0] a = 0, logic [3:0] b = 0);
      this.op = op;
      this.a  = a;
      this.b  = b;
    endfunction

    function string show();
      op_t o = op_t'(op);
      return $sformatf("%-3s a=%2d b=%2d", o.name(), a, b);
    endfunction
  endclass

  //======================================================================
  // MODEL                                                    (reference)
  //======================================================================
  // What the ALU should do, from the spec. It will look a lot like your
  // alu_core.sv, and that's the danger: write it from SPEC.md and your
  // Python model, not by copying your RTL.
  function automatic result_t model(logic [2:0] op, logic [3:0] a, logic [3:0] b);
    result_t r = '0;
    logic [4:0] full;
    case (op_t'(op))
      ADD: begin                                    // given, as the pattern
        full = {1'b0, a} + {1'b0, b};
        r.y  = full[3:0];
        r.c  = full[4];
        r.v  = (a[3] == b[3]) && (r.y[3] != a[3]);
      end
      // TODO(step3): SUB, AND, OR, XOR, NOT, SHL, SHR.
      default: r.y = '0;
    endcase
    // TODO(step3): n and z.
    return r;
  endfunction

  function automatic string fmt(result_t r);
    return $sformatf("y=%2d n=%0d z=%0d c=%0d v=%0d", r.y, r.n, r.z, r.c, r.v);
  endfunction

  //----------------------------------------------------------------------
  // The channels between components.
  //----------------------------------------------------------------------
  mailbox #(AluTxn)   todo = new();
  mailbox #(AluTxn)   sent = new();
  mailbox #(result_t) seen = new();

  int n_seen    = 0;
  int n_checked = 0;
  int errors    = 0;

  //======================================================================
  // 1. GENERATOR                                           uvm_sequence
  //======================================================================
  task automatic add_corner_cases();
    AluTxn t;
    t = new(ADD,  7,  1); todo.put(t);   // signed overflow, positive to negative
    t = new(SUB,  0,  1); todo.put(t);   // borrow: C must be 0
    // TODO(step3): the rest of your corner cases from Part A.
  endtask

  // Given, as the pattern. randomize() fills every `rand` field. It returns
  // 0 if it couldn't (impossible constraints), and ignoring that would
  // quietly send whatever was in the object before. Always check it.
  task automatic add_random(int count);
    AluTxn t;
    repeat (count) begin
      t = new();
      if (t.randomize() == 0) $fatal(1, "randomize() failed");
      todo.put(t);
    end
  endtask

  task automatic add_exhaustive();
    // TODO(step3): every op, every a, every b. new(3'(o), 4'(i), 4'(j))
    // makes a transaction from loop counters.
  endtask

  //======================================================================
  // 2. DRIVER                                                uvm_driver
  //======================================================================
  task automatic driver();
    AluTxn t;
    forever begin
      todo.get(t);
      @(negedge clk);
      a  = t.a;
      // TODO(step3): drive b and op too.
      sent.put(t);
    end
  endtask

  //======================================================================
  // 3. MONITOR                                              uvm_monitor
  //======================================================================
  task automatic monitor();
    result_t r;
    repeat (LATENCY) @(negedge clk);
    forever begin
      @(negedge clk);
      r = '{y: y, n: n, z: z, c: c, v: v};
      seen.put(r);
    end
  endtask

  //======================================================================
  // 4. SCOREBOARD                                        uvm_scoreboard
  //======================================================================
  task automatic scoreboard();
    AluTxn   t;
    result_t got, expected;
    forever begin
      sent.get(t);
      seen.get(got);
      n_seen++;
      sample_coverage(t, model(t.op, t.a, t.b));   // what we tried, not what came back
      // TODO(step3): ask model() for the expected result, count n_checked,
      // and on a mismatch count errors and $display the check number,
      // t.show(), fmt(expected) and fmt(got). Compare with !==, not !=:
      // !== also catches X and Z bits, which != would let slide.
      expected = '0;
    end
  endtask

  //======================================================================
  // 5. COVERAGE                                              covergroup
  //======================================================================
  int op_hits    [8];
  int z_hits     [8][2];
  int flag_hits  [8][4][2];       // [op][n,z,c,v][0/1]; only ADD and SUB are used

  function automatic void sample_coverage(AluTxn t, result_t r);
    op_hits[t.op]++;
    if (t.op == ADD || t.op == SUB) begin
      // TODO(step3): count the four flag bins, one line each:
      //   flag_hits[t.op][0][r.n]++;   is the one for n.
    end else begin
      z_hits[t.op][r.z]++;
    end
  endfunction

  function automatic real coverage_percent();
    int hit = 0, total = 0;
    for (int o = 0; o < 8; o++) begin
      total++; if (op_hits[o] > 0) hit++;
    end
    for (int o = 2; o < 8; o++)
      for (int val = 0; val < 2; val++) begin
        total++; if (z_hits[o][val] > 0) hit++;
      end
    for (int o = 0; o < 2; o++)
      for (int f = 0; f < 4; f++)
        for (int val = 0; val < 2; val++) begin
          total++; if (flag_hits[o][f][val] > 0) hit++;
        end
    return 100.0 * hit / total;
  endfunction

  //======================================================================
  // Run
  //======================================================================
  initial begin
    int n_txns;

    rst = 1'b1; a = '0; b = '0; op = '0;
    repeat (2) @(negedge clk);
    rst = 1'b0;

    add_corner_cases();
`ifdef EXHAUSTIVE
    add_exhaustive();
`else
    add_random(N_RANDOM);
`endif
    n_txns = todo.num();

    fork
      driver();
      monitor();
      scoreboard();
    join_none

    wait (n_seen == n_txns);

    $display("");
    $display("============================================================");
    $display(" sent    : %0d", n_txns);
    $display(" checked : %0d", n_checked);
    $display(" errors  : %0d", errors);
    $display(" coverage: %0.1f%%", coverage_percent());
    $display("============================================================");
    if (n_checked != n_txns)
      $display(" FAIL: the scoreboard only checked %0d of %0d. Does it count every transaction?",
               n_checked, n_txns);
    else if (errors != 0)
      $display(" FAIL");
    else
      $display(" PASS");
    $display("");
    $finish;
  end

  initial begin
    #1ms;
    $display("[FAIL] timeout. Is a mailbox empty that something is waiting on?");
    $finish;
  end

endmodule
