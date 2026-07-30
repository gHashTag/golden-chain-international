// Key-equation solver for the PUF fuzzy extractor's decoder: the third stage,
// left out of bch_area_probe.v because writing it unverified in one pass and
// reporting the result as measured would have been worse than saying it was not
// measured. This file exists to remove that gap, and it comes with a testbench
// that must pass before any area figure from it is quoted.
//
// Algorithm: the inversionless Berlekamp-Massey iteration. Inversionless because
// a GF(2^8) inverter is expensive and the standard reformulation removes it by
// carrying a scale factor instead - the discrepancy of the step that last changed
// the register length. Same field and primitive polynomial as the other stages:
// GF(2^8), x^8+x^4+x^3+x^2+1, 0x11D.
//
// Two things this deliberately does not do, both stated because they bound what
// the measurement means.
//
// First, the discrepancy here is an inner product computed in one cycle, so the
// critical path is one general multiply plus an XOR tree over t+1 terms. A
// systolic reformulation exists that shortens the path to one multiply and one
// add by spreading the same arithmetic across a regular array; it uses about the
// same number of multipliers, which is why the area figure survives the choice,
// and it is the form to use if the clock matters. Timing is not closed here.
//
// Second, the syndromes arrive as a byte per cycle on syn_byte rather than from
// an internal store. In a whole decoder they come from the syndrome bank, which
// bch_area_probe.v already measures. Keeping the store out avoids counting the
// same registers in two stages and then adding the stages together.

