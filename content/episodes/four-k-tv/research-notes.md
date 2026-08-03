# Research notes — 001 `four-k-tv`

**Researcher:** trend-archaeologist
**Date of session:** 2026-08-03
**Status: BLOCKED — NOT SHIPPABLE. No `evidence.json` was written.**

> This is an **infrastructure** blocker, not a finding about 4K TVs. Nothing below says the
> STILL CHEAP hypothesis is wrong. It says I could not verify a single number, and under the
> two-source rule an unverifiable episode does not ship.

---

## 1. What I verified

**Nothing.** Zero prices, zero series IDs, zero snapshot dates, zero footage licenses.

I did not reach a single web page in this session. Every factual value that would have gone into
`evidence.json` — the 2016 archived price, the 2026 retail prices, the BLS series ID, the
inflation adjustment, the cause sources, the footage licenses — remains unverified.

## 2. Why: outbound egress is denied for every fetch path

Confirmed by direct test, not assumed. Three independent transports, all blocked:

| Transport | Result |
|---|---|
| `curl` via Bash (through `$HTTPS_PROXY`) | `curl: (56) CONNECT tunnel failed, response 403` |
| `WebFetch` tool | `HTTP 403 Forbidden` on every host; `web.archive.org` refused at the tool layer ("Claude Code is unable to fetch from web.archive.org") |
| Headless Chromium `/opt/pw-browsers/chromium` | Rendered Chrome's `ERR_TUNNEL_CONNECTION_FAILED` error page |

The proxy's own diagnostic endpoint (`$HTTPS_PROXY/__agentproxy/status`) logged each attempt as
`connect_rejected` — *"gateway answered 403 to CONNECT (policy denial or upstream failure)"* — for:

```
archive.org:443
www.bestbuy.com:443
www.bls.gov:443
fred.stlouisfed.org:443
commons.wikimedia.org:443
```

Plus 403 (not logged separately) for `en.wikipedia.org`, `www.walmart.com`, `www.rtings.com`,
and `example.com`. **`example.com` failing is the tell: this is a blanket denial, not a
site-specific block or a bot-detection problem.**

Per `/root/.ccr/README.md`: *"403 / 407 from the proxy — the destination host is not allowed by
your organization's egress policy for this session. Do not retry or route around it — report the
blocked host."* I stopped retrying and did not attempt any workaround.

**The only working network capability is the `WebSearch` tool.**

## 3. Why WebSearch alone cannot rescue this episode

WebSearch returns result titles, URLs, and a *summarizer's synthesis* of pages I never loaded.
Using it as a source would break three rules at once:

1. "Never cite a source you have not actually fetched and read."
2. Every value must be read from a fetched page **with the exact quote saved**. A summarizer's
   paraphrase is not a quote, and I cannot tell which words are the page's and which are the
   summarizer's.
3. The two-source rule requires a **primary** source. The primary here is defined as the archived
   retail listing at a specific 14-digit Wayback timestamp. A search snippet is not that, and
   there is no way to obtain the snapshot date — which the bible requires on screen — without
   loading the snapshot.

Concretely, one search summary asserted the Samsung UN55KU6300 had an *"original price of
$699.99"* at Best Buy. **I am recording that as a lead only and it must not be used.** It has no
date, no snapshot, no quoted price string, no indication whether it is MSRP, launch price, or a
promo, and I could not open the page to check. That is precisely the half-remembered-number
failure mode `SLATE.md` warns about.

A second search summary gave *contradictory* readings of the BLS television series ID — offering
`CUSR0000SERA01` as "video and audio" and `CUSR0000SERA02` as "cable, satellite and live
streaming television service" (a **service** index, not a **hardware** index — a trap worth
flagging for the next run). Resolving which ID is the TV-set item series requires reading
`bls.gov` or `download.bls.gov/pub/time.series/cu/cu.series`, both blocked.

## 4. Dead ends, in order

1. `archive.org/wayback/available?url=bestbuy.com&timestamp=20160601` — proxy 403 (Bash).
2. Wayback CDX API (`web.archive.org/cdx/search/cdx`) — Bash: `Host not in allowlist`.
3. `web.archive.org` snapshot of the Best Buy UN55KU6300 page — WebFetch refuses this host outright.
4. `bls.gov/cpi/` — 403.
5. `fred.stlouisfed.org/series/CUSR0000SERA01` — 403.
6. `www.bestbuy.com`, `www.walmart.com` (2026 live prices) — 403. Could not establish a
   same-day two-retailer current price.
