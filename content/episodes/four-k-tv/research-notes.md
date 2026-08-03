# Research notes — 001 `four-k-tv`

**Researcher:** trend-archaeologist
**Session date:** 2026-08-03
**Status: SHIPPABLE.** `evidence.json` written and validates against `schemas/evidence.schema.json`.
**Verdict (an output, not an input): STILL CHEAP.** `affiliate_eligible: true`.

This supersedes the 2026-08-03 (earlier run) BLOCKED note. That run failed on a blanket egress
denial. The founder widened the network policy; the research path was re-run unchanged and
completed, with one substitution (Wayback) documented below.

---

## 1. Headline numbers, and exactly where each came from

| | 2016 | 2026 |
|---|---|---|
| **Object** | VIZIO SmartCast 55" E-Series **Ultra HD** Home Theater Display **E55u-D0** | TCL **55Q651G** — 55" Q-Series 4K QLED Google TV |
| **Price** | **$699.99** MSRP | **$319.96** (P.C. Richard & Son) / **$319.99** (us.tcl.com) |
| **Dated** | 19 Apr 2016 (press release dateline) | 3 Aug 2026, both sellers, same day |
| **Nominal change** | — | **−54.3%** |
| **2016 price in Jul-2026 dollars** | **$967.58** | real change **−66.9%** |

**Deflator (shown, not hand-waved):** BLS CPI-U `CUUR0000SA0`, U.S. city average, NSA.
Apr 2016 = 239.261; Jul 2026 = 330.724 → factor **1.382273**. 699.99 × 1.382273 = **967.58**.
I used CPI-U arithmetic rather than the BLS online calculator because the calculator page sits on
`www.bls.gov`, which is WAF-blocked from this container; `data.bls.gov` timeseries pages are not.

**Official series (read off the page, not assumed):** `CUUR0000SERA01` —
*"Televisions in U.S. city average, all urban consumers, not seasonally adjusted"*, Item:
Televisions, Base Period **DECEMBER 2024=100**, "Data extracted on: August 2, 2026".
Apr 2016 **283.408** → Jul 2026 **93.176** = **−67.1% nominal**, **−76.2% real**.

> **The trap in the brief was real and I checked for it.** There is a television-*services*
> index in the same family. `CUUR0000SERA01` is the **hardware item index** — the page states
> `Item: Televisions` and the series shows the long steep decline (296.661 in Jan 2016 to 93.176
> in Jul 2026). I did not take the ID from the prompt; I loaded the page and read the title.

**The most interesting thing in the pack (flagging it, per the charter):** the inflation-adjusted
verdict and the constant-quality verdict *converge*. My named-model real decline is −66.9%; the
BLS constant-quality televisions index fell −67.1% nominally over the same months. Two entirely
independent methods — one built from five manufacturer MSRPs and four retailers, one built from
BLS's hedonic index — land within 0.2 points of each other. That is the strongest internal
consistency check this pack has, and it is worth a line on screen.

---

## 2. The like-for-like discipline (what I held constant, and what I could not)

Held constant: **55-inch class · 3840×2160 · LED-backlit LCD (no OLED on either side) · a
mass-market brand's entry 4K smart line.**

Three asterisks, stated in `spec_note` rather than hidden:

1. **MSRP vs street.** The 2016 number is a manufacturer MSRP at announcement; the 2026 number is
   a shelf price. Street prices fell inside 2016 too — TechRadar's own review of the LG 55UH7700
   quotes **$999** against a **$1,799** launch MSRP. So the true street-to-street fall is smaller
   than the MSRP-to-street fall. I could not fix this cleanly because the archived-retail-listing
   route (Wayback) is blocked; see §5.
2. **The 2026 set is better, not merely cheaper** (QLED, Google TV, higher brightness). That means
   the pack *understates* the per-unit-quality collapse — which is why `CUUR0000SERA01` is carried
   as claim c5.
3. **Tier drift.** 4K + HDR + smart was premium in 2016 and is the floor in 2026. To stop the
   entry-tier headline reading as cherry-picking, claims **c3/c4** carry the premium tier
   separately: LG 55UH7700 **$1,799** (2016) vs Samsung QN55QN90F **$1,297.99** (2026), and
   Samsung's 2016 flagship flat 55" LED (UN55KS9000) at **$2,299**. Every tier fell. The story
   does not depend on which tier you pick — it only changes the size.

### The named trap from the prior run — confirmed and disarmed
`E55-D0` **is 1080p, not 4K.** The 4K sibling is **E55u-D0**. Both appear in the same VIZIO
release: *"55" E-Series HDTV (E55-D0) MSRP $569.99"* and *"55" E-Series Ultra HD Home Theater
Display (E55u-D0) MSRP $699.99"*. Reviewed.com independently splits the same list into "1080P"
and "4K UHD" headings. Using the $569.99 number would have been a 4K claim about a 1080p TV. Both
lines are visible in `assets/2016-press-release.png` — the trap is on the artifact, deliberately.

