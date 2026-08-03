# Handoff — evidence collection for episode 001 (`four-k-tv`)

**Why this handoff exists.** This studio's cloud environment has a restrictive network
policy: outbound requests to archive.org, bls.gov, retailer sites — even example.com — are
denied at the proxy (only package hosts pass). `trend-archaeologist` correctly refused to
write an evidence pack it couldn't source ("an absent file cannot be mistaken for research")
— the full dead-end log is in `content/episodes/four-k-tv/research-notes.md`.

**Two ways to unblock. Pick one:**

- **Path A (permanent, preferred): widen the environment's network policy.** It was chosen
  when this Claude Code environment was created and you can change it — allow the domains
  below (or switch to trusted/full egress). Then the studio researches every future episode
  autonomously and this handoff file never gets used again:
  `web.archive.org, archive.org, bls.gov, data.bls.gov, fred.stlouisfed.org, bestbuy.com,
  walmart.com, amazon.com, cnet.com, rtings.com, commons.wikimedia.org`
- **Path B (works today): run the brief below in Claude for Chrome** and paste its output
  block back into the studio chat. Attach the two screenshots it saves.

---

## PROMPT BLOCK — hand everything below to Claude for Chrome, verbatim

You are collecting price evidence for a research project about what a 55-inch 4K TV cost in
2016 versus today. Everything you report must be something you actually saw on a page you
loaded — never from memory, never approximated. Copy exact strings. If you cannot verify an
item, write UNVERIFIED for it rather than guessing.

**Task 1 — the 2016 price (primary source).**
1. Identify one specific, mainstream 55" 4K TV model sold in the US in 2016 (Samsung
   KU-series, Vizio M-series, LG UH-series are good hunting grounds — a 2016 review on
   cnet.com or rtings.com will give you exact model numbers).
   ⚠ Trap found in earlier research: the Vizio E55-D0 is 1080p, not 4K. Verify the panel
   resolution says 4K/2160p on the page you cite.
2. On web.archive.org, find a 2016 snapshot of a retailer product page (bestbuy.com,
   walmart.com, or amazon.com) for that model showing a price. Use the Wayback Machine
   calendar; any 2016 month works.
3. Record: the model number, the EXACT price string as shown, the full snapshot URL
   (it contains a 14-digit timestamp), and the snapshot date.
4. **Save a full-page screenshot of that archived listing** — this is the episode's core
   artifact. Name it `2016-listing.png`.
5. Find one 2016-era review or article that states the same model's price in its text —
   record URL and the exact sentence (this is the secondary source).

**Task 2 — the 2026 price (two live retailers, same day).**
Find a current mainstream 55" 4K LED TV (comparable tier — not OLED, not a doorbuster) at
TWO different major retailers. Record: model, exact price string, URL, and today's date for
each. Same tier as the 2016 model matters more than same brand.

**Task 3 — the official series.**
On bls.gov (or fred.stlouisfed.org), find the CPI item series for **televisions** (the
hardware index, under video/audio products).
⚠ Trap: there is a similarly named series for television *services* (cable/streaming) —
that is the wrong one. The right series shows a long, steep decline.
Record: the series ID exactly as shown, the page URL, its index value nearest to mid-2016,
and the latest value shown, with their dates.

**Task 4 — the cause (one mechanism, sourced).**
Find one credible article (industry/business press) explaining why TV prices collapsed —
look for LCD panel manufacturing capacity/oversupply, and separately for articles about
TVs being subsidised by advertising/data ("the TV is the product" economics). Record for
each: URL, publication, date, and the one sentence that states the mechanism.

**Task 5 — footage leads (no downloads needed).**
On archive.org, search: "consumer electronics store 2016", "electronics retail b-roll",
"LCD panel factory", "television manufacturing" — and on commons.wikimedia.org: "electronics
store interior", "flat screen TV shop". For 4–6 items that look usable as vertical-crop
b-roll, record: item URL, title, and the license line EXACTLY as printed on the item page.

**Output — fill this template and return it as one block:**

```
2016 MODEL:            <model number>
2016 PRICE (exact):    <e.g. $XXX.XX>
WAYBACK URL:           <full URL with 14-digit timestamp>
SNAPSHOT DATE:         <date>
SECONDARY SOURCE:      <URL> | "<exact sentence containing the price>"
RESOLUTION CHECK:      <where the page says 4K/2160p>

2026 RETAILER 1:       <retailer> | <model> | <exact price> | <URL> | <date>
2026 RETAILER 2:       <retailer> | <model> | <exact price> | <URL> | <date>

BLS SERIES ID:         <ID> | <URL>
SERIES 2016 VALUE:     <value> @ <date>
SERIES LATEST VALUE:   <value> @ <date>

CAUSE A (panels):      <URL> | <publication, date> | "<mechanism sentence>"
CAUSE B (ad-subsidy):  <URL> | <publication, date> | "<mechanism sentence>"

FOOTAGE 1..6:          <URL> | <title> | "<license line exactly as shown>"

UNVERIFIED ITEMS:      <anything you could not confirm, stated plainly>
```

Attach `2016-listing.png` (and a screenshot of the BLS series page if easy). Do not round
any number. Do not substitute a similar model. Exact strings only.

---

## After the handoff (founder)

Paste the output block into the studio chat and attach the screenshot(s). The studio then:
converts it to `evidence.json` (every claim keeps its two sources), saves your screenshot as
the C1 artifact, downloads the footage *if egress allows* (else lists exact files for you),
and runs the rest of the pipeline — script, VO, render, gate — hands-free.