`default_nettype none

// General GF(2^8) multiplier - both operands variable. This is the cell that
// makes this stage expensive relative to the other two: syndrome accumulation
// and the Chien search multiply by compile-time constants, which fold into XOR
// trees, while Berlekamp-Massey multiplies two runtime values.
module gf_mul #(parameter M = 8, parameter [M-1:0] RED = 8'h1D) (
    input  wire [M-1:0] a,
    input  wire [M-1:0] b,
    output wire [M-1:0] y
);
    reg [M-1:0] acc, cur;
    integer i;
    always @* begin
        acc = {M{1'b0}};
        cur = a;
        for (i = 0; i < M; i = i + 1) begin
            if (b[i]) acc = acc ^ cur;
            cur = (cur[M-1]) ? ((cur << 1) ^ RED) : (cur << 1);
        end
    end
    assign y = acc;
endmodule

// Inversionless Berlekamp-Massey.
//
// State per iteration r = 0 .. 2t-1, with lambda the connection polynomial, B the
// correction polynomial, gamma the carried scale factor and L the register length:
//
//   delta      = sum_j lambda_j * S_{r+1-j}
//   lambda_new = gamma * lambda  +  delta * x * B
//   if delta != 0 and 2L <= r:  B <- lambda, gamma <- delta, L <- r+1-L
//   else:                       B <- x * B
//
// Addition is XOR, so subtraction does not appear. The window D holds
// S_{r+1-j} for j = 0..t and is a shift register fed by syn_byte, which is why
// the syndromes must arrive in order starting with S_1.
module bm_solver #(parameter T = 18, parameter M = 8,
                   parameter [M-1:0] RED = 8'h1D) (
    input  wire                clk,
    input  wire                rst_n,
    input  wire                start,      // load: lambda=1, B=1, gamma=1, L=0
    input  wire                en,         // advance one iteration
    input  wire [M-1:0]        syn_byte,   // S_1 first, then S_2, ...
    output wire [M*(T+1)-1:0]  lambda,
    output wire [$clog2(T+2)-1:0] deg,     // register length L
    output reg                 done
);
    localparam LW = $clog2(T+2);

    reg [M-1:0] lam [0:T];
    reg [M-1:0] bee [0:T];
    reg [M-1:0] win [0:T];
    reg [M-1:0] gamma;
    reg [LW-1:0] ell;
    reg [$clog2(2*T+1)-1:0] r;

    // ── discrepancy: t+1 general multiplies and an XOR tree ─────────────────
    wire [M-1:0] prod [0:T];
    genvar j;
    generate
        for (j = 0; j <= T; j = j + 1) begin : disc
            gf_mul #(.M(M), .RED(RED)) m (.a(lam[j]), .b(win[j]), .y(prod[j]));
        end
    endgenerate

    wire [M-1:0] dchain [0:T];
    assign dchain[0] = prod[0];
    generate
        for (j = 1; j <= T; j = j + 1) begin : dsum
            assign dchain[j] = dchain[j-1] ^ prod[j];
        end
    endgenerate
    wire [M-1:0] delta = dchain[T];

    // ── the update: two general multiplies per coefficient ──────────────────
    // Bshift is x*B, so coefficient k of x*B is B_{k-1}, and zero at k=0.
    wire [M-1:0] scaled_lam [0:T];
    wire [M-1:0] scaled_bee [0:T];
    generate
        for (j = 0; j <= T; j = j + 1) begin : upd
            gf_mul #(.M(M), .RED(RED)) ml (.a(gamma), .b(lam[j]), .y(scaled_lam[j]));
            // Coefficient zero of x*B is zero by construction. Selecting it with
            // a ternary would still elaborate bee[-1] as the untaken operand,
            // which simulation reports as an out-of-bounds read and synthesis is
            // free to treat differently - and a circuit that differs from the one
            // the testbench passed is not the circuit being measured.
            if (j == 0) begin : zero_tap
                assign scaled_bee[0] = {M{1'b0}};
            end else begin : shifted_tap
                gf_mul #(.M(M), .RED(RED)) mb (.a(delta), .b(bee[j-1]), .y(scaled_bee[j]));
            end
        end
    endgenerate

    // Length update condition. 2L <= r decides whether this step lengthens the
    // register or only corrects it, and it is the whole of the algorithm's
    // cleverness - getting it wrong yields a polynomial of the wrong degree that
    // still looks plausible, which is why the testbench checks degree as well as
    // coefficients.
    // Doubling by concatenation, not by shifting: `ell << 1` is self-determined
    // at the width of ell, so at t=18 it would truncate 36 to 4 and the length
    // condition would fire on the wrong steps while still producing a plausible
    // looking polynomial.
    wire [LW:0] two_ell = {ell, 1'b0};
    wire lengthen = (delta != {M{1'b0}}) && (two_ell <= r);

    integer i;
    always @(posedge clk) begin
        if (!rst_n) begin
            for (i = 0; i <= T; i = i + 1) begin
                lam[i] <= (i == 0) ? {{(M-1){1'b0}}, 1'b1} : {M{1'b0}};
                bee[i] <= (i == 0) ? {{(M-1){1'b0}}, 1'b1} : {M{1'b0}};
                win[i] <= {M{1'b0}};
            end
            gamma <= {{(M-1){1'b0}}, 1'b1};
            ell   <= {LW{1'b0}};
            r     <= 0;
            done  <= 1'b0;
        end else if (start) begin
            for (i = 0; i <= T; i = i + 1) begin
                lam[i] <= (i == 0) ? {{(M-1){1'b0}}, 1'b1} : {M{1'b0}};
                bee[i] <= (i == 0) ? {{(M-1){1'b0}}, 1'b1} : {M{1'b0}};
                win[i] <= {M{1'b0}};
            end
            // S_1 must already be in the window when iteration zero computes its
            // discrepancy, so start loads it and the enabled cycles feed S_2 on.
            win[0] <= syn_byte;
            gamma <= {{(M-1){1'b0}}, 1'b1};
            ell   <= {LW{1'b0}};
            r     <= 0;
            done  <= 1'b0;
        end else if (en && !done) begin
            // The window advances first in program order but this is a clocked
            // block, so every right-hand side reads the pre-edge value: the
            // discrepancy above used the window as it stands this cycle.
            win[0] <= syn_byte;
            for (i = 1; i <= T; i = i + 1) win[i] <= win[i-1];

            for (i = 0; i <= T; i = i + 1) lam[i] <= scaled_lam[i] ^ scaled_bee[i];

            if (lengthen) begin
                for (i = 0; i <= T; i = i + 1) bee[i] <= lam[i];
                gamma <= delta;
                ell   <= (r + 1'b1) - ell;
            end else begin
                bee[0] <= {M{1'b0}};
                for (i = 1; i <= T; i = i + 1) bee[i] <= bee[i-1];
            end

            if (r == 2*T - 1) done <= 1'b1;
            else              r <= r + 1'b1;
        end
    end

    assign deg = ell;

    generate
        for (j = 0; j <= T; j = j + 1) begin : flat
            assign lambda[M*j +: M] = lam[j];
        end
    endgenerate
endmodule

// Top level for area measurement: the solver alone, so the figure can be added
// to the syndrome and Chien numbers without overlap.
module bm_area_probe #(parameter T = 18, parameter M = 8,
                       parameter [M-1:0] RED = 8'h1D) (
    input  wire               clk,
    input  wire               rst_n,
    input  wire               start,
    input  wire               en,
    input  wire [M-1:0]       syn_byte,
    output wire [M*(T+1)-1:0] lambda,
    output wire               done
);
    wire [$clog2(T+2)-1:0] deg_unused;
    bm_solver #(.T(T), .M(M), .RED(RED)) s (
        .clk(clk), .rst_n(rst_n), .start(start), .en(en),
        .syn_byte(syn_byte), .lambda(lambda), .deg(deg_unused), .done(done)
    );
endmodule

`default_nettype wire
