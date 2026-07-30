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

// GENERATED for GF(2^7), x^7+x^3+1 (0x89), t=27 - the code that satisfies the
// leakage, error and area constraints together. See research/code_choice_model.py.

// GF(2^8) multiply by a compile-time constant. Cheap: XOR tree, no logic depth
// worth speaking of. This is what makes syndrome accumulators affordable.
module gf_mul_const #(parameter [6:0] C = 7'h02) (
    input  wire [6:0] a,
    output wire [6:0] y
);
    function [6:0] xtime(input [6:0] v);
        xtime = (v[6]) ? ((v << 1) ^ 7'h09) : (v << 1);
    endfunction

    reg [6:0] acc, cur;
    integer i;
    always @* begin
        acc = 7'h00;
        cur = a;
        for (i = 0; i < 7; i = i + 1) begin
            if (C[i]) acc = acc ^ cur;
            cur = xtime(cur);
        end
    end
    assign y = acc;
endmodule

// One syndrome accumulator: S_j <= S_j * alpha^j + bit. Serial over 255 bits.
module syndrome_acc #(parameter [6:0] ALPHA_J = 8'h02) (
    input  wire       clk,
    input  wire       rst_n,
    input  wire       en,
    input  wire       bit_in,
    output reg  [6:0] s
);
    wire [6:0] scaled;
    gf_mul_const #(.C(ALPHA_J)) m (.a(s), .y(scaled));

    always @(posedge clk) begin
        if (!rst_n)     s <= 7'h00;
        else if (en)    s <= scaled ^ {6'b0, bit_in};
    end
endmodule

// Syndrome bank: 2t accumulators, one per power of alpha. This is the stage that
// consumes the received word, and it is where most of the GF arithmetic lives.
module syndrome_bank #(parameter T = 27) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        en,
    input  wire        bit_in,
    output wire [7*2*T-1:0] syn
);
    // alpha^j for j = 1 .. 2t, precomputed in GF(2^8) with 0x11D.
    localparam [7*54-1:0] ALPHAS = {
        7'h71,7'h7C,7'h3E,7'h1F,7'h4B,7'h61,7'h74,7'h3A,7'h1D,7'h4A,7'h25,7'h56,7'h2B,7'h51,7'h6C,7'h36,7'h1B,7'h49,7'h60,7'h30,7'h18,7'h0C,7'h06,7'h03,7'h45,7'h66,7'h33,7'h5D,7'h6A,7'h35,7'h5E,7'h2F,7'h53,7'h6D,7'h72,7'h39,7'h58,7'h2C,7'h16,7'h0B,7'h41,7'h64,7'h32,7'h19,7'h48,7'h24,7'h12,7'h09,7'h40,7'h20,7'h10,7'h08,7'h04,7'h02
    };
    genvar j;
    generate
        for (j = 0; j < 2*T; j = j + 1) begin : bank
            syndrome_acc #(.ALPHA_J(ALPHAS[7*j +: 7])) a (
                .clk(clk), .rst_n(rst_n), .en(en), .bit_in(bit_in),
                .s(syn[7*j +: 7])
            );
        end
    endgenerate
endmodule

// Chien search: evaluate the error locator at each of n positions, one per cycle.
// t multipliers by fixed powers of alpha, plus a wide XOR to test for zero.
module chien #(parameter T = 27) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        start,
    input  wire [7*T-1:0] lambda,
    output wire        root_found
);
    reg [7*T-1:0] acc;
    wire [7*T-1:0] stepped;

    localparam [7*27-1:0] APOW = {
        7'h5D,7'h6A,7'h35,7'h5E,7'h2F,7'h53,7'h6D,7'h72,7'h39,7'h58,7'h2C,7'h16,7'h0B,7'h41,7'h64,7'h32,7'h19,7'h48,7'h24,7'h12,7'h09,7'h40,7'h20,7'h10,7'h08,7'h04,7'h02
    };

    genvar i;
    generate
        for (i = 0; i < T; i = i + 1) begin : mults
            gf_mul_const #(.C(APOW[7*i +: 7])) m (
                .a(acc[7*i +: 7]), .y(stepped[7*i +: 7])
            );
        end
    endgenerate

    always @(posedge clk) begin
        if (!rst_n)      acc <= {(7*T){1'b0}};
        else if (start)  acc <= lambda;
        else             acc <= stepped;
    end

    // Sum all terms in GF(2^8) - XOR - and flag a root when the sum is zero.
    reg [6:0] sum;
    integer k;
    always @* begin
        sum = 7'h00;
        for (k = 0; k < T; k = k + 1) sum = sum ^ acc[7*k +: 7];
    end
    assign root_found = (sum == 7'h00);
endmodule

// Top: the two measured stages wired together.
module bch_area_probe #(parameter T = 27) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        en,
    input  wire        bit_in,
    input  wire        chien_start,
    input  wire [7*T-1:0] lambda,
    output wire [7*2*T-1:0] syn,
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
