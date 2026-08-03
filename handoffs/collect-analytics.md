# Handoff — weekly retention collection from YouTube Studio

**Who runs this:** Claude for Chrome, in the founder's logged-in browser.
**Why it exists:** manual-first mode has no Analytics API. This brief replaces it. The output
feeds `growth-analyst`, whose entire method needs retention mapped to the beat sheet.
**Cadence:** weekly, or after any episode that clearly over-/under-performs.

---

## PROMPT BLOCK — hand everything below this line to Claude for Chrome, verbatim

You are collecting analytics for the channel **Price Archaeology** in YouTube Studio. This is
a read-only task: do not change any setting, do not reply to comments, do not edit videos.

1. Go to `studio.youtube.com` → Content → filter to Shorts. Confirm the channel is
   **Price Archaeology**; stop and report if not.
2. For each of the **{{N}}** most recent Shorts, open its Analytics and record:
   - Title and publish date
   - Views, average percentage viewed / average view duration
   - Impressions and click-through if shown for Shorts
   - Likes and comment count
   - On the audience-retention graph (usually under Engagement): read the retention value at
     approximately **3s, 8s, 26s and 36s** by hovering. If exact hover values aren't available,
     describe the curve: where the steepest drop happens (timestamp), and whether the curve is
     smooth or cliffed.
   - Any note YouTube attaches (limited ads, copyright, policy) — copy the exact wording.
3. Output ONE markdown table, exactly these columns, one row per Short:

   | slug/title | published | views | avg % viewed | ret@3s | ret@8s | ret@26s | ret@36s | steepest drop at | likes | comments | flags |

4. Below the table add, per video, one line only if applicable: "retention cliff at Xs".
5. Report the table and nothing else. No interpretation — analysis is done downstream.

---

## After the handoff (founder)

Paste the table into the studio session and invoke `@growth-analyst`. The timestamps map to
the beat sheet (`docs/02-channel-bible.md` §3): 0–3 ARTIFACT · 3–8 GAP · 8–26 EXCAVATION ·
26–36 VERDICT · 36+ HANDOFF. The analyst's report goes to `content/reports/<date>.md` and
recommends exactly one change — never five.
