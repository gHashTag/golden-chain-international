// Index-Based Syndrome Coding, reproduction side: the whole on-device cost of the
// pointer family's leakage story.
//
// The comparison this exists for. SLLC removes helper-data leakage by masking the
// redundancy with fresh response bits, and costs a degree-98 encoder plus an unmask -
// 4,745 square micrometres measured. IBS removes it differently: the helper data is a
// pointer to a position, and for i.i.d. bits a pointer says nothing about the value it
// points at. The question is what the pointer machinery costs against the masking
// machinery, and this is the pointer machinery.
//
// Reproduction is simply: for each codeword bit, read a pointer, count that many
// positions into the block, and take the bit there. One counter, one comparator, one
// register. Enrolment - scanning a block for a position that matches the wanted codeword
// bit and is reliable - happens off the die in a reverse fuzzy extractor and is not here.

`default_nettype none

module ibs_select #(
    parameter BLOCK = 4,                 // positions scanned per codeword bit
    parameter NBITS = 635,               // codeword bits to recover
    // Width of the pointer. A localparam would be tidier and cannot be used: a port
    // declaration may not reference an identifier declared in the body, and one
    // simulator accepted the tidier version while another rejected it - which is why
    // the area was nearly quoted for a module that never compiled.
    parameter PW = $clog2(BLOCK)   // BLOCK is at least 4 in every use here
) (
    input  wire                     clk,
    input  wire                     rst_n,
    input  wire                     start,
    input  wire                     resp_bit,      // response positions, in order
    input  wire                     resp_valid,
    input  wire [PW-1:0]            pointer,       // helper data for the current bit
    output reg                      code_bit,
    output reg                      code_valid,
    output reg                      done
);
    localparam CW = $clog2(NBITS + 1);

    // `within` is a SystemVerilog sequence keyword; yosys accepted it as an
    // identifier and iverilog did not, which is how a module that never compiled
    // came within one command of having its area quoted.
    reg [PW-1:0]  offset;        // position inside the current block
    reg [CW-1:0]  produced;      // codeword bits recovered so far

    always @(posedge clk) begin
        if (!rst_n || start) begin
            offset     <= {PW{1'b0}};
            produced   <= {CW{1'b0}};
            code_bit   <= 1'b0;
            code_valid <= 1'b0;
            done       <= 1'b0;
        end else begin
            code_valid <= 1'b0;
            if (resp_valid && !done) begin
                // the pointer names one position in this block; take it and ignore the
                // rest, which is the inefficiency the literature names and the reason
                // C-IBS exists
                if (offset == pointer) begin
                    code_bit   <= resp_bit;
                    code_valid <= 1'b1;
                end
                if (offset == BLOCK - 1) begin
                    offset <= {PW{1'b0}};
                    if (produced == NBITS - 1) done <= 1'b1;
                    else produced <= produced + 1'b1;
                end else begin
                    offset <= offset + 1'b1;
                end
            end
        end
    end
endmodule

`default_nettype wire
