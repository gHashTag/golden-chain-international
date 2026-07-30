// End-to-end decode through all three stages: syndrome bank, key-equation solver,
// Chien search. The stages had been measured separately and never driven together,
// and doing so found a defect in one of them.
//
// Method. BCH is linear, so decoding a received word equal to the error pattern
// alone is decoding the all-zero codeword - which is a codeword - and exercises the
// whole error-locating path without needing an encoder. Errors are injected at known
// positions, the hardware locates them, and the test asserts that the set of
// positions the Chien search flags is exactly the set injected.

`timescale 1ns/1ps
`default_nettype none

module tb_bch_e2e;
    localparam M = `MVAL;
    localparam T = `TVAL;
    localparam N = (1 << M) - 1;

    reg clk = 0, rst_n = 0;
    reg syn_load = 0, syn_en = 0, bit_in = 0;
    reg chien_start = 0, chien_en = 0;
    wire [M*2*T-1:0] syn;
    wire root;
    reg  [M*(T+1)-1:0] lambda_in;

    `TOPNAME dut (
        .clk(clk), .rst_n(rst_n), .syn_load(syn_load), .syn_en(syn_en),
        .bit_in(bit_in), .chien_start(chien_start), .chien_en(chien_en),
        .lambda(lambda_in), .syn(syn), .root(root)
    );

    reg bm_start = 0, bm_en = 0;
    reg  [M-1:0] bm_syn_byte = 0;
    wire [M*(T+1)-1:0] bm_lambda;
    wire [$clog2(T+2)-1:0] bm_deg;
    wire bm_done;

    bm_solver #(.T(T), .M(M), .RED(`REDVAL)) solver (
        .clk(clk), .rst_n(rst_n), .start(bm_start), .en(bm_en),
        .syn_byte(bm_syn_byte), .lambda(bm_lambda), .deg(bm_deg), .done(bm_done)
    );

    always #5 clk = ~clk;

    reg [N-1:0] rx;
    integer pos [0:T-1];
    integer i, j, e, trial, seed, fails, dup, k, found_count, cyc;
    reg [N-1:0] flagged;

    task decode(input integer ecount);
        begin
            // ── stage one: stream the received word into the syndrome bank,
            //    most significant position first
            @(negedge clk); syn_load = 1;
            @(negedge clk); syn_load = 0; syn_en = 1;
            for (i = N-1; i >= 0; i = i - 1) begin
                bit_in = rx[i];
                @(negedge clk);
            end
            syn_en = 0;

            // ── stage two: syndromes into the solver, S_1 first
            bm_syn_byte = syn[0 +: M];
            bm_start = 1; @(negedge clk); bm_start = 0; bm_en = 1;
            for (j = 1; j < 2*T; j = j + 1) begin
                bm_syn_byte = syn[M*j +: M];
                @(negedge clk);
            end
            @(negedge clk); bm_en = 0;

            // ── stage three: locator into the Chien search, sweep all positions
            lambda_in = bm_lambda;
            chien_start = 1; @(negedge clk); chien_start = 0;
            flagged = {N{1'b0}};
            chien_en = 1;
            for (cyc = 0; cyc < N; cyc = cyc + 1) begin
                // after cyc multiplies the sum is Lambda(alpha^cyc); a root there
                // means an error at position (N - cyc) mod N
                if (root) flagged[(N - cyc) % N] = 1'b1;
                @(negedge clk);
            end
            chien_en = 0;
        end
    endtask

    initial begin
        seed = 11; fails = 0;
        @(negedge clk); rst_n = 1;
        $display("end-to-end m=%0d t=%0d n=%0d", M, T, N);
        for (e = 1; e <= T; e = e + 1) begin
            for (trial = 0; trial < 2; trial = trial + 1) begin
                rx = {N{1'b0}};
                for (i = 0; i < e; i = i + 1) begin
                    dup = 1;
                    while (dup) begin
                        pos[i] = {$random(seed)} % N;
                        dup = 0;
                        for (k = 0; k < i; k = k + 1) if (pos[k] == pos[i]) dup = 1;
                    end
                    rx[pos[i]] = 1'b1;
                end
                decode(e);
                // the flagged set must equal the injected set, exactly
                if (flagged !== rx) begin
                    $display("FAIL e=%0d: located set differs from injected set", e);
                    fails = fails + 1;
                end else if (bm_deg !== e) begin
                    $display("FAIL e=%0d: locator degree %0d", e, bm_deg);
                    fails = fails + 1;
                end
            end
        end
        if (fails == 0) $display("PASS end-to-end m=%0d t=%0d, weights 1..%0d", M, T, T);
        else            $display("FAILED end-to-end with %0d failures", fails);
        $finish;
    end
endmodule

`default_nettype wire