---

## 3. Sources actually fetched and read (nothing here is from memory or from a search summary)

**Primary (2016)**
- VIZIO, Inc. press release, 19 Apr 2016 (PR Newswire 300253366) — E-Series full MSRP table.
- VIZIO, Inc. press release, 19 Apr 2016 (PR Newswire 300253361) — M-Series; **M55-D0 MSRP $999.99**.
- LG Electronics USA press release PDF, 10 Mar 2016, hosted on lg.com — **55UH7700 $1,799**,
  **55UH8500 $1,999**. Downloaded as PDF and text-extracted with PyMuPDF; pages 1 and 5 rendered
  pixel-accurately into `assets/2016-press-release-lg.png`.

**Secondary (2016)**
- Reviewed.com, `datePublished 2016-04-19T13:00:00Z` — independent restatement of the VIZIO table.
- Digital Trends, `datePublished 2016-03-10T13:00:26+00:00` — "the 60-inch and 55-inch class models
  sell for $2,100 and $1,800 respectively" (rounds LG's $1,799).
- Forbes / John Archer, 12 Apr 2016 — Samsung 2016 55-inch prices: KS9500 $2,499, KS9000 $2,299,
  KS8500 $1,999, KS8000 $1,799.
- TechRadar, LG 55UH7700 review — the $999 street-price asterisk.

**Primary (2026 retail, all captured 3 Aug 2026)**
- P.C. Richard & Son PDP for `55Q651G` — schema.org Offer `"price":"319.96"`, `InStock`.
- us.tcl.com (TCL North America official store) product JSON — sku `55Q651G`, price `319.99`,
  compare_at `399.99`.
- Newegg.com — Hisense `55QD65QF` **$299.99** (new); Samsung `QN55QN90FAFXZA` **$1,297.99** (new);
  Samsung `QN55QN70FAFXZA` **$897.99**.
- vizio.com — `V4K55M-0801`, "55″ 4K HDR Smart TV", **$419.99**.

**Official series**
- `data.bls.gov/timeseries/CUUR0000SERA01` (televisions) and `.../CUUR0000SA0` (all items).

**Cause**
- VIZIO Holding Corp. Form 10-K FY2023, filed 2024-02-28, SEC EDGAR (`vzio-20231231.htm`).
- TrendForce press release, 3 Jan 2024.

---

## 4. The cause: why manufacturing-scale beat the ad-subsidy story

`primary_cause.mechanism = "manufacturing-scale"`.

The decisive quote is from the **same manufacturer as the 2016 anchor set**, in an SEC filing:

> "Intense competition and expectations of growth in demand across the industry may cause media
> entertainment device companies or their suppliers to make additional investments in
> manufacturing capacity on similar schedules, resulting in a surge in production capacity. During
> these surges in capacity, retailers can exert strong downward pricing pressure, resulting in
> sharp declines in prices…" — VIZIO 10-K FY2023

TrendForce (3 Jan 2024) supplies the supply-side half: *"the massive expansion of Chinese panel
production capacity and the resulting price competitiveness have led Korean panel makers to exit
the supply chain under loss pressures."*

**Why the ad-subsidy angle is the runner-up, not the headline.** The brief's excavation surprise
was ad-subsidised smart-TV economics, and it verified beautifully — VIZIO's FY2023 10-K reports
**"Gross profit of $356.3 million"** and **"Platform+ gross profit of $364.9 million"**. Platform+
gross profit *exceeds total* gross profit, so the hardware business contributed no gross profit at
all that year. That is a genuinely startling, checkable fact and it belongs in the pack.

But the bible allows one cause on screen and the charter says pick the one explaining the most of
the delta. The delta is **$380 per set**. A device business running at roughly break-even implies
single-digit dollars of subsidy per unit, not hundreds. Panel supply explains the rest. So:
manufacturing-scale on screen, ad-subsidy in `secondary_causes`. If the writer wants the ad line,
it must replace the panel line, not sit beside it.

**Deliberately not claimed:** tariffs. Over this window US tariff policy pushed prices the *other*
way. I verified nothing about it, so nothing about it appears.

---

## 5. Dead ends and blocks (complete list)

