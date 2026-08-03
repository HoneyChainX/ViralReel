# four-k-tv — script v3 (STORYLINE cut)

**Segment:** STILL CHEAP · **Verdict:** STILL CHEAP · **Words:** 93 · **Sentences:** 22 · **[PAUSE] marks:** 7
**Read @~140wpm natural:** ~40s speech + ~4s of pauses ≈ **44s** — inside the 45s cap without rushing.

> Numerals are spelled as spoken per `docs/08-voice-casting.md` §5.1 — the VO script contains no
> numerals, ever. Compressed retail read below $1,000 (§5.2). Unit ("dollars") spoken on the first
> figure only, then dropped. Years read as "twenty sixteen". Percentages never compressed.
> Numerals live on screen and in `evidence.json`, not in this read.

> **v3 brief (founder):** same spine — number-first cold open, one cause, verdict stamp, handoff —
> with an emotional arc on top: scene, mini-mystery, human stake, proof flex, serial kicker.
> Word band tightened to 85–95 so the read breathes at ~140wpm with real pauses.

---

**[ARTIFACT 0:00–0:09]** — *the drop-in: April 2016, felt, then the number*
Twenty sixteen. April. A wall of brand-new four-K TVs. [PAUSE] VIZIO's cheapest fifty-five
inch: nine sixty-seven fifty-eight dollars, in today's money.

**[GAP 0:09–0:16]** — *the odometer moment: the collapse, watched*
Watch it fall. [PAUSE] Three nineteen ninety-six. [PAUSE] Same size. Same resolution. Same tier.

**[EXCAVATION 0:16–0:28]** — *mini-mystery, then the ONE cause, then the human stake*
Almost everything got more expensive. [EMPHASIS] This didn't. [PAUSE] Why?
One reason: panel factories outbuilt the market.
The glut ran so deep, Korean panel makers left the business.

**[PROOF FLEX 0:28–0:37]** — *two independent methods, same answer*
Our receipts: down sixty-six point nine percent, after inflation.
BLS's television index: sixty-seven point one. [PAUSE] Two methods. Point two apart.

**[VERDICT 0:37–0:39]** — *flat delivery, stamp lands on the same frame*
Verdict: [PAUSE] still cheap.

**[HANDOFF 0:39–0:44]** — *serial kicker: tease the next dig, explain nothing*
One catch. [PAUSE] Why it's this cheap costs you something else. Next dig.

---

## Source map

Every spoken figure and every causal assertion maps to a row in
`content/episodes/four-k-tv/evidence.json`. `compliance-officer` checks the script against this
table; an unmapped claim is an automatic C2 failure.

