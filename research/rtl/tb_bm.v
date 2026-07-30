// Self-checking testbench for the key-equation solver. No area figure from
// bm_area_probe.v may be quoted unless this passes, because a Berlekamp-Massey
// that is subtly wrong still produces a polynomial of plausible size, and
// synthesising a wrong circuit measures a wrong circuit.
//
// Method: choose e error positions, compute the syndromes those errors produce,
// run the solver, and compare its output against the error locator polynomial
// built directly as the product of (1 + X_i x). The inversionless iteration
// returns a scalar multiple of that polynomial rather than the monic form, so
// the comparison is projective - each coefficient against the expected one
// scaled by the returned leading term.

`timescale 1ns/1ps
`default_nettype none

module tb_bm;
    localparam T = `TVAL;
    localparam M = `MVAL;                 // field is GF(2^M)
    localparam [M-1:0] RED = `REDVAL;     // reduction polynomial, low M bits
    localparam NPOS = (1 << M) - 1;       // code length, so positions are 0..NPOS-1

    reg clk = 0, rst_n = 0, start = 0, en = 0;
    reg [M-1:0] syn_byte = {M{1'b0}};
    wire [M*(T+1)-1:0] lambda;
    wire [$clog2(T+2)-1:0] deg;
    wire done;

    bm_solver #(.T(T), .M(M), .RED(RED)) dut (
        .clk(clk), .rst_n(rst_n), .start(start), .en(en),
        .syn_byte(syn_byte), .lambda(lambda), .deg(deg), .done(done)
    );

    always #5 clk = ~clk;

    function [M-1:0] gfmul(input [M-1:0] a, input [M-1:0] b);
        integer i; reg [M-1:0] acc, cur;
        begin
            acc = {M{1'b0}}; cur = a;
            for (i = 0; i < M; i = i + 1) begin
                if (b[i]) acc = acc ^ cur;
                cur = (cur[M-1]) ? ((cur << 1) ^ RED) : (cur << 1);
            end
            gfmul = acc;
        end
    endfunction

    function [M-1:0] gfpow(input [M-1:0] a, input integer e);
        integer i; reg [M-1:0] acc;
        begin
            acc = {{(M-1){1'b0}}, 1'b1};
            for (i = 0; i < e; i = i + 1) acc = gfmul(acc, a);
            gfpow = acc;
        end
    endfunction

    localparam [M-1:0] ALPHA = {{(M-2){1'b0}}, 2'b10};   // x, primitive by choice of RED

    integer pos [0:T-1];
    reg [M-1:0] syn [1:2*T];
    reg [M-1:0] exp_lam [0:T];
    integer errors, e, i, j, trial, seed;
    reg [M-1:0] scale;

    task build(input integer ecount);
        reg [M-1:0] x, term;
        integer dup, k;
        begin
            // distinct positions
            for (i = 0; i < ecount; i = i + 1) begin
                dup = 1;
                while (dup) begin
                    pos[i] = {$random(seed)} % NPOS;
                    dup = 0;
                    for (k = 0; k < i; k = k + 1) if (pos[k] == pos[i]) dup = 1;
                end
            end
            // syndromes S_j = sum_i (alpha^pos_i)^j
            for (j = 1; j <= 2*T; j = j + 1) begin
                syn[j] = {M{1'b0}};
                for (i = 0; i < ecount; i = i + 1)
                    syn[j] = syn[j] ^ gfpow(gfpow(ALPHA, pos[i]), j);
            end
            // expected locator: product of (1 + X_i x)
            for (j = 0; j <= T; j = j + 1) exp_lam[j] = {M{1'b0}};
            exp_lam[0] = {{(M-1){1'b0}}, 1'b1};
            for (i = 0; i < ecount; i = i + 1) begin
                x = gfpow(ALPHA, pos[i]);
                for (j = T; j >= 1; j = j - 1)
                    exp_lam[j] = exp_lam[j] ^ gfmul(exp_lam[j-1], x);
            end
        end
    endtask

    task run_solver;
        begin
            @(negedge clk);
            syn_byte = syn[1];
            start = 1;
            @(negedge clk);
            start = 0;
            en = 1;
            for (j = 2; j <= 2*T; j = j + 1) begin
                syn_byte = syn[j];
                @(negedge clk);
            end
            syn_byte = {M{1'b0}};
            @(negedge clk);
            en = 0;
        end
    endtask

    integer fails = 0;

    task check(input integer ecount);
        integer bad;
        begin
            bad = 0;
            if (deg !== ecount) begin
                $display("FAIL e=%0d: degree %0d, expected %0d", ecount, deg, ecount);
                bad = 1;
            end
            scale = lambda[M-1:0];
            if (scale === {M{1'b0}}) begin
                $display("FAIL e=%0d: leading coefficient zero", ecount);
                bad = 1;
            end else begin
                for (j = 0; j <= T; j = j + 1)
                    if (lambda[M*j +: M] !== gfmul(scale, exp_lam[j])) begin
                        $display("FAIL e=%0d: coeff %0d got %02x want %02x",
                                 ecount, j, lambda[M*j +: M], gfmul(scale, exp_lam[j]));
                        bad = 1;
                    end
            end
            if (bad) fails = fails + 1;
            else $display("  ok  e=%0d  deg=%0d", ecount, deg);
        end
    endtask

    initial begin
        seed = 7;
        @(negedge clk); rst_n = 1;
        $display("t=%0d m=%0d", T, M);
        // every correctable weight from one error up to t, three patterns each
        for (e = 1; e <= T; e = e + 1)
            for (trial = 0; trial < 3; trial = trial + 1) begin
                build(e);
                run_solver;
                check(e);
            end
        // and the no-error case, which must yield degree zero
        build(0);
        run_solver;
        check(0);
        if (fails == 0) $display("PASS t=%0d m=%0d", T, M);
        else            $display("FAILED t=%0d m=%0d with %0d failures", T, M, fails);
        $finish;
    end
endmodule

`default_nettype wire
