// GENERATED: Systematic Low Leakage Coding stages for BCH(127,29,21) over GF(2^7).
//
// The two things SLLC adds beyond the decoder already measured, so the cost of removing
// the n-k leakage term can be stated rather than assumed.
//
// Enrolment computes the systematic redundancy - the remainder of the information part
// times x^(n-k) modulo the generator - with a linear feedback shift register of degree
// 98, then exclusive-ors it with fresh response bits to form the helper data.
//
// Reconstruction only exclusive-ors the helper data with the noisy mask. That is the
// whole on-device addition if enrolment happens off the die, which is the arrangement a
// reverse fuzzy extractor uses.

`default_nettype none

module sllc_encoder (
    input  wire clk,
    input  wire rst_n,
    input  wire en,          // shift one information bit in, most significant first
    input  wire bit_in,
    output wire [97:0] parity
);
    reg [97:0] reg_lfsr;
    wire fb = bit_in ^ reg_lfsr[97];
    integer i;
    always @(posedge clk) begin
        if (!rst_n) reg_lfsr <= 98'b0;
        else if (en) begin
            reg_lfsr <= {reg_lfsr[96:0], 1'b0} ^ (98'b0
                | ({95'b0, fb, 2'b0})   // g[2]
                | ({94'b0, fb, 3'b0})   // g[3]
                | ({92'b0, fb, 5'b0})   // g[5]
                | ({91'b0, fb, 6'b0})   // g[6]
                | ({87'b0, fb, 10'b0})   // g[10]
                | ({86'b0, fb, 11'b0})   // g[11]
                | ({85'b0, fb, 12'b0})   // g[12]
                | ({84'b0, fb, 13'b0})   // g[13]
                | ({83'b0, fb, 14'b0})   // g[14]
                | ({82'b0, fb, 15'b0})   // g[15]
                | ({79'b0, fb, 18'b0})   // g[18]
                | ({74'b0, fb, 23'b0})   // g[23]
                | ({73'b0, fb, 24'b0})   // g[24]
                | ({67'b0, fb, 30'b0})   // g[30]
                | ({66'b0, fb, 31'b0})   // g[31]
                | ({64'b0, fb, 33'b0})   // g[33]
                | ({62'b0, fb, 35'b0})   // g[35]
                | ({61'b0, fb, 36'b0})   // g[36]
                | ({60'b0, fb, 37'b0})   // g[37]
                | ({59'b0, fb, 38'b0})   // g[38]
                | ({57'b0, fb, 40'b0})   // g[40]
                | ({56'b0, fb, 41'b0})   // g[41]
                | ({54'b0, fb, 43'b0})   // g[43]
                | ({53'b0, fb, 44'b0})   // g[44]
                | ({52'b0, fb, 45'b0})   // g[45]
                | ({51'b0, fb, 46'b0})   // g[46]
                | ({45'b0, fb, 52'b0})   // g[52]
                | ({44'b0, fb, 53'b0})   // g[53]
                | ({40'b0, fb, 57'b0})   // g[57]
                | ({39'b0, fb, 58'b0})   // g[58]
                | ({38'b0, fb, 59'b0})   // g[59]
                | ({36'b0, fb, 61'b0})   // g[61]
                | ({35'b0, fb, 62'b0})   // g[62]
                | ({34'b0, fb, 63'b0})   // g[63]
                | ({33'b0, fb, 64'b0})   // g[64]
                | ({32'b0, fb, 65'b0})   // g[65]
                | ({30'b0, fb, 67'b0})   // g[67]
                | ({29'b0, fb, 68'b0})   // g[68]
                | ({28'b0, fb, 69'b0})   // g[69]
                | ({27'b0, fb, 70'b0})   // g[70]
                | ({25'b0, fb, 72'b0})   // g[72]
                | ({21'b0, fb, 76'b0})   // g[76]
                | ({20'b0, fb, 77'b0})   // g[77]
                | ({17'b0, fb, 80'b0})   // g[80]
                | ({14'b0, fb, 83'b0})   // g[83]
                | ({13'b0, fb, 84'b0})   // g[84]
                | ({10'b0, fb, 87'b0})   // g[87]
                | ({7'b0, fb, 90'b0})   // g[90]
                | ({6'b0, fb, 91'b0})   // g[91]

                | {97'b0, fb});
        end
    end
    assign parity = reg_lfsr;
endmodule

// Reconstruction side: the helper data is unmasked with the noisy response bits. This is
// the entire on-device cost of SLLC when enrolment is done off the die.
module sllc_unmask (
    input  wire [97:0] helper,
    input  wire [97:0] mask_noisy,
    output wire [97:0] redundancy
);
    assign redundancy = helper ^ mask_noisy;
endmodule

`default_nettype wire
