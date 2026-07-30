// Differential against the parallel Chien inside the generated tables module: the same
// locator in, the same set of root positions out.
`timescale 1ns/1ps
`default_nettype none
module tb_chien_diff;
    localparam T=21, M=7, NPOS=127;
    localparam [M-1:0] RED = 7'h09;
    reg clk=0, rst_n=0, s_start=0, p_start=0, p_en=0;
    reg [M*(T+1)-1:0] lambda=0, apow=0;
    wire p_root;
    wire [$clog2(NPOS)-1:0] s_pos;
    wire s_root, s_valid, s_done;
    bch127t21_chien par (.clk(clk), .rst_n(rst_n), .start(p_start), .en(p_en),
                         .lambda(lambda), .root(p_root));
    chien_serial #(.T(T), .M(M), .RED(RED), .NPOS(NPOS)) ser (
        .clk(clk), .rst_n(rst_n), .start(s_start), .lambda(lambda), .alpha_pow(apow),
        .position(s_pos), .root(s_root), .root_valid(s_valid), .done(s_done));
    always #5 clk = ~clk;
    function [M-1:0] gfmul(input [M-1:0] x, input [M-1:0] y);
        integer i; reg [M-1:0] acc, cur;
        begin acc={M{1'b0}}; cur=x;
            for (i=0;i<M;i=i+1) begin
                if (y[i]) acc=acc^cur;
                cur=(cur[M-1])?((cur<<1)^RED):(cur<<1);
            end
            gfmul=acc; end
    endfunction
    integer i, c, seed, fails, trial;
    reg [NPOS-1:0] pr, sr;
    reg [M-1:0] t;
    always @(posedge clk) if (s_valid) sr[s_pos] = s_root;
    initial begin
        seed=31; fails=0;
        t = {{(M-2){1'b0}},2'b10};
        apow[0 +: M] = {{(M-1){1'b0}},1'b1};
        for (i=1;i<=T;i=i+1) apow[M*i +: M] = gfmul(apow[M*(i-1) +: M], t);
        @(negedge clk); rst_n=1;
        for (trial=0; trial<6; trial=trial+1) begin
            for (i=0;i<=T;i=i+1) lambda[M*i +: M] = {$random(seed)};
            // parallel: sample root each cycle over the sweep
            pr = {NPOS{1'b0}};
            @(negedge clk); p_start=1;
            @(negedge clk); p_start=0; p_en=1;
            for (c=0;c<NPOS;c=c+1) begin
                if (p_root) pr[(NPOS-c)%NPOS] = 1'b1;
                @(negedge clk);
            end
            p_en=0;
            sr = {NPOS{1'b0}};
            s_start=1; @(negedge clk); s_start=0;
            wait (s_done); repeat (2) @(negedge clk);
            if (sr !== pr) begin
                $display("FAIL trial %0d: root sets differ", trial);
                fails = fails + 1;
            end
        end
        if (fails==0) $display("PASS chien_serial matches the parallel Chien on 6 locators");
        else          $display("FAILED chien_serial with %0d mismatches", fails);
        $finish;
    end
endmodule
`default_nettype wire
