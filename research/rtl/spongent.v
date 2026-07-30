// GENERATED: SPONGENT-88/80/8 permutation, the diffusion primitive the helper-data
// manipulation countermeasure needs. b=88, rate 8, 45 rounds.
//
// Written because the countermeasure's cost was the last figure in this project taken from
// a paper rather than measured here - 85 slices on a Spartan-3E, which is a different
// process and a different technology. The countermeasure is now load-bearing: it is what
// makes the code choice independent of helper-data manipulation, so its cost should not be
// borrowed.
//
// What is verified here and what is not. The S-box and the bit permutation are each checked
// to be bijections at generation time, and the testbench checks avalanche - one input bit
// changing about half the output bits - which is the property the countermeasure actually
// relies on. There are no official test vectors in hand, so this is not verified to be
// SPONGENT rather than a SPONGENT-shaped permutation of the same cost. The area figure is
// what it is measured for.

`default_nettype none

module spongent_round (
    input  wire [87:0] state_in,
    input  wire [5:0]     lcounter,
    output wire [87:0] state_out
);
    function [3:0] sbox(input [3:0] x);
        case (x)
            4'd0: sbox = 4'hC;
            4'd1: sbox = 4'h5;
            4'd2: sbox = 4'h6;
            4'd3: sbox = 4'hB;
            4'd4: sbox = 4'h9;
            4'd5: sbox = 4'h0;
            4'd6: sbox = 4'hA;
            4'd7: sbox = 4'hD;
            4'd8: sbox = 4'h3;
            4'd9: sbox = 4'hE;
            4'd10: sbox = 4'hF;
            4'd11: sbox = 4'h8;
            4'd12: sbox = 4'h4;
            4'd13: sbox = 4'h7;
            4'd14: sbox = 4'h1;
            4'd15: sbox = 4'h2;
        endcase
    endfunction

    // round constant into the low bits, its reverse into the high bits
    wire [5:0] rev = {lcounter[0], lcounter[1], lcounter[2],
                       lcounter[3], lcounter[4], lcounter[5]};
    wire [87:0] c = state_in ^ {{82{1'b0}}, lcounter}
                                ^ {rev, {82{1'b0}}};

    reg [87:0] s;
    integer i;
    always @* begin
        for (i = 0; i < 22; i = i + 1)
            s[4*i +: 4] = sbox(c[4*i +: 4]);
    end

    reg [87:0] p;
    always @* begin
        p[0] = s[0];
        p[22] = s[1];
        p[44] = s[2];
        p[66] = s[3];
        p[1] = s[4];
        p[23] = s[5];
        p[45] = s[6];
        p[67] = s[7];
        p[2] = s[8];
        p[24] = s[9];
        p[46] = s[10];
        p[68] = s[11];
        p[3] = s[12];
        p[25] = s[13];
        p[47] = s[14];
        p[69] = s[15];
        p[4] = s[16];
        p[26] = s[17];
        p[48] = s[18];
        p[70] = s[19];
        p[5] = s[20];
        p[27] = s[21];
        p[49] = s[22];
        p[71] = s[23];
        p[6] = s[24];
        p[28] = s[25];
        p[50] = s[26];
        p[72] = s[27];
        p[7] = s[28];
        p[29] = s[29];
        p[51] = s[30];
        p[73] = s[31];
        p[8] = s[32];
        p[30] = s[33];
        p[52] = s[34];
        p[74] = s[35];
        p[9] = s[36];
        p[31] = s[37];
        p[53] = s[38];
        p[75] = s[39];
        p[10] = s[40];
        p[32] = s[41];
        p[54] = s[42];
        p[76] = s[43];
        p[11] = s[44];
        p[33] = s[45];
        p[55] = s[46];
        p[77] = s[47];
        p[12] = s[48];
        p[34] = s[49];
        p[56] = s[50];
        p[78] = s[51];
        p[13] = s[52];
        p[35] = s[53];
        p[57] = s[54];
        p[79] = s[55];
        p[14] = s[56];
        p[36] = s[57];
        p[58] = s[58];
        p[80] = s[59];
        p[15] = s[60];
        p[37] = s[61];
        p[59] = s[62];
        p[81] = s[63];
        p[16] = s[64];
        p[38] = s[65];
        p[60] = s[66];
        p[82] = s[67];
        p[17] = s[68];
        p[39] = s[69];
        p[61] = s[70];
        p[83] = s[71];
        p[18] = s[72];
        p[40] = s[73];
        p[62] = s[74];
        p[84] = s[75];
        p[19] = s[76];
        p[41] = s[77];
        p[63] = s[78];
        p[85] = s[79];
        p[20] = s[80];
        p[42] = s[81];
        p[64] = s[82];
        p[86] = s[83];
        p[21] = s[84];
        p[43] = s[85];
        p[65] = s[86];
        p[87] = s[87];
    end
    assign state_out = p;
endmodule

// The full permutation, one round per clock, plus the counter that drives it.
module spongent_permutation (
    input  wire            clk,
    input  wire            rst_n,
    input  wire            start,
    input  wire [87:0]  data_in,
    output reg  [87:0]  state,
    output reg             done
);
    reg [5:0] lc;
    reg [5:0] round;
    wire [87:0] next;
    spongent_round r (.state_in(state), .lcounter(lc), .state_out(next));

    // six-bit counter, x^6 + x^5 + 1, seeded as the specification requires
    wire lc_fb = lc[5] ^ lc[4];
    always @(posedge clk) begin
        if (!rst_n || start) begin
            state <= data_in;
            lc    <= 6'h05;
            round <= 6'd0;
            done  <= 1'b0;
        end else if (!done) begin
            state <= next;
            lc    <= {lc[4:0], lc_fb};
            if (round == 45 - 1) done <= 1'b1;
            else                       round <= round + 1'b1;
        end
    end
endmodule

`default_nettype wire
