// The property the countermeasure relies on is diffusion: one bit of helper data must
// change a large fraction of the output. That is what this measures. It does not verify
// the permutation against official SPONGENT vectors, which are not in hand.
`timescale 1ns/1ps
`default_nettype none
module tb_spongent;
    localparam B = 88;
    reg clk = 0, rst_n = 0, start = 0;
    reg  [B-1:0] din = 0;
    wire [B-1:0] state;
    wire done;
    spongent_permutation dut (.clk(clk), .rst_n(rst_n), .start(start),
                             .data_in(din), .state(state), .done(done));
    always #5 clk = ~clk;

    integer trial, bit_i, hd, total, worst, best, seed;
    reg [B-1:0] a, b, base;

    task run(input [B-1:0] v, output [B-1:0] out);
        begin
            @(negedge clk); din = v; start = 1;
            @(negedge clk); start = 0;
            wait (done);
            @(negedge clk);
            out = state;
        end
    endtask

    initial begin
        seed = 17; total = 0; worst = B; best = 0;
        @(negedge clk); rst_n = 1;
        for (trial = 0; trial < 24; trial = trial + 1) begin
            base = {$random(seed), $random(seed), $random(seed)};
            run(base, a);
            bit_i = {$random(seed)} % B;
            run(base ^ (1 << bit_i), b);
            hd = 0;
            for (bit_i = 0; bit_i < B; bit_i = bit_i + 1)
                if (a[bit_i] !== b[bit_i]) hd = hd + 1;
            total = total + hd;
            if (hd < worst) worst = hd;
            if (hd > best)  best  = hd;
        end
        $display("avalanche over 24 single-bit flips, %0d-bit state:", B);
        $display("  mean %0d.%0d of %0d bits changed, range %0d to %0d",
                 total/24, (total*10/24)%10, B, worst, best);
        if (total/24 >= B/3 && worst >= B/6)
            $display("PASS spongent diffusion: one input bit moves a large fraction of the output");
        else
            $display("FAILED spongent diffusion: mean %0d worst %0d", total/24, worst);
        $finish;
    end
endmodule
`default_nettype wire