| # | Line as spoken | Claim ID | Sources backing it |
|---|---|---|---|
| 1 | "Twenty sixteen. April." | `c1-2016-entry-55in-4k` (`year`, source 1 dateline) | VIZIO press release dateline: "IRVINE, Calif., April 19, 2016 /PRNewswire/" (primary) |
| 2 | "A wall of brand-new four-K TVs." | — scene-setting, no factual claim | Visual beat only. Generated imagery here must be STYLIZED AND OBVIOUSLY NON-DOCUMENTARY (docs/05-compliance.md Rule 6, adapted) — never a fake 2016 storefront or fake archival footage. Real period texture, if wanted, comes from `footage_candidates` (all PD/CC0/CC-BY-SA) |
| 3 | "VIZIO's cheapest four-K fifty-five inch: nine sixty-seven fifty-eight dollars, in today's money" ($967.58) | `c1-2016-entry-55in-4k` (`inflation_adjusted_value`, `text`) | VIZIO press release 19 Apr 2016, E55u-D0 MSRP $699.99 (primary) + Reviewed.com 19 Apr 2016 (secondary) + BLS CPI-U `CUUR0000SA0`: Apr 2016 239.261 → Jul 2026 330.724, deflator 1.382273; 699.99 × 1.382273 = 967.58 (primary) |
| 4 | "Watch it fall. Three nineteen ninety-six" ($319.96 — the `<PriceOdometer>` rolls 967.58 → 319.96 through the two pauses) | `c2-2026-entry-55in-4k` (`value`) | P.C. Richard & Son live listing, 3 Aug 2026, $319.96 (primary) + us.tcl.com official store $319.99 (primary) |
| 5 | "Same size. Same resolution. Same tier." | `spec_note` (the four held axes) + `c1` / `c2` | Both sets: 55-inch class, 3840×2160, LED-backlit LCD, the maker's ENTRY 4K line — entry line to entry line |
| 6 | "Almost everything got more expensive. This didn't." | `c1` source 3 + `c5-bls-constant-quality-televisions` | BLS CPI-U all items `CUUR0000SA0` ROSE 239.261 → 330.724 (+38.2%) over the window (primary) while the BLS televisions index `CUUR0000SERA01` FELL 283.408 → 93.176 (primary). Both directions read straight off the two BLS series |
| 7 | "One reason: panel factories outbuilt the market." — **THE ONE CAUSE** | `primary_cause` (`mechanism: manufacturing-scale`) | VIZIO 10-K FY2023, SEC EDGAR: "a surge in production capacity. During these surges in capacity, retailers can exert strong downward pricing pressure, resulting in sharp declines in prices" (primary) + TrendForce 3 Jan 2024: "the current surplus in TV panel production capacity" (secondary) |
| 8 | "The glut ran so deep, Korean panel makers left the business." — the human stake | `primary_cause` source 2 | TrendForce 3 Jan 2024: "the massive expansion of Chinese panel production capacity and the resulting price competitiveness have led Korean panel makers to exit the supply chain under loss pressures" (secondary, quoting the named event) |
| 9 | "Our receipts: down sixty-six point nine percent, after inflation" (66.9%) | derived from `c1` + `c2` | 1 − (319.96 / 967.58) = 0.6693 → −66.9%. Both inputs primary ($699.99 VIZIO release × BLS deflator; $319.96 P.C. Richard). Pure arithmetic on evidence values, no new figure |
| 10 | "BLS's television index: sixty-seven point one" (67.1%) | `c5-bls-constant-quality-televisions` (`text`) | BLS `CUUR0000SERA01`: 283.408 (Apr 2016) → 93.176 (Jul 2026); 1 − 93.176/283.408 = 67.1% nominal fall (primary) |
| 11 | "Two methods. Point two apart." | rows 9–10 arithmetic | 67.1 − 66.9 = 0.2 percentage points. **Bases differ and the on-screen chip MUST label them** — see Notes, "The point-two line" |
| 12 | "Verdict: still cheap." | `verdict` | Evidence pack verdict field: STILL CHEAP |
| 13 | "One catch. Why it's this cheap costs you something else. Next dig." | teases `secondary_causes[0]` — **no figure, no mechanism spoken** | Ad-subsidised smart-TV economics (VIZIO 10-K FY2023: Platform+ gross profit $364.9M exceeds total gross profit $356.3M). Deliberately NOT explained here — it is the next episode's one cause. Nothing factual is asserted beyond "a catch exists", which that filing supports |

### Not spoken, carried on screen only

- `c3-2016-premium-55in-4k-led` ($1,799 LG 55UH7700) and `c4-2026-premium-55in-4k-led`
  ($1,297.99 Samsung QN55QN90F): the tier-matched anti-cherry-pick check stays on the chart
  (`assets/price-chart-2016-2026.png`), never in the read. Speaking a second tier breaks the
  one-cause discipline and the word budget.
- The **76.2% real** constant-quality fall (`c5` text) stays in the chart footer. The read
  carries the 66.9/67.1 pair because that is the proof-flex; speaking a third percentage
  buries the two that matter.
- The MSRP-vs-shelf asterisk (`spec_note` asterisk 1, TechRadar $999 street on the 55UH7700)
  moves from the v2 read to an on-screen chip under the GAP beat. It must stay visible —
  it is the honesty concession — but it no longer spends words.

## Notes for downstream agents

