// Differential test: the serialised solver against the parallel one, which is already
// verified end to end. Same syndromes in, the same locator must come out. This is a
// cheaper and stronger check than re-deriving the expected locator, because the reference
// has itself been checked against constructed error patterns and against injected faults.
`timescale 1ns/1ps
`default_nettype none
module tb_bm_diff;
    localparam T = `TVAL, M = `MVAL;
    localparam [M-1:0] RED = `REDVAL;
    reg clk=0, rst_n=0, p_start=0, p_en=0, s_start=0;
    reg [M-1:0] p_syn=0;
    reg [M*2*T-1:0] syn_all=0;
    wire [M*(T+1)-1:0] p_lam, s_lam;
    wire [$clog2(T+2)-1:0] p_deg, s_deg;
    wire p_done, s_done;
    bm_solver #(.T(T), .M(M), .RED(RED)) par (
        .clk(clk), .rst_n(rst_n), .start(p_start), .en(p_en),
        .syn_byte(p_syn), .lambda(p_lam), .deg(p_deg), .done(p_done));
    bm_serial #(.T(T), .M(M), .RED(RED)) ser (
        .clk(clk), .rst_n(rst_n), .start(s_start),
        .syn(syn_all), .lambda(s_lam), .deg(s_deg), .done(s_done));
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
        begin acc = {{(M-1){1'b0}},1'b1};
            for (i=0;i<e;i=i+1) acc = gfmul(acc,a); gfpow = acc; end
    endfunction

    localparam NPOS = (1<<M)-1;
    integer pos [0:T-1];
    reg [M-1:0] syn [1:2*T];
    integer e, trial, i, j, k, dup, seed, fails;

    initial begin
        seed = 23; fails = 0;
        @(negedge clk); rst_n = 1;
        for (e = 1; e <= T; e = e + 1) begin
            for (trial = 0; trial < 2; trial = trial + 1) begin
                for (i = 0; i < e; i = i + 1) begin
                    dup = 1;
                    while (dup) begin
                        pos[i] = {$random(seed)} % NPOS; dup = 0;
                        for (k = 0; k < i; k = k + 1) if (pos[k] == pos[i]) dup = 1;
                    end
                end
                for (j = 1; j <= 2*T; j = j + 1) begin
                    syn[j] = {M{1'b0}};
                    for (i = 0; i < e; i = i + 1)
                        syn[j] = syn[j] ^ gfpow(gfpow({{(M-2){1'b0}},2'b10}, pos[i]), j);
                    syn_all[M*(j-1) +: M] = syn[j];
                end
                // parallel reference
                @(negedge clk); p_syn = syn[1]; p_start = 1;
                @(negedge clk); p_start = 0; p_en = 1;
                for (j = 2; j <= 2*T; j = j + 1) begin p_syn = syn[j]; @(negedge clk); end
                @(negedge clk); p_en = 0;
                // serialised
                s_start = 1; @(negedge clk); s_start = 0;
                wait (s_done); @(negedge clk);
                if (s_lam !== p_lam || s_deg !== p_deg) begin
                    $display("FAIL e=%0d: serial deg %0d parallel deg %0d, locators %s",
                             e, s_deg, p_deg, (s_lam === p_lam) ? "match" : "differ");
                    fails = fails + 1;
                end
            end
        end
        if (fails == 0) $display("PASS bm_serial matches bm_solver on %0d cases", 2*T);
        else            $display("FAILED bm_serial with %0d mismatches", fails);
        $finish;
    end
endmodule
`default_nettype wire
