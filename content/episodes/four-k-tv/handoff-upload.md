# Handoff — upload one episode via YouTube Studio

**Who runs this:** Claude for Chrome, in the founder's logged-in browser.
**Precondition:** the episode's `content/episodes/<slug>/gate.json` says `"verdict": "PASS"`.
If it doesn't, stop — this brief must not exist for an ungated episode.

## Prepare the brief (founder or studio, before handing off)

Fill every `{{…}}` below from `content/episodes/<slug>/packaging.json`, and have the video
file (`out/<slug>.mp4`) downloaded where the browser can reach it. Do not hand over a brief
with placeholders still in it.

---

## PROMPT BLOCK — hand everything below this line to Claude for Chrome, verbatim

You are uploading one YouTube Short for the channel **Price Archaeology**. Work only inside
YouTube Studio. Do not change any channel-level setting, do not touch monetization, and stop
and report if anything unexpected appears (a policy dialog, a verification prompt, an unknown
account chooser).

1. Go to `studio.youtube.com`. Confirm the channel shown is **Price Archaeology** — if any
   other channel is active, stop and report.
2. Start a video upload (the Create/Upload action) and select the file: **`out/four-k-tv.mp4  (delivered in chat — save it locally first)`**.
3. On the details step, set exactly — paste, don't retype:
   - **Title:** `$699.99 to $319.96: The 55-Inch 4K TV, 2016 vs 2026`
   - **Description:** paste the full block below, unmodified:
     ```
     VIZIO's cheapest 55-inch 4K smart TV (E55u-D0) launched at an MSRP of $699.99 in April 2016; TCL's cheapest 55-inch 4K smart TV (55Q651G) sells for $319.96 today.

Sources:
- 2016 (primary): VIZIO, Inc. press release via PR Newswire, 19 Apr 2016 — "VIZIO SmartCast 55\" E-Series Ultra HD Home Theater Display (E55u-D0) MSRP $699.99" — https://www.prnewswire.com/news-releases/vizio-smartcast-e-series-ultra-hd-home-theater-display-joins-next-generation-smart-entertainment-ecosystem-with-ultra-hd-picture-quality-300253366.html
- 2016 (secondary): Reviewed.com, 19 Apr 2016 — price breakdown confirming E55u-D0 MSRP $699.99 — https://www.reviewed.com/televisions/news/vizio-debuts-2016-m-series-e-series-tvs-with-smartcast
- 2026: P.C. Richard & Son, live listing accessed 2026-08-03, $319.96 — https://www.pcrichard.com/tcl-55-class-q-series-qled-4k-uhd-smart-google-tv/55Q651G.html
- 2026: TCL North America official US store, accessed 2026-08-03, $319.99 — https://us.tcl.com/products/q-class-4k-uhd-hdr-qled-smart-tv-with-google-tv
- Series: BLS CPI-U CUUR0000SERA01 (Televisions, constant-quality index) — https://data.bls.gov/timeseries/CUUR0000SERA01
- Series: BLS CPI-U CUUR0000SA0 (All items, used as the inflation deflator) — https://data.bls.gov/timeseries/CUUR0000SA0
- Note: the 2016 figure is a manufacturer launch MSRP; the 2026 figure is a live retail shelf price. This is disclosed, not smoothed — street prices fell within 2016 too (LG's 55UH7700 launched at $1,799 in March 2016 and was reviewed at $999 the same year), so the true street-to-street fall is smaller than MSRP-to-street.

Footage: Archive.org, CC0 1.0 — no attribution legally required; credited as "Warehouse of Old Electronics Equipment" / Archive.org; Prelinger Archives / Archive.org, Public Domain — "Television Tomorrow"; Prelinger Archives / Archive.org, Public Domain — "Magic in the Air" (1955); Prelinger Archives / Archive.org, Public Domain — "Sharp Calculator Commercial"; Santeri Viinamäki (User:Zunter) / Wikimedia Commons, CC BY-SA 4.0 ("Televisions on sale", 2017-12-27); Price Archaeology original chart — eleven named models, per-point citations, from evidence.json sources; Provenance render of VIZIO, Inc. press release, 19 Apr 2016, via PR Newswire (factual pricing record, provenance use); Provenance render of LG Electronics USA press release, 10 Mar 2016 (factual pricing record, provenance use)

Corrections: github.com/HoneyChainX/ViralReel/blob/main/content/CORRECTIONS.md
     ```
   - **Audience:** not made for kids.
   - Find the **altered or synthetic content** disclosure (may sit under "Show more") and
     answer **Yes** — this channel uses synthetic narration and always discloses. This step is
     mandatory; if you cannot find the control, stop and report rather than skipping it.
   - **Tags** (under "Show more"): `4k tv price history, 55 inch 4k tv, vizio e55u-d0, tcl 55q651g, tv prices 2016, tv prices 2026, 2016 vs 2026, price archaeology, cost of living, electronics deflation, bls cpi televisions, consumer electronics prices, smart tv price drop`
4. Skip video elements. Wait for checks to finish. If YouTube raises any copyright or policy
   flag, stop and report the exact message — do not proceed.
5. **Visibility: Private.** Never Public, never Unlisted, never Scheduled. Save.
6. Report back: the video's Studio URL, the checks status, and a one-line confirmation that
   the AI disclosure was set to Yes and visibility is Private.

Do not pin comments, do not publish, do not delete anything. Your job ends at a saved
private upload.

---

## After the handoff (founder)

1. Watch the private upload start to finish. This is compliance check C10 in its strongest
   form — you are the last gate.
2. Flip to **Public** in Studio if it's right.
3. Pin the source comment: paste `pinned_comment` from `packaging.json` and pin it.
4. **Log it — not optional:**
   ```bash
   python3 scripts/log_publish.py --slug four-k-tv
   ```
   This is what keeps the 2/day cap real (gate C6). If the video is later unlisted under the
   corrections policy, free its cap slot with `--retract`.
