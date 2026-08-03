# four-k-tv — script

**Segment:** STILL CHEAP · **Verdict:** STILL CHEAP · **Words:** 109 · **Read @150wpm:** ~44s

> Numerals are spelled as spoken per `docs/08-voice-casting.md` §5.1 (the VO script contains no
> numerals, ever). Unit ("dollars") is spoken on the first figure only, then dropped. Years read
> as "twenty sixteen". The ARTIFACT beat is the selected hook, wording unchanged — only the
> figures are respelled, which §5.1 requires and does not treat as a rewrite.

---

**[ARTIFACT 0:00–0:03]**
Nine sixty-seven fifty-eight dollars, in today's money. That's VIZIO's cheapest fifty-five-inch
four-K TV, twenty sixteen. It's three nineteen ninety-six now.

**[GAP 0:03–0:08]**
[PAUSE] Same size. Same resolution. Entry line to entry line.

**[EXCAVATION 0:08–0:26]**
The receipt: VIZIO's own press release, April nineteenth. Six ninety-nine ninety-nine, MSRP.
[EMPHASIS] Panel makers built more capacity than the market bought.
VIZIO's SEC filing names the mechanism: a capacity surge. Then retailers force prices down.
Chinese fabs supplied that surge.
Constant quality, BLS: televisions down seventy-six point two percent after inflation.

**[VERDICT 0:26–0:36]**
One asterisk: twenty sixteen is a launch price, today's a shelf price.
Verdict: [PAUSE] still cheap. And today's set is QLED, with HDR.

**[HANDOFF 0:36–0:42]**
What did your first four-K TV cost?

---

## Source map

Every spoken figure and every causal assertion maps to a row. `compliance-officer` checks the
script against this table; an unmapped claim is an automatic C2 failure.

| # | Line as spoken | Claim ID | Sources backing it |
|---|---|---|---|
| 1 | "Nine sixty-seven fifty-eight dollars, in today's money" ($967.58) | `c1-2016-entry-55in-4k` (`inflation_adjusted_value`) | VIZIO press release 19 Apr 2016 (primary) + BLS CPI-U `CUUR0000SA0`, Apr 2016 239.261 → Jul 2026 330.724, deflator 1.382273 (primary) |
| 2 | "VIZIO's cheapest fifty-five-inch four-K TV, twenty sixteen" | `c1-2016-entry-55in-4k` (`text`) | VIZIO press release 19 Apr 2016 (primary) + Reviewed.com 19 Apr 2016 (secondary) |
| 3 | "It's three nineteen ninety-six now" ($319.96) | `c2-2026-entry-55in-4k` | P.C. Richard & Son live listing, 3 Aug 2026 (primary) + us.tcl.com official store $319.99 (primary) |
| 4 | "Same size. Same resolution. Entry line to entry line." | `spec_note` (the four held axes) + `c1` / `c2` | Both listings state 55-inch class and 3840×2160 / "4K Ultra HD (2160p)"; both are the maker's entry 4K line |
| 5 | "VIZIO's own press release, April nineteenth" | `c1` source 1 | Dateline read in the release: "IRVINE, Calif., April 19, 2016 /PRNewswire/" (primary) |
| 6 | "Six ninety-nine ninety-nine, MSRP" ($699.99) | `c1-2016-entry-55in-4k` (`value`) | VIZIO press release line "E55u-D0 MSRP $699.99" (primary) + Reviewed.com price breakdown (secondary) |
| 7 | "Panel makers built more capacity than the market bought" — **THE ONE CAUSE** | `primary_cause` (`mechanism: manufacturing-scale`) | VIZIO 10-K FY2023, SEC EDGAR (primary) + TrendForce, 3 Jan 2024 (secondary) |
| 8 | "VIZIO's SEC filing names the mechanism: a capacity surge. Then retailers force prices down." | `primary_cause` source 1 | VIZIO 10-K FY2023: "resulting in a surge in production capacity. During these surges in capacity, retailers can exert strong downward pricing pressure, resulting in sharp declines in prices" (primary) |
| 9 | "Chinese fabs supplied that surge" | `primary_cause` source 2 | TrendForce 3 Jan 2024: "the massive expansion of Chinese panel production capacity"; "the current surplus in TV panel production capacity" (secondary) |
| 10 | "Constant quality, BLS: televisions down seventy-six point two percent after inflation" | `c5-bls-constant-quality-televisions` | BLS `CUUR0000SERA01` Apr 2016 283.408 → Jul 2026 93.176 (primary) + BLS `CUUR0000SA0` as deflator (primary). Real change = (93.176/283.408)/(330.724/239.261) − 1 = −76.2% |
| 11 | "twenty sixteen is a launch price, today's a shelf price" | `spec_note` asterisk (1) | Stated concession, not a new figure: `c1` is a manufacturer MSRP at announcement, `c2` is a live retail price |
| 12 | "today's set is QLED, with HDR" | `c2` sources 1–2 | P.C. Richard listing "Panel Type: QLED"; us.tcl.com product title "Q Class 4K UHD HDR QLED Smart TV with Google TV" (both primary) |
| 13 | "What did your first four-K TV cost?" | — | Comment question, no factual content |

### Not spoken, carried on screen only

`c3-2016-premium-55in-4k-led` ($1,799 LG 55UH7700) and `c4-2026-premium-55in-4k-led` ($1,297.99
Samsung QN55QN90F) are the tier-matched anti-cherry-pick check. They belong on the chart, not in
the read — speaking a second tier would break the one-cause discipline and the word budget. No
figure from either claim appears in the narration.

### Notes for downstream agents

- **Handoff is the comment question, not the affiliate line** (beat sheet: never both). Affiliate
  is not live — `docs/01-strategy.md` §ladder puts YouTube Shopping at months 3–6 behind 10k
  subs. Speaking an affiliate line before the shelf exists would be a claim we cannot honour.
- **No "cheapest it has ever been" claim.** The bible's STILL CHEAP close suggests it, but the
  evidence pack does not establish an all-time low — it establishes a 2016-vs-2026 pair and a
  constant-quality index. An honest gap beats a plausible guess, so the line is not in the script.
- **Discrepancy flagged in `evidence.json`:** claim `c5` has `inflation_adjusted_value: 67.4`,
  which does not match its own `text` ("76.2% after general inflation") or the arithmetic in its
  primary source quote (−76.2%). The script speaks **76.2%**, the figure the quoted BLS values
  actually produce. `trend-archaeologist` should reconcile the field.
- **[PAUSE] count is two**, both load-bearing: after the 2026 figure (bible §3, GAP holds one full
  beat) and after "Verdict:" (voice-casting §4.2 Gate 5 — the colon must be audible as a gap).
