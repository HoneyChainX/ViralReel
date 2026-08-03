# 01 — Strategy

## 1. The thesis

> **Nostalgia gets the click. Inflation gets the comment. The bargain gets the money.**

Price Archaeology sits on the intersection of two independently-verified 2026 forces:

**Force A — the nostalgia wave.** "2026 is the new 2016" is one of the largest organic social
trends of the year: 37M+ Instagram posts, 1M+ TikTok posts, celebrity participation, and heavy
mainstream press coverage. Critically, the *stated reason* people love it is a hunger for the
pre-algorithmic internet — "the last moment of true mass culture." That is an audience actively
rewarding content that feels human and researched over content that feels generated.

**Force B — price rage.** Cost-of-living is the most reliably engaging non-political topic on
short-form. It needs no celebrity, no trend audio, and no personality to work. It is evergreen,
it is universal, and every viewer arrives pre-loaded with an opinion.

Everyone is currently running Force A (throwback photo dumps) or Force B (inflation rants).
The combination is open, and the combination is strictly better than either half: nostalgia
supplies the hook and the free archival visuals, price supplies the payload and the search
demand, and "what's still cheap" supplies the revenue.

## 2. Why the 10-year gap specifically

2016 is not an arbitrary anchor. It is load-bearing:

- **It is the trend.** We ride an existing wave rather than manufacturing one.
- **It is inside living memory for the entire Shorts demographic.** A 2026 22-year-old was 12 in
  2016. They remember it, but they didn't *pay* for anything in it. That asymmetry — "I remember
  this, but I never knew what it cost" — is the exact emotional engine of the format.
- **The evidence exists and is free.** The Wayback Machine has dense 2016 retail coverage.
  BLS/FRED series are continuous. Wikimedia and Archive.org have abundant period footage. A
  2006 or 1996 anchor would be far more expensive to source.
- **A decade is the cleanest possible math.** "Ten years" needs no explanation on screen.

## 3. Monetization — and the honest version of it

**Ad revenue is not the business.** YouTube pools 45% of Shorts ad revenue across all eligible
views and distributes by view share. This structurally caps Shorts RPM at roughly $0.01–$0.45
regardless of niche. A million views on a Short is realistically $30–$200. Anyone who tells you
otherwise is selling a course.

**Shopping affiliate is the business.** For product-intent content the gap is not incremental —
a single product Short has been documented earning ~$1,200 in affiliate against ~$10 in ad
revenue on the same views. Median merchant commission sits near 15%. Realistic funnel math:
100k views → ~3k product clicks (2.8–4.2% CTR) → 30–40 purchases (0.8–1.4% conversion) →
**$450–$800**.

### The problem I need to name

I recommended a different concept (*Shelf Life*) partly because Price Archaeology has **weaker
direct purchase intent**. A video about 2016 concert ticket prices makes people angry; it does
not make them buy anything. That is a real gap and I am not going to paper over it.

**The fix is structural, and it's built into the format.** The slate is deliberately split:

| Segment | Share of slate | Job | Revenue |
|---|---|---|---|
| **THE DIG** (things that got worse) | 40% | Reach, rage, comments, shares | Ads only |
| **STILL CHEAP** (things that collapsed in price) | 40% | Purchase intent | **Affiliate — the engine** |
| **EXTINCT PRICES** | 10% | Format identity, rewatch | Ads only |
| **TIME CAPSULE CART** | 10% | Series anchor, subscriber driver | Mixed |

STILL CHEAP is not a filler segment — it is the P&L. TVs, SSDs, solar, LED lighting, genome
sequencing, air fryers, and 3D printers have all genuinely collapsed in price since 2016. Those
episodes end on "this is the cheapest this has ever been, here's the current one" — which is a
recommendation the viewer *asked for* by watching, not an ad bolted onto a rant.

**Counting rule (added after review M1):** the 40% quota counts only episodes whose brief says
**Affiliate: yes** with no hedge. A "cautiously" (solar) or category-restricted (genome) brief
is a STILL CHEAP *story* but not an affiliate *slot* — the launch slate's effective affiliate
share was 2/10 while claiming 40%, which is exactly the drift this rule exists to catch.
`growth-analyst` reports the **view-weighted** affiliate-eligible share, since slate-share and
view-share will diverge. The slate also keeps a category-depth ledger
(`content/episodes/SLATE.md`): when unaired affiliate-grade categories drop below 26 weeks of
runway, finding more becomes a strategy-lead priority, not a nice-to-have.

