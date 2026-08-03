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
2. Start a video upload (the Create/Upload action) and select the file: **`{{VIDEO_FILE}}`**.
3. On the details step, set exactly — paste, don't retype:
   - **Title:** `{{TITLE}}`
   - **Description:** paste the full block below, unmodified:
     ```
     {{DESCRIPTION}}
     ```
   - **Audience:** not made for kids.
   - Find the **altered or synthetic content** disclosure (may sit under "Show more") and
     answer **Yes** — this channel uses synthetic narration and always discloses. This step is
     mandatory; if you cannot find the control, stop and report rather than skipping it.
   - **Tags** (under "Show more"): `{{TAGS_COMMA_SEPARATED}}`
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
   python3 scripts/log_publish.py --slug {{SLUG}}
   ```
   This is what keeps the 2/day cap real (gate C6). If the video is later unlisted under the
   corrections policy, free its cap slot with `--retract`.