| Attempt | Result |
|---|---|
| `web.archive.org` snapshot pages | **Blocked.** The archived-retail-listing route — the charter's preferred primary and the preferred C1 artifact — is unavailable. Substituted per the sanctioned alternative: manufacturer MSRP press release + contemporaneous review, and an `original-chart` artifact. **Pending upgrade; record in `docs/DECISIONS.md`.** |
| Headless Chromium network access | **Broken at the browser layer** (`ERR_CONNECTION_RESET` on every host, including hosts curl reaches). Tried `--proxy-server`, `--disable-quic`, `--proxy-bypass-list=<-loopback>`, fresh `--user-data-dir`. Local `file://` rendering and screenshots work fine, which is all the artifacts needed. Even if `web.archive.org` is allowlisted, **Chromium must be fixed too** or the Wayback screenshot stays impossible. |
| walmart.com | 200 but serves the PerimeterX "Robot or human?" interstitial on `/search` **and** on `/ip/` PDPs. `business.walmart.com` identical. WebFetch also 403. No price obtained. |
| target.com | 200, but the PDP and category pages are fully client-rendered — no JSON-LD, no `current_retail`, no price anywhere in the served HTML. Redsky API needs a key I will not guess. No price obtained. |
| costco.com | 403 Akamai "Access Denied" on both search and PDP. |
| bestbuy.com | Blocked (per environment map; not retried). |
| Amazon, Sam's Club, B&H, Adorama, Crutchfield, Abt, BJ's, Micro Center | 403 / 503 / bot interstitial. |
| **Substitution made:** the brief asked for two of Walmart/Target/Newegg/Costco. Only Newegg was usable. I substituted **P.C. Richard & Son** (an independent US electronics retailer) and **us.tcl.com** (TCL's own US store) and got the **same model** at both on the **same day**, which is stronger than two different models at two retailers. Flagging the substitution explicitly for `compliance-officer`. | |
| news.samsung.com (US newsroom) | Reachable, and I queried its WP REST API across all of 2016 — **there is no 2016 TV pricing post**. Samsung's April 2016 pricing release went out on Business Wire, which is 403. Samsung 2016 prices therefore enter the pack only as a **secondary** (Forbes), never as the primary. |
| businesswire.com | 403 Akamai. |
| hometheaterreview.com, highdefdigest.com, camelcamelcamel.com | 403. |
| hdtvsolutions.com | 200 — but it is a **verbatim reprint** of the LG release, so it is *not* an independent second source. Not cited. Worth remembering: a press-release mirror is not corroboration. |
| fred.stlouisfed.org | Listed as open, but every request stalled (`HTTP/2 INTERNAL_ERROR`, then a 60s timeout on HTTP/1.1). **No FRED corroboration was obtained.** The televisions index therefore rests on a single publisher (BLS) via two of its series pages. Honest gap; not fatal, since BLS is the authoritative issuer, but a FRED mirror would be better and should be added on a later run. |
| Wikimedia Commons video search | Essentially barren for this subject — searches for TV factories / LCD lines / electronics retail returned unrelated PDFs. Only one usable Commons item was found (a CC BY-SA 4.0 still). Motion footage therefore comes from Archive.org. |
| Newegg listing for VIZIO `V4K55M-0801` | **$330.49 — but tagged "Refurbished."** Rejected: a refurb price is not a like-for-like new-unit price. This nearly became a wrong number; recording it so the next researcher checks condition flags on Newegg. |

---

## 6. Artifacts produced

- `assets/price-chart-2016-2026.png` — **the C1 artifact.** Eleven named 55" 4K models on one
  axis; five 2016 sets from three independent sources, six 2026 listings from four independent
  sellers; every 2016 MSRP also drawn in July-2026 dollars; BLS series IDs and values in the
  footer; the MSRP-vs-street caveat printed on the chart itself.
- `assets/price-chart-2016-2026.source.html` — the chart's source, checked in so every figure is
  re-derivable without me.
- `assets/2016-press-release.png` — render of the **captured** VIZIO 19 Apr 2016 release body
  (page chrome stripped, banner states the URL, the publication date and the retrieval date).
  Shows the E55u-D0 $699.99 line directly above the 1080p E55-D0 $569.99 line.
- `assets/2016-press-release-lg.png` — pixel-accurate PyMuPDF render of pages 1 and 5 of LG's own
  10 Mar 2016 pricing PDF, straight from lg.com.

Honesty note on the first PNG: it is a render of the HTML I fetched, with navigation chrome
removed — equivalent to cropping a screenshot. It is not a Wayback capture and must not be
captioned as one. The LG PNG is a direct render of the original PDF and carries stronger
provenance; prefer it if only one can go on screen next to a source chip.

---

## 7. Handoff notes

- **First spoken word is a number/year.** The line the evidence supports: *"In 2016, the cheapest
  55-inch 4K TV Vizio sold was $699.99."*
- **The gap line:** *"Today the same tier is $319.96."*
- **One cause only:** panel manufacturing capacity. Do not also say "ads pay for your TV" — pick one.
- **If the writer wants the ad angle instead**, the sourced sentence is: *"In 2023 Vizio's
  advertising arm made more gross profit than the whole company — the hardware made none."*
  It is in `secondary_causes` with the filing URL. It replaces the panel line; it does not join it.
- **Do not say "roughly."** Nothing in this pack is estimated; every `estimated` flag is `false`.
- **Citation chips:** 2016 → "VIZIO press release, 19 Apr 2016". 2026 → "P.C. Richard & Son,
  3 Aug 2026". Index → "BLS CUUR0000SERA01".
- **Affiliate shelf** is permitted (STILL CHEAP). The defensible current best-value pick from what
  was actually priced today is the TCL 55Q651G at ~$320 or the Hisense 55QD65QF at $299.99.