The rage episodes subsidize reach. The cheap episodes convert it. Neither works alone.

### Revenue ladder

1. **Months 1–3 — none.** Build the archive and the format. Do not monetize a channel with no
   retention data; you will optimize for the wrong thing.
2. **Months 3–6 — YouTube Shopping affiliate** on STILL CHEAP episodes only. Requires 10k subs.
3. **The data product — split in two after review (docs/DECISIONS.md D6):**
   - **3a, from ~month 2 — the free public index.** A read-only page of *already-aired* price
     pairs (they were on screen; publishing them leaks nothing), on the connected Cloudflare
     free tier, with email capture. This is the off-platform hedge against R1 — the moat is
     worthless as a hedge while it sits private — and it's what a journalist can actually cite.
   - **3b, months 6–12 — paid products.** Newsletter, licensed chart pack. Unchanged. By then
     the database holds hundreds of verified pairs, and journalists cite a sourced price
     database; they will not cite a Shorts channel.
4. **Month 12+ — long-form.** Long-form earns roughly **20× per view** what Shorts do. Shorts are
   the top of the funnel, not the destination. "The 2016 Grocery Cart" as a 12-minute video is
   the actual business.

## 4. Competitive moat

Three layers, in increasing durability:

1. **Format IP** (weak) — copyable in a week.
2. **The verified price database** (strong) — every episode permanently adds a sourced pair.
   A competitor starting in month 6 starts at zero. This compounds and nothing else does.
3. **Provenance** (strongest) — being the channel whose numbers are *checkable* in a category
   where everyone else is guessing. This is what survives both the slop crackdown and chatbot
   substitution.

### On the chatbot threat

An AI assistant can already tell a user what a TV cost in 2016. That is a genuine, structural
threat to generic deal content and it will get worse. Our answer is that we sell three things a
chatbot does not deliver: **the archival visual proof** (the actual 2016 storefront, the actual
period footage), **a serial identity** worth returning to, and **an emotional verdict**. Nobody
opens a chatbot to feel something about a price. Design to that and the threat narrows.

## 5. Risk register

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | **Inauthentic Content Policy strike** — channel-level judgement on mass-production | **Fatal** | Hard compliance gate; original research artifact required per video; publish cap of 2/day enforced in config; no template-only episodes; **off-platform database + email list live by month 3** (docs/DECISIONS.md D6) so a strike costs distribution, not the asset. See `docs/05-compliance.md` |
| R2 | **A wrong price number** — one bad figure destroys a provenance-based brand | **Fatal** | Two-source rule; `compliance-officer` veto; on-screen citations; public corrections log |
| R3 | Nostalgia wave decays | High | The format's spine is *price*, not 2016. The anchor year is a config value — it can slide to a rolling 10-year window without touching the pipeline |
| R4 | Weak purchase intent | High | 40% STILL CHEAP quota, enforced in `config/channel.yaml` |
| R5 | Chatbot substitution | Medium | Visual proof + serial identity + verdict (§4) |
| R6 | Archival footage licensing | Medium | Public-domain / CC-BY only; `archive-sourcer` records license + URL per asset; cleared list in config |
| R7 | Voice sameness across Shorts | Medium | One cast ElevenLabs voice, consistent — sameness is *branding* at channel level; variation lives in writing, not voice |
| R8 | Undisclosed-AI penalty | Medium | AI disclosure set at upload by default; no photorealistic synthetic humans anywhere in the format |

R1 and R2 are the only two that can kill the company, and both are addressed by the same
mechanism: the gate in `docs/05-compliance.md`. Everything else is a bad quarter, not an ending.

## 6. What success looks like

| Horizon | Target | The metric that actually matters |
|---|---|---|
| Day 30 | 30 published, format locked | Avg. view duration > 85% |
| Day 90 | 1k subs, one 100k+ Short | Which segment drove it |
| Month 6 | 10k subs, affiliate live | Affiliate revenue per 100k views |
| Month 12 | Long-form + database live | Revenue *not* from YouTube |

Do not optimize subscriber count. Optimize **the % of viewers who watch to the verdict** — that
is the number that predicts everything downstream, and it is the number the format is built for.