- **The point-two line (compliance flag, resolved on screen).** Row 9 is the named-model pair
  in July-2026 dollars (real). Row 10 is the BLS constant-quality hardware index, nominal.
  They are genuinely independent methods and they land 0.2 points apart, but the bases differ.
  The spoken line attaches "after inflation" ONLY to our figure and never claims the BLS figure
  is real. Required chip, on screen with row 10: "BLS CUUR0000SERA01, nominal, constant-quality
  · real fall −76.2%". With that chip, nothing spoken or shown is misattributable.
- **`c5` field discrepancy carried forward from v2:** `inflation_adjusted_value: 67.4` in
  `evidence.json` matches neither the claim's own text (76.2%) nor its quoted arithmetic.
  v3 speaks 67.1 (nominal, from the quoted index values) and 66.9 (our pair) — neither touches
  the disputed field. `trend-archaeologist` should still reconcile it.
- **Handoff is a serial kicker, not a comment question (founder override).** The bible offers
  comment question OR affiliate line; v2 used the question. The founder's v3 brief substitutes
  a next-episode tease for serial retention. Affiliate remains not live (docs/01-strategy.md
  ladder), so no shelf line — unchanged from v2.
- **One-cause rule holds.** The kicker names no second cause and no mechanism. "Costs you
  something else" asserts only that a catch exists; the ad-subsidy dig is the NEXT episode,
  where it gets the full excavation it deserves.
- **"Why?" is an answered question, not a rhetorical one.** The charter bans rhetorical
  questions mid-script; this one is the founder-directed mini-mystery and is answered in the
  next breath ("One reason: ..."). If `head-of-format` reads it as rhetorical anyway, the
  fallback is to cut "Why?" (word count drops to 92; nothing else moves).
- **Word band 85–95 is the founder's v3 override** of the charter's 95–130. At ~140wpm natural
  delivery plus seven real pauses this lands ≈44s — the fix for the rushed v2 read.
- **[PAUSE] count is seven**, each load-bearing: (1) after the scene, before the price lands;
  (2) after "Watch it fall." — the odometer rolls INSIDE this pause; (3) after the 2026 figure
  — bible §3, the GAP holds one full beat; (4) after "This didn't." — the mystery hangs;
  (5) before "Two methods." — let the two percentages sit side by side; (6) after "Verdict:" —
  voice-casting §4.2 Gate 5, the colon must be audible; (7) after "One catch." — the kicker's
  bait beat.
- **[EMPHASIS] on "This didn't."** — the wrong-direction turn is the episode's emotional pivot.
- **Visuals policy (docs/05-compliance.md Rule 6, adapted for generated visuals):** everything
  Firefly-generated under ARTIFACT/GAP/EXCAVATION is stylized, cinematic, symbolic — never
  imitation archival, news, CCTV, home video, or a real 2016 storefront presented as a record.
  The RECEIPTS stay real: press-release stills (`assets/2016-press-release.png`,
  `assets/2016-press-release-lg.png`), live-listing screenshots, and the original chart are
  real screenshots overlaid in edit. AI disclosure ON at upload.
- **No "cheapest it has ever been" claim** — unchanged from v2. The evidence establishes a
  2016-vs-2026 pair and an index fall, not an all-time low.

## Delta vs v2 (what changed and why)

| v2 weakness | v3 fix |
|---|---|
| No scene — the number arrived contextless | ARTIFACT opens inside April 2016 for one breath before the price lands |
| Collapse stated, not felt | "Watch it fall." cues the odometer roll; the 2026 figure lands in silence |
| Cause delivered as a list of attributions | Mini-mystery ("This didn't. Why?") → one cause → the Korean-exit human stake |
| Proof was a lone index citation | Proof flex: two independent methods, 0.2 apart — the checkability IS the flex |
| 109 words forced a rushed read | 93 words at ~140wpm with 7 pauses ≈ 44s |
| Handoff was a low-stakes comment question | Serial kicker teasing the ad-subsidy dig — retention without breaking one-cause |
