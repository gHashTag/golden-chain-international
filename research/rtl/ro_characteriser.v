// Characterisation structure for the identity root: measures the three quantities
// every remaining open question depends on, and measures none of them through a
// decision made at design time.
//
// Why raw counts and not response bits. A ring-oscillator PUF produces a response
// bit by comparing two oscillator frequencies, so a structure that emits response
// bits can only report the error rate of the pairing wired into it. The bias, the
// entropy per oscillator, and whether reuse across pairs degrades extraction all
// depend on which pairs are chosen, and choosing them in silicon means the
// measurement cannot answer the question it was built for. That is the broken-ruler
// error: diagnosing through a signal that sits inside the decision under test.
//
// So this emits one frequency count per oscillator per sweep. Everything else -
// pairing, thresholds for discarding close pairs, bias, error rate across
// temperature, entropy under any pairing scheme - is computed afterwards from the
// counts, off the die, and can be recomputed when the question changes.
//
// What it does not contain. No comparator, no arbiter, no response register, no
// helper data, no key. It is an instrument, not a key generator, and it should never
// be shipped in a part that holds a secret: raw counts are exactly what an attacker
// wants and exactly what a key generator must never expose.

`default_nettype none

module ro_characteriser #(
    parameter NRO   = 16,      // oscillators in the bank
    parameter CW    = 20,      // counter width
    parameter GATE  = 16       // gate window is 2^GATE reference clocks
) (
    input  wire                   clk,      // reference clock
    input  wire                   rst_n,
    input  wire                   start,    // begin a sweep of the whole bank
    input  wire [NRO-1:0]         ro,       // oscillator outputs, asynchronous
    output reg  [CW-1:0]          count,    // frequency count for `index`
    output reg  [$clog2(NRO)-1:0] index,    // which oscillator `count` belongs to
    output reg                    valid,    // one cycle per completed count
    output reg                    busy
);
    localparam SW = $clog2(NRO);

    reg [SW-1:0]   sel;
    reg [GATE:0]   window;
    reg [CW-1:0]   acc;

    // Two-stage synchroniser on the selected oscillator. The oscillators run in
    // their own time, so sampling one directly into the counting logic would put a
    // metastable value into an adder and corrupt the very number being measured.
    reg sync0, sync1, sync2;
    always @(posedge clk) begin
        sync0 <= ro[sel];
        sync1 <= sync0;
        sync2 <= sync1;
    end
    wire rise = sync1 & ~sync2;

    // Switching `sel` at a window boundary leaves two stale samples in the
    // synchroniser, so at most one spurious edge can be attributed to each
    // oscillator after the first. Against a 2^GATE window that is below the
    // measurement noise and is left uncorrected; it is recorded here rather than
    // discovered later, because a systematic offset of one count would otherwise
    // look like a real frequency difference between neighbouring oscillators.

    // Counting rising edges of a signal sampled at the reference clock measures the
    // oscillator's frequency only if it is slower than half the reference. A real
    // bank runs far faster, so in silicon the oscillator drives a small prescaler
    // first; the prescaler is not modelled here because it does not change what is
    // being read out, only the scale factor applied afterwards.
    always @(posedge clk) begin
        if (!rst_n) begin
            sel    <= {SW{1'b0}};
            window <= {(GATE+1){1'b0}};
            acc    <= {CW{1'b0}};
            count  <= {CW{1'b0}};
            index  <= {SW{1'b0}};
            valid  <= 1'b0;
            busy   <= 1'b0;
        end else if (start) begin
            sel    <= {SW{1'b0}};
            window <= {(GATE+1){1'b0}};
            acc    <= {CW{1'b0}};
            valid  <= 1'b0;
            busy   <= 1'b1;
        end else if (busy) begin
            valid <= 1'b0;
            if (window == (1 << GATE) - 1) begin
                // Window closed: publish this oscillator's count and move on. The
                // edge arriving on this very cycle still belongs to this window.
                count  <= acc + (rise ? 1'b1 : 1'b0);
                index  <= sel;
                valid  <= 1'b1;
                acc    <= {CW{1'b0}};
                window <= {(GATE+1){1'b0}};
                if (sel == NRO - 1) busy <= 1'b0;
                else                sel  <= sel + 1'b1;
            end else begin
                if (rise) acc <= acc + 1'b1;
                window <= window + 1'b1;
            end
        end else begin
            valid <= 1'b0;
        end
    end
endmodule

`default_nettype wire
