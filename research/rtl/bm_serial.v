// Berlekamp-Massey with the multipliers shared instead of replicated.
//
// The parallel form in bm_area_probe.v instantiates 3(t+1) general GF multipliers - 66 at
// t=21 - and is 62,490 of the 79,787 square micrometres the decoder costs. That is 78
// percent of the decoder and the decoder is 87 percent of the design, so this one choice
// is two thirds of the whole budget.
//
// It is also a choice made for a use case this is not. A communications decoder needs a
// codeword per symbol time; a key generator runs once at power-up and may take as long as
// it likes. This trades that latency back for area: two multipliers, used over and over.
//
// Cycles: the discrepancy is an inner product over t+1 terms, one per cycle, and the update
// is t+1 coefficients with two multiplies each, done with two multipliers in one cycle
// apiece. So about 2(t+1) cycles per iteration and 2t iterations - roughly 4t^2, which is
// 1,850 cycles at t=21. At ten megahertz that is 185 microseconds, once, at boot.

`default_nettype none

module bm_serial #(
    parameter T = 21,
    parameter M = 7,
    parameter [M-1:0] RED = 7'h09
) (
    input  wire                clk,
    input  wire                rst_n,
    input  wire                start,
    input  wire [M*2*T-1:0]    syn,        // all syndromes, S_1 first
    output wire [M*(T+1)-1:0]  lambda,
    output reg  [$clog2(T+2)-1:0] deg,
    output reg                 done
);
    localparam LW = $clog2(T+2);
    localparam IW = $clog2(T+2);

    reg [M-1:0] lam [0:T];
    reg [M-1:0] bee [0:T];
    reg [M-1:0] gamma, delta;
    reg [LW-1:0] ell;
    reg [$clog2(2*T+1)-1:0] r;
    reg [IW-1:0] idx;
    reg [1:0]    phase;          // 0 discrepancy, 1 update, 2 commit
    reg [M-1:0] nlam [0:T];      // the update lands here, then commits in one step so
                                 // that the discrepancy phase read consistent lambda

    // syndrome window: S_{r+1-j}, addressed rather than shifted
    wire [$clog2(2*T+1)-1:0] widx = r - idx;
    wire in_range = (idx <= r) && (r - idx) < 2*T;
    wire [M-1:0] swin = in_range ? syn[M*widx +: M] : {M{1'b0}};

    // The two shared multipliers, which are the whole point of this module. Their
    // operands are selected combinationally rather than registered: registering them and
    // using the product in the same cycle makes the product reflect the previous cycle's
    // operands, which is how the first version of this module was wrong.
    wire [M-1:0] a0 = (phase == 2'd0) ? lam[idx] : gamma;
    wire [M-1:0] b0 = (phase == 2'd0) ? swin     : lam[idx];
    wire [M-1:0] a1 = delta;
    wire [M-1:0] b1 = (idx == 0) ? {M{1'b0}} : bee[idx-1];
    wire [M-1:0] p0, p1;
    gf_mul #(.M(M), .RED(RED)) m0 (.a(a0), .b(b0), .y(p0));
    gf_mul #(.M(M), .RED(RED)) m1 (.a(a1), .b(b1), .y(p1));


    wire lengthen = (delta != {M{1'b0}}) && ({ell, 1'b0} <= r);

    integer i;
    always @(posedge clk) begin
        if (!rst_n || start) begin
            for (i = 0; i <= T; i = i + 1) begin
                lam[i] <= (i == 0) ? {{(M-1){1'b0}}, 1'b1} : {M{1'b0}};
                bee[i] <= (i == 0) ? {{(M-1){1'b0}}, 1'b1} : {M{1'b0}};
            end
            gamma <= {{(M-1){1'b0}}, 1'b1};
            delta <= {M{1'b0}};
            ell   <= {LW{1'b0}};
            r     <= 0;
            idx   <= {IW{1'b0}};
            phase <= 2'd0;
            done  <= 1'b0;
        end else if (!done) begin
            case (phase)
            2'd0: begin                       // accumulate the discrepancy, one term a cycle
                delta <= (idx == 0) ? p0 : (delta ^ p0);
                if (idx == T) begin idx <= 0; phase <= 2'd1; end
                else idx <= idx + 1'b1;
            end
            2'd1: begin                       // one coefficient a cycle, two multiplies
                nlam[idx] <= p0 ^ p1;
                if (idx == T) begin idx <= 0; phase <= 2'd2; end
                else idx <= idx + 1'b1;
            end
            default: begin                    // commit both the update and the length
                for (i = 0; i <= T; i = i + 1) lam[i] <= nlam[i];
                if (lengthen) begin
                    for (i = 0; i <= T; i = i + 1) bee[i] <= lam[i];
                    gamma <= delta;
                    ell   <= (r + 1'b1) - ell;
                end else begin
                    bee[0] <= {M{1'b0}};
                    for (i = 1; i <= T; i = i + 1) bee[i] <= bee[i-1];
                end
                delta <= {M{1'b0}};
                idx   <= 0;
                phase <= 2'd0;
                if (r == 2*T - 1) done <= 1'b1;
                else              r <= r + 1'b1;
            end
            endcase
        end
    end


    genvar j;
    generate
        for (j = 0; j <= T; j = j + 1) begin : flat
            assign lambda[M*j +: M] = lam[j];
        end
    endgenerate
    always @* deg = ell;
endmodule

`default_nettype wire