7. `www.rtings.com` KU6300 review (intended secondary, price-in-body) — 403.
8. `commons.wikimedia.org` and `en.wikipedia.org` (footage licenses) — 403. **No footage
   candidate can be listed: I cannot read a license off an item page, and asserting "CC-BY-SA"
   from memory is exactly as unacceptable as inventing a price.**
9. Headless Chromium as a fetch fallback — same tunnel, same denial. The mandated original
   research artifact (`assets/2016-listing.png`, a screenshot of the archived listing) is
   therefore **impossible to produce** in this session. Gate C1 cannot be satisfied.

## 5. Why I did not write a placeholder `evidence.json`

An `evidence.json` full of `null`s, or one carrying search-derived numbers marked
`estimated: true`, is more dangerous than no file. Downstream agents treat the presence of the
file as "research happened," and the likeliest repair is someone filling the gaps with plausible
figures. **An absent file cannot be mistaken for research.** The absence is the signal.

For the same reason I am **not** proposing a substitute artifact. Every alternative on the slate
(`ssd-per-terabyte`, `solar-per-watt`, `genome-sequencing`, the reserves) depends on Wayback,
BLS/FRED, NREL or NHGRI — all behind the identical blanket denial. Swapping the artifact does not
route around an egress policy; it just relocates the same failure. **This is a slate-wide block,
not an episode-specific one.**

## 6. What unblocks this (allowlist request)

Re-run this agent unchanged once these hosts are permitted for CONNECT:

| Host | Needed for |
|---|---|
| `web.archive.org`, `archive.org` | the 2016 primary source **and** the artifact screenshot; also footage |
| `www.bls.gov`, `data.bls.gov`, `download.bls.gov` | the CPI television item series ID + values |
| `fred.stlouisfed.org` | FRED fallback for the same series |
| `www.bestbuy.com`, `www.walmart.com`, `www.amazon.com` | 2026 same-day prices, two retailers |
| `www.rtings.com`, `www.cnet.com`, `www.techradar.com` | contemporaneous 2016 secondary with price in body |
| `commons.wikimedia.org` | footage candidates + licenses |

Note `web.archive.org` needs fixing at **two** layers: the egress policy *and* the WebFetch
tool-level refusal. Chromium must also be able to reach it, or the artifact screenshot stays
impossible even if WebFetch starts working.

## 7. Leads for the next run (UNVERIFIED — do not cite, re-derive from source)

Candidate 2016 55" 4K models to look up in Wayback, surfaced by search result *titles* only.
Treat every one as unconfirmed until an archived listing is opened and quoted:

- Samsung **UN55KU6300** (2016 mainstream 4K LED) — Best Buy SKU `5147600`, Walmart item
  `51500799` appeared in result titles. Strongest like-for-like candidate: mainstream 4K LED,
  not flagship, not budget.
- Vizio **E55-D0** — **caution: search results describe this as 1080p, not 4K.** If used, the
  4K E-series sibling must be identified instead. This is the like-for-like trap for this episode.
- Vizio **M55-C2** — described in a result title as 55" 4K, but 2015-era; check the model year.

Series-ID leads to resolve on bls.gov (contradictory in search, both suspect):
`CUSR0000SERA01` vs `CUSR0000SERA02`. The TV **hardware** item series is what this episode needs;
`SERA02` looks like a **service** index and would be the wrong number.

Cause hypotheses from the brief, **entirely unverified**: LCD panel oversupply / manufacturing
scale, versus ad-subsidised smart-TV economics (ACR data revenue offsetting hardware margin).
Both need fetched sources before either can be named as `primary_cause`. I have deliberately not
picked one, because picking a cause I cannot source is the same error as quoting a price I cannot
source.

## 8. Verdict on the episode

**Not shippable today.** The STILL CHEAP hypothesis is neither confirmed nor refuted — it is
untested. Re-run after the allowlist change; expected to complete normally, since the
research path itself is sound and the artifact is well chosen.
