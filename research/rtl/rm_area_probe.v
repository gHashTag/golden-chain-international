// The alternative the literature actually recommends for this exact problem, so
// that the choice between it and BCH rests on two numbers from the same library
// rather than on one number and a citation.
//
// Bosch, Guajardo, Sadeghi, Shokrollahi and Tuyls, "Efficient Helper Data Key
// Extractor on FPGAs", CHES 2008, set out to build a fuzzy extractor as small as
// possible - their stated reason being that the area belongs to the application,
// not to the key generator. They discard BCH on complexity grounds before
// implementing it, and their measured conclusion on a Spartan-3E is that a
// first-order Reed-Muller decoder is superior to Golay in area and, by their own
// error tables, in correction performance too. A concatenated construction - a
// short repetition code to bring the error rate down, then Reed-Muller - reaches
// a word error probability of about one in a million.
//
// This file decodes R(1,6): 64-bit codewords, 7 message bits, minimum distance
// 32, so fifteen errors correctable.
//
// Architecture: majority-logic decoding, serialised to one check per cycle. For
// first-order Reed-Muller the checks for message bit i are exactly the 2^(m-1)
// pairs of positions differing only in bit i, which makes each check a single XOR
// of two bits of the received word and the whole decoder a counter, a tally and
// two multiplexers. 448 cycles for a full decode. Key generation happens once at
// power-up, so cycles are the cheap resource here and area is the dear one - the
// trade every serial architecture makes, made in the direction this application
// wants.
//
// This is not the paper's own circuit. Theirs generates generator-matrix columns
// on the fly through a characteristic-vector generator, and reports FF = 2^m+6m-1
// with a few hundred gates besides. The structure below is the same idea reached
// by the pair-of-positions identity, which is simpler to verify and should land
// in the same neighbourhood. The testbench in tb_rm.v is what licenses quoting
// any area figure from it.

`default_nettype none

module rm_decoder #(parameter M = 6) (
    input  wire            clk,
    input  wire            rst_n,
    input  wire            start,
    input  wire [(1<<M)-1:0] rword,
    output reg  [M:0]      msg,      // msg[0] = u0, msg[i] = u_i
    output reg             done
);
    localparam N  = 1 << M;          // codeword length
    localparam H  = N >> 1;          // checks per variable
    localparam CW = $clog2(N);       // width of the position counter
    localparam TW = $clog2(N+1);     // width of the tally

    // The received word is stored inside the decoder rather than presented on a
    // port, because majority-logic decoding needs random access to it and a
    // comparison that left those 2^m flip-flops outside would flatter this design
    // against the BCH stages, which hold their own state.
    reg [N-1:0]    word;

    reg [CW-1:0]   x;                // position counter
    reg [$clog2(M+1)-1:0] v;         // which variable is being decoded
    reg [TW-1:0]   tally;
    reg            phase;            // 0: variables 1..m, 1: the constant term

    // Decoded message bits, shifted in rather than written at a computed index.
    // `u[v+1] <= ...` is legal and simulates correctly, but synthesis expands the
    // 32-bit index into a wide decoder whose upper bits have no driver - a
    // divergence between the circuit the testbench passed and the circuit being
    // measured. The variables are decoded in order, so a shift register carries
    // the same information with none of that: after M steps ubits[b] holds u_(b+1).
    reg [M-1:0]    ubits;
    reg            u0;

    // The two positions a check compares differ only in bit v. Reading the word
    // at two computed positions is the whole combinational cost of the design.
    wire [CW-1:0] partner = x ^ (1 << v);
    wire          bit_x   = word[x];
    wire          bit_p   = word[partner];
    wire          check   = bit_x ^ bit_p;
    wire          counts  = (x[v] == 1'b0);   // count each pair once

    // For the constant term: r[x] xor (u . x), the inner product over the
    // already-recovered message bits.
    reg  inner;
    integer b;
    always @* begin
        inner = 1'b0;
        for (b = 0; b < M; b = b + 1)
            if (x[b]) inner = inner ^ ubits[b];
    end
    wire const_check = bit_x ^ inner;

    always @(posedge clk) begin
        if (!rst_n || start) begin
            word  <= rword;
            x     <= {CW{1'b0}};
            v     <= 0;
            tally <= {TW{1'b0}};
            phase <= 1'b0;
            ubits <= {M{1'b0}};
            u0    <= 1'b0;
            msg   <= {(M+1){1'b0}};
            done  <= 1'b0;
        end else if (!done) begin
            if (phase == 1'b0) begin
                if (counts && check) tally <= tally + 1'b1;
                if (x == N - 1) begin
                    // Strict majority of H checks. Within the correction radius
                    // each error falsifies at most one check per variable, since
                    // the checks partition the positions into disjoint pairs -
                    // which is why H/2 is the right threshold and why a tie
                    // cannot occur for a correctable word.
                    ubits <= {((tally + ((counts && check) ? 1'b1 : 1'b0)) > (H >> 1)),
                              ubits[M-1:1]};
                    tally  <= {TW{1'b0}};
                    x      <= {CW{1'b0}};
                    if (v == M - 1) phase <= 1'b1;
                    else            v     <= v + 1'b1;
                end else begin
                    x <= x + 1'b1;
                end
            end else begin
                if (const_check) tally <= tally + 1'b1;
                if (x == N - 1) begin
                    u0   <= (tally + (const_check ? 1'b1 : 1'b0)) > (N >> 1);
                    msg  <= {ubits, (tally + (const_check ? 1'b1 : 1'b0)) > (N >> 1)};
                    done <= 1'b1;
                end else begin
                    x <= x + 1'b1;
                end
            end
        end
    end
endmodule

// The other half of the concatenated construction: an odd repetition code,
// decoded by majority. Included because the comparison should be against the
// whole scheme the paper recommends, not against its larger half alone.
module rep_decoder #(parameter R = 3) (
    input  wire         clk,
    input  wire         rst_n,
    input  wire         en,
    input  wire         bit_in,
    output reg          bit_out,
    output reg          valid
);
    localparam CW = $clog2(R+1);
    reg [CW-1:0] cnt, ones;
    always @(posedge clk) begin
        if (!rst_n) begin
            cnt <= 0; ones <= 0; bit_out <= 1'b0; valid <= 1'b0;
        end else if (en) begin
            if (cnt == R - 1) begin
                bit_out <= (ones + (bit_in ? 1'b1 : 1'b0)) > (R >> 1);
                valid   <= 1'b1;
                cnt     <= 0;
                ones    <= 0;
            end else begin
                ones  <= ones + (bit_in ? 1'b1 : 1'b0);
                cnt   <= cnt + 1'b1;
                valid <= 1'b0;
            end
        end
    end
endmodule

// Area top: both decoders of the concatenated construction.
module rm_area_probe #(parameter M = 6, parameter R = 3) (
    input  wire              clk,
    input  wire              rst_n,
    input  wire              start,
    input  wire [(1<<M)-1:0] rword,
    input  wire              rep_en,
    input  wire              rep_bit,
    output wire [M:0]        msg,
    output wire              done,
    output wire              rep_out,
    output wire              rep_valid
);
    rm_decoder #(.M(M)) rm (
        .clk(clk), .rst_n(rst_n), .start(start),
        .rword(rword), .msg(msg), .done(done)
    );
    rep_decoder #(.R(R)) rp (
        .clk(clk), .rst_n(rst_n), .en(rep_en), .bit_in(rep_bit),
        .bit_out(rep_out), .valid(rep_valid)
    );
endmodule

`default_nettype wire
