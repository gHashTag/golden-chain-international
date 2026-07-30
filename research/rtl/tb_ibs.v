`timescale 1ns/1ps
`default_nettype none
module tb_ibs;
    localparam BLOCK = 4, NBITS = 16, PW = 2;
    reg clk=0, rst_n=0, start=0, resp_bit=0, resp_valid=0;
    reg [PW-1:0] pointer=0;
    wire code_bit, code_valid, done;
    ibs_select #(.BLOCK(BLOCK), .NBITS(NBITS)) dut (
        .clk(clk), .rst_n(rst_n), .start(start), .resp_bit(resp_bit),
        .resp_valid(resp_valid), .pointer(pointer), .code_bit(code_bit),
        .code_valid(code_valid), .done(done));
    always #5 clk = ~clk;
    integer i, j, seed, fails, got_n;
    reg [BLOCK-1:0] block [0:NBITS-1];
    reg [PW-1:0]    ptr   [0:NBITS-1];
    reg             want  [0:NBITS-1];
    reg             got   [0:NBITS-1];
    always @(posedge clk) if (code_valid) begin got[got_n] = code_bit; got_n = got_n + 1; end
    initial begin
        seed = 5; fails = 0; got_n = 0;
        for (i = 0; i < NBITS; i = i + 1) begin
            block[i] = {$random(seed)};
            ptr[i]   = {$random(seed)} % BLOCK;
            want[i]  = block[i][ptr[i]];
        end
        @(negedge clk); rst_n = 1;
        @(negedge clk); start = 1;
        @(negedge clk); start = 0; resp_valid = 1;
        for (i = 0; i < NBITS; i = i + 1) begin
            pointer = ptr[i];
            for (j = 0; j < BLOCK; j = j + 1) begin
                resp_bit = block[i][j];
                @(negedge clk);
            end
        end
        resp_valid = 0;
        repeat (3) @(negedge clk);
        if (got_n !== NBITS) begin
            $display("FAIL: recovered %0d of %0d codeword bits", got_n, NBITS);
            fails = fails + 1;
        end else
            for (i = 0; i < NBITS; i = i + 1)
                if (got[i] !== want[i]) begin
                    $display("FAIL: bit %0d got %b want %b", i, got[i], want[i]);
                    fails = fails + 1;
                end
        if (fails == 0) $display("PASS ibs_select: %0d pointers followed to the right positions", NBITS);
        else            $display("FAILED ibs_select with %0d failures", fails);
        $finish;
    end
endmodule
`default_nettype wire
