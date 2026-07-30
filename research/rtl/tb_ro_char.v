// The instrument has to be checked like any other. Oscillators are modelled as
// square waves with known, distinct periods, so the expected count over the gate
// window is arithmetic rather than opinion.

`timescale 1ns/1ps
`default_nettype none

module tb_ro_char;
    localparam NRO  = 8;
    localparam CW   = 20;
    localparam GATE = 10;              // 1024 reference clocks per oscillator

    reg clk = 0, rst_n = 0, start = 0;
    reg [NRO-1:0] ro = 0;
    wire [CW-1:0] count;
    wire [2:0] index;
    wire valid, busy;

    ro_characteriser #(.NRO(NRO), .CW(CW), .GATE(GATE)) dut (
        .clk(clk), .rst_n(rst_n), .start(start), .ro(ro),
        .count(count), .index(index), .valid(valid), .busy(busy)
    );

    always #5 clk = ~clk;

    // Distinct periods in reference-clock cycles: the thing a PUF's uniqueness
    // rests on is that nominally identical oscillators differ, so the test drives
    // them deliberately close together as well as far apart.
    integer period [0:NRO-1];
    integer half   [0:NRO-1];
    integer tick   [0:NRO-1];
    integer i, fails, seen;
    integer got [0:NRO-1];

    initial begin
        // Even periods only. The first version of this testbench used consecutive
        // integers and half the oscillators silently collapsed onto their
        // neighbours, because a half-period is an integer number of reference
        // clocks and 5/2 is 2. Every failure in that run was in the test model
        // rather than in the circuit - which is the ordinary way an instrument
        // lies, and the reason this one is checked against arithmetic.
        period[0]=4;  period[1]=6;  period[2]=8;  period[3]=10;
        period[4]=12; period[5]=14; period[6]=16; period[7]=18;
        for (i = 0; i < NRO; i = i + 1) begin
            half[i] = period[i] / 2;
            tick[i] = 0;
            got[i]  = -1;
        end
    end

    // free-running oscillator models, in reference-clock time
    always @(posedge clk) begin
        for (i = 0; i < NRO; i = i + 1) begin
            tick[i] = tick[i] + 1;
            if (tick[i] >= half[i]) begin
                tick[i] = 0;
                ro[i]  <= ~ro[i];
            end
        end
    end

    always @(posedge clk) if (valid) got[index] = count;

    integer expect_lo, expect_hi;

    initial begin
        fails = 0;
        @(negedge clk); rst_n = 1;
        @(negedge clk); start = 1;
        @(negedge clk); start = 0;
        wait (!busy);
        repeat (4) @(negedge clk);

        $display("oscillator  period  counted  expected");
        seen = 0;
        for (i = 0; i < NRO; i = i + 1) begin
            // one rising edge per full period over the window, give or take the
            // partial period at each end and the synchroniser's stale samples
            expect_lo = (1 << GATE) / period[i] - 3;
            expect_hi = (1 << GATE) / period[i] + 3;
            $display("    %0d       %2d     %4d     %0d..%0d",
                     i, period[i], got[i], expect_lo, expect_hi);
            if (got[i] < 0) begin
                $display("FAIL: oscillator %0d never reported", i);
                fails = fails + 1;
            end else begin
                seen = seen + 1;
                if (got[i] < expect_lo || got[i] > expect_hi) begin
                    $display("FAIL: oscillator %0d counted %0d, expected %0d..%0d",
                             i, got[i], expect_lo, expect_hi);
                    fails = fails + 1;
                end
            end
        end
        if (seen !== NRO) begin
            $display("FAIL: %0d of %0d oscillators reported", seen, NRO);
            fails = fails + 1;
        end
        // The property the whole primitive rests on: a faster oscillator must
        // count higher. If the readout does not preserve the ordering it cannot
        // measure a comparison-based PUF at all.
        for (i = 1; i < NRO; i = i + 1)
            if (got[i-1] <= got[i]) begin
                $display("FAIL: ordering broken between %0d and %0d (%0d vs %0d)",
                         i-1, i, got[i-1], got[i]);
                fails = fails + 1;
            end

        if (fails == 0) $display("PASS ro_characteriser: %0d oscillators, counts and ordering", NRO);
        else            $display("FAILED ro_characteriser with %0d failures", fails);
        $finish;
    end
endmodule

`default_nettype wire
