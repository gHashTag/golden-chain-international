// Area probe for the error-correction stage of a PUF fuzzy extractor.
//
// Parameters chosen to match a realistic construction: BCH(255,131) over GF(2^8),
// correcting t=18 errors, which is the order published designs use for PUF key
// generation. Primitive polynomial x^8+x^4+x^3+x^2+1 (0x11D).
//
// This implements the two area-dominant stages - syndrome computation and Chien
// search - which between them carry the GF(2^8) arithmetic. The key-equation
// solver (Berlekamp-Massey) is deliberately NOT here; it is reported separately,
// because writing an unverified BM in one pass and calling the result measured
// would be worse than saying which part is measured and which is not.

`default_nettype none

// GF(2^8) multiply by a compile-time constant. Cheap: XOR tree, no logic depth
// worth speaking of. This is what makes syndrome accumulators affordable.
module gf_mul_const #(parameter [7:0] C = 8'h02) (
    input  wire [7:0] a,
    output wire [7:0] y
);
    function [7:0] xtime(input [7:0] v);
        xtime = (v[7]) ? ((v << 1) ^ 8'h1D) : (v << 1);
    endfunction

    reg [7:0] acc, cur;
    integer i;
    always @* begin
        acc = 8'h00;
        cur = a;
        for (i = 0; i < 8; i = i + 1) begin
            if (C[i]) acc = acc ^ cur;
            cur = xtime(cur);
        end
    end
    assign y = acc;
endmodule

// One syndrome accumulator: S_j <= S_j * alpha^j + bit. Serial over 255 bits.
module syndrome_acc #(parameter [7:0] ALPHA_J = 8'h02) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       en,
    input  wire       bit_in,
    output reg  [7:0] s
);
    wire [7:0] scaled;
    gf_mul_const #(.C(ALPHA_J)) m (.a(s), .y(scaled));

    always @(posedge clk) begin
        if (!rst_n)     s <= 8'h00;
        else if (en)    s <= scaled ^ {7'b0, bit_in};
    end
endmodule

// Syndrome bank: 2t accumulators, one per power of alpha. This is the stage that
// consumes the received word, and it is where most of the GF arithmetic lives.
module syndrome_bank #(parameter T = 18) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        en,
    input  wire        bit_in,
    output wire [8*2*T-1:0] syn
);
    // alpha^j for j = 1 .. 2t, precomputed in GF(2^8) with 0x11D.
    localparam [8*36-1:0] ALPHAS = {
        8'hE7,8'h8F,8'hC5,8'h91,8'h3B,8'h9D,8'h4C,8'h26,8'h13,8'h8A,8'h45,8'hAE,
        8'h57,8'hA0,8'h50,8'h28,8'h14,8'h0A,8'h05,8'h8E,8'h47,8'hAD,8'hDE,8'h6F,
        8'hB6,8'h5B,8'h9E,8'h4F,8'hAF,8'hDF,8'hEF,8'hFF,8'hF7,8'hFB,8'hFD,8'hFE
    };
    genvar j;
    generate
        for (j = 0; j < 2*T; j = j + 1) begin : bank
            syndrome_acc #(.ALPHA_J(ALPHAS[8*j +: 8])) a (
                .clk(clk), .rst_n(rst_n), .en(en), .bit_in(bit_in),
                .s(syn[8*j +: 8])
            );
        end
    endgenerate
endmodule

// Chien search: evaluate the error locator at each of n positions, one per cycle.
// t multipliers by fixed powers of alpha, plus a wide XOR to test for zero.
module chien #(parameter T = 18) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        start,
    input  wire [8*T-1:0] lambda,
    output wire        root_found
);
    reg [8*T-1:0] acc;
    wire [8*T-1:0] stepped;

    localparam [8*18-1:0] APOW = {
        8'h13,8'h8A,8'h45,8'hAE,8'h57,8'hA0,8'h50,8'h28,8'h14,
        8'h0A,8'h05,8'h8E,8'h47,8'hAD,8'hDE,8'h6F,8'hB6,8'h02
    };

    genvar i;
    generate
        for (i = 0; i < T; i = i + 1) begin : mults
            gf_mul_const #(.C(APOW[8*i +: 8])) m (
                .a(acc[8*i +: 8]), .y(stepped[8*i +: 8])
            );
        end
    endgenerate

    always @(posedge clk) begin
        if (!rst_n)      acc <= {(8*T){1'b0}};
        else if (start)  acc <= lambda;
        else             acc <= stepped;
    end

    // Sum all terms in GF(2^8) - XOR - and flag a root when the sum is zero.
    reg [7:0] sum;
    integer k;
    always @* begin
        sum = 8'h00;
        for (k = 0; k < T; k = k + 1) sum = sum ^ acc[8*k +: 8];
    end
    assign root_found = (sum == 8'h00);
endmodule

// Top: the two measured stages wired together.
module bch_area_probe #(parameter T = 18) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        en,
    input  wire        bit_in,
    input  wire        chien_start,
    input  wire [8*T-1:0] lambda,
    output wire [8*2*T-1:0] syn,
    output wire        root_found
);
    syndrome_bank #(.T(T)) sb (
        .clk(clk), .rst_n(rst_n), .en(en), .bit_in(bit_in), .syn(syn)
    );
    chien #(.T(T)) cs (
        .clk(clk), .rst_n(rst_n), .start(chien_start),
        .lambda(lambda), .root_found(root_found)
    );
endmodule

`default_nettype wire
