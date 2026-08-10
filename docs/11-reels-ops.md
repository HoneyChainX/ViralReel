# 11 — Reels operations: the three gaps

Founder handoff, verified against live tool state on 2026-08-03. The gaps are correctly
identified. The tool assignments need four corrections, because **status "enabled" and
"callable in this session" are different things**, and one connector has no funding.

---

## Verified tool state (measured, not assumed)

| Tool | Plan said | Actually |
|---|---|---|
| Higgsfield `shorts_studio` / `reframe` / `virality_predictor` | ✅ have | **Connected but unfunded — balance is 0 credits, free plan.** `shorts_studio` on a 45s source = **135 credits**; `reframe` to 9:16 at 1080p = **419 credits**. Nothing is executable |
| Adobe `video_create_quick_cut` / `video_resize` | ✅ have | ✅ **Correct** — connected, enabled, covered by the CC subscription |
| Postiz | ✅ enabled (plugin) | Plugin **is** enabled — but it exposes **no callable surface in this Claude Code session**. It is a claude.ai-chat CLI plugin; it works there, not here |
| Canva | ⚙ toggled off | **Already toggled ON in chat** (`enabledInChat: true`) — what it needs is **authorization**, not a toggle. Its 31 tools disconnected mid-session pending auth |
| n8n | ⚙ toggled off | ✅ **Correct** — `enabledInChat: false`. This is the one real toggle, and only the founder can flip it |
| Adspirer | ✅ enabled (plugin) | Plugin enabled (91 ad tools) — same surface caveat as Postiz, and premature regardless: nothing is published to boost |

### Why the surface caveat matters
This studio runs in a **Claude Code remote session**, not the claude.ai chat surface. Chat
plugins and some connectors do not project into it. So "enabled in my chat" ≠ "the studio can
call it." Anything Postiz- or Adspirer-shaped is a **founder-side or chat-side action**, and the
repo's job is to hand it a ready-to-run input, not to pretend it can drive it.

### The credits question is a reversal, not a detail
`config/channel.yaml` sets `paid_generators_enabled: false`, `stock_enabled: false`, and the
$0.00-per-video guarantee is the reason the channel is viable against Shorts' capped RPM
(`docs/01-strategy.md` §3). Higgsfield closing Gaps 1 & 3 requires **buying credits** — a
deliberate reversal of a standing decision. It is the founder's call to make, but it should be
made on the numbers below, not by accident.

---

## Gap 1 — volume (script → vertical video → captions too slow)

**The plan's tool is the wrong shape for the job.** `shorts_studio` **restyles an existing
source video**; it does not build a reel from a script. Even fully funded it would not close
this gap — it needs a finished video as input. And `reframe` is unnecessary outright: the studio
renders **native 1080×1920**, so there is nothing to reframe, and ffmpeg crops for free anyway.
Paying 419 credits to reach an aspect ratio we already output would be pure waste.

**What actually closes it, at $0 — the hybrid pipeline.**
The founder rejected the studio render's *aesthetic*, not its speed. The measured speed was
already good: script → 21-scene 9:16 → 23 auto-captions → gate-checked, ~6 minutes unattended.
So split the labour along the grain of what each side is good at:

```
studio (free, minutes)        founder (Adobe, taste)         studio (free, minutes)
research + script + prompts → 4 Firefly hero clips        → assembly + overlays + captions
                                (adobe-master-prompt.md)     + odometer + stamp + gate + QC
```

The founder generates only the **4 hero clips** — not the whole edit. The pipeline takes them as
assets and does every mechanical step: real-data overlays with citations, captions, the odometer,
the stamp, loudness, delivery QC, gate. Per-reel founder time drops from "edit a whole video" to
"generate four clips and approve."

Supporting, already paid for: Adobe `video_create_quick_cut` (fast selects) and `video_resize`.

**Action:** add a `--assets-from` mode to `scripts/render_episode.sh` so founder-generated clips
drop into `assets/` and the scene plan maps to them. Cost: $0. This is the highest-leverage
change in this document.

## Gap 2 — cross-posting cadence (IG / TikTok / Shorts)

**Blocked on two founder actions, and on a decision the repo already recorded.**

`docs/DECISIONS.md` **D2** deliberately declined TikTok at launch, for reasons that still hold:
the compliance gate's checks are **YouTube-shaped** (nothing audits TikTok's disclosure rules or
reuse policy), and one platform's retention data is confounded enough for a channel with zero
published episodes. Cross-posting reverses D2. That is fine — but it should update D2 with the
new reasoning, not bypass it.

**What the studio can do at $0 today:** emit, per episode, a `crosspost/` bundle —
per-platform caption/hashtag variants, the 9:16 master, and the exact Postiz CLI invocations
for the founder (or claude.ai chat) to run. The repo prepares; the founder or n8n executes.

**Actions only the founder can take:**
1. **Authorize Canva** in claude.ai connector settings (it is already toggled on — it needs auth)
2. **Toggle n8n on** in this chat's connector settings — then the auto-pipeline
   (new video → caption → Postiz schedule) becomes buildable

## Gap 3 — no feedback loop

**This gap is already closed by something built and free — it has simply never run, because
nothing is published yet.**

`handoffs/collect-analytics.md` + `@growth-analyst` produce retention mapped to the beat sheet
(3s / 8s / 26s / 36s → ARTIFACT / GAP / EXCAVATION / VERDICT), which is the only readout that
improves the format. `virality_predictor` is a *pre*-publish estimate; retention is *actual
behaviour*. Real data beats a prediction, and it costs nothing.

`virality_predictor` becomes genuinely useful at one specific point: **A/B-ing hooks before
publishing**, once there is enough published retention data to know whether its score correlates
with our real curves. Until then it is an unvalidated number we would be paying for.

**Adspirer** is for boosting proven winners. With zero published episodes there is nothing to
boost — revisit after the first 100k-view Short (`docs/01-strategy.md` §6).

---

## Recommended sequence

1. **Now, $0:** hybrid pipeline (`--assets-from`), so founder-generated clips flow into the
   automated assembly. This is what actually fixes volume.
2. **Now, founder:** authorize Canva; toggle n8n on. Both are settings actions the studio cannot
   perform.
3. **After episode 001 publishes:** run the analytics handoff. Get real retention. That is the
   feedback loop.
4. **After ~10 published episodes:** decide on Higgsfield credits with evidence — by then we know
   whether hooks or the excavation beat is where viewers actually drop, which is exactly what
   `virality_predictor` claims to predict. Buying it before then is buying an unvalidated signal.
5. **After the first winner:** Adspirer, on that specific video.

## What the studio will not do without an explicit decision

- Spend Higgsfield credits (reverses `paid_generators_enabled: false` and the $0 guarantee)
- Publish to TikTok/IG (reverses `docs/DECISIONS.md` D2, and the gate does not audit those
  platforms' rules)
- Claim a connector works in this session without having called it
