// Chien search with its multipliers shared, the same trade the solver took.
//
// The parallel form holds t+1 running products and steps every one of them each cycle,
// which is t+1 constant multipliers - 22 at t=21, measured at 8,906 square micrometres of
// which 65 percent is that logic. The registers are irreducible: t+1 coefficients have to
// be held. The multipliers are not.
//
// Serialised: one general multiplier, stepping one coefficient per cycle, so t+1 cycles per
// codeword position and (t+1)*n over the sweep - 2,794 at t=21, n=127. At ten megahertz
// that is 279 microseconds, once, alongside the solver's 185.
//
// Note the multiplier has to be general here where the parallel form's were constant: each
// lane is multiplied by a different power of alpha, and sharing one multiplier across lanes
// means the multiplicand changes every cycle. That is why the saving is smaller than the
// solver's - a general multiplier costs more than the constant one it replaces, and only
// the replication is saved.

`default_nettype none

module chien_serial #(
    parameter T = 21,
    parameter M = 7,
    parameter [M-1:0] RED = 7'h09,
    parameter NPOS = 127
) (
    input  wire                   clk,
    input  wire                   rst_n,
    input  wire                   start,
    input  wire [M*(T+1)-1:0]     lambda,
    input  wire [M*(T+1)-1:0]     alpha_pow,   // alpha^k for k = 0..t
    output reg  [$clog2(NPOS)-1:0] position,
    output reg                    root,
    output reg                    root_valid,
    output reg                    done
);
    localparam KW = $clog2(T+2);
    localparam PW = $clog2(NPOS);

    reg [M-1:0] q [0:T];
    reg [KW-1:0] k;
    reg [M-1:0]  acc;
    reg [PW-1:0] pos;

    wire [M-1:0] a = q[k];
    wire [M-1:0] b = alpha_pow[M*k +: M];
    wire [M-1:0] p;
    gf_mul #(.M(M), .RED(RED)) mul (.a(a), .b(b), .y(p));

    integer i;
    always @(posedge clk) begin
        if (!rst_n || start) begin
            for (i = 0; i <= T; i = i + 1) q[i] <= lambda[M*i +: M];
            k          <= {KW{1'b0}};
            acc        <= {M{1'b0}};
            pos        <= {PW{1'b0}};
            root       <= 1'b0;
            root_valid <= 1'b0;
            position   <= {PW{1'b0}};
            done       <= 1'b0;
        end else if (!done) begin
            root_valid <= 1'b0;
            // sum the current lane into the accumulator, then step it for the next position
            acc  <= (k == 0) ? q[0] : (acc ^ q[k]);
            q[k] <= p;
            if (k == T) begin
                // the whole polynomial has been summed for this position
                root       <= ((acc ^ q[T]) == {M{1'b0}});
                position   <= (pos == 0) ? {PW{1'b0}} : (NPOS[PW-1:0] - pos);
                root_valid <= 1'b1;
                k          <= {KW{1'b0}};
                acc        <= {M{1'b0}};
                if (pos == NPOS - 1) done <= 1'b1;
                else                 pos  <= pos + 1'b1;
            end else begin
                k <= k + 1'b1;
            end
        end
    end
endmodule

`default_nettype wire
