// Self-checking testbench for the Reed-Muller decoder. Same rule as the key
// equation solver: no area figure is quoted from a circuit that has not decoded
// correctly, and the check must be shown capable of failing.

`timescale 1ns/1ps
`default_nettype none

module tb_rm;
    localparam M = 6;
    localparam N = 1 << M;

    reg clk = 0, rst_n = 0, start = 0;
    reg [N-1:0] rword = 0;
    wire [M:0] msg;
    wire done;

    rm_decoder #(.M(M)) dut (
        .clk(clk), .rst_n(rst_n), .start(start), .rword(rword),
        .msg(msg), .done(done)
    );

    always #5 clk = ~clk;

    reg [M:0] tx;
    integer i, b, e, trial, seed, fails, flips, pos, par;
    reg [N-1:0] code;

    task encode;
        begin
            for (i = 0; i < N; i = i + 1) begin
                par = tx[0];
                for (b = 0; b < M; b = b + 1)
                    if (i[b]) par = par ^ tx[b+1];
                code[i] = par[0];
            end
        end
    endtask

    initial begin
        seed = 3; fails = 0;
        @(negedge clk); rst_n = 1;
        // every error weight the code can correct, several messages each
        for (e = 0; e <= 15; e = e + 1) begin
            for (trial = 0; trial < 4; trial = trial + 1) begin
                tx = {$random(seed)} % 128;
                encode;
                rword = code;
                flips = 0;
                while (flips < e) begin
                    pos = {$random(seed)} % N;
                    rword[pos] = ~rword[pos];
                    flips = flips + 1;
                end
                @(negedge clk); start = 1;
                @(negedge clk); start = 0;
                wait (done);
                @(negedge clk);
                if (msg !== tx) begin
                    $display("FAIL e=%0d msg=%b expected %b", e, msg, tx);
                    fails = fails + 1;
                end
            end
        end
        if (fails == 0) $display("PASS rm M=%0d, weights 0..15", M);
        else            $display("FAILED rm with %0d failures", fails);
        $finish;
    end
endmodule

`default_nettype wire
