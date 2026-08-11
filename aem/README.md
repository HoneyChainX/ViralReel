# AEM — price database, ready to publish

The founder chose AEM to host the price database (`docs/DECISIONS.md` D6). Everything that can
be built without a live instance **is built**. Publishing is three calls once auth resolves.

## Current blocker — auth, not absence

Diagnosed 2026-08-03, in this order:

| Probe | Result |
|---|---|
| `list-aem-environments` (×2) | "No AEM environments found for the current access token" |
| `core-context-management-widget` (org lookup) | **"Could not determine organization from token. Please re-authenticate."** |
| sandboxes | "User ID or org ID is invalid" |

AEM environments are scoped to an **IMS organization**. The token resolves **no org**, so no
environment can be listed — the environment list is empty *because* the org is unknown, not
because AEM is necessarily unprovisioned. The `Adobe Journey Optimizer` connector reporting
"requires authentication" in the same session is corroborating: the whole Adobe *enterprise*
auth family is stale, while the *Creative Cloud* connector (a separate entitlement) works fine.

### Two ways to unblock — either is enough

1. **Re-authenticate the Adobe enterprise connectors** in claude.ai connector settings (Adobe
   Experience Manager, and Journey Optimizer while you are there). The error asks for this
   explicitly. Then `list-aem-environments` should return your author URL.
2. **Hand over the author URL directly** — `read-api` and `write-api` both accept `aemUrl` as a
   parameter, so a URL **bypasses discovery entirely**. Find it in Adobe Experience Cloud → the
   AEM card → the address bar; it looks like `author-p12345-e67890.adobeaemcloud.com`.

## What is already built

| File | What it is |
|---|---|
| `price-pair-model.json` | Content Fragment Model for one verified price pair |
| `price-pairs/four-k-tv--entry.json` | Episode 001 entry tier — $699.99 → $319.96, 6 sources |
| `price-pairs/four-k-tv--premium.json` | Episode 001 premium tier — $1,799 → $1,297.99 |
| `price-pairs/_write-api-calls.md` | Generated `write-api` call per payload |
| `../scripts/aem_push_pricedb.py` | Regenerates payloads from any episode's `evidence.json` |

Payload shapes come from the **live spec**, read via `lookup-api-spec` (which needs no
environment): `POST /adobe/sites/cf/fragments/create` requires `title`, `parentPath`, `modelId`;
`fields` is an array of `{name, type, values[]}`.

### Two things the model does that a flat table cannot

- **`sourcesJson` is required.** The two-independent-sources-with-one-primary rule
  (`docs/05-compliance.md` Rule 2) becomes a *schema constraint* — an under-sourced pair cannot
  be authored. That extends gate check C2's guarantee from the video pipeline to the public data.
- **`anchorPriceKind` / `currentPriceKind` are enumerations.** The MSRP-vs-street asterisk becomes
  structured data instead of a footnote someone can quietly drop.

`aem_push_pricedb.py` enforces the same rule before emitting: it **refuses** any pair whose
claims lack two sources with at least one primary. Episode 001: 2 emitted, 0 refused.

## The publish sequence — three calls

Run these with the AEM connector once you have `<AUTHOR_URL>`.

**1 — create the model** (returns the `modelId` everything else needs)
```
write-api(aemUrl: "<AUTHOR_URL>", code: `
  const model = <contents of aem/price-pair-model.json>;
  return await aem.post('/adobe/sites/cf/models', model);
`)
```

**2 — regenerate payloads with the real model id, then create both fragments**
```bash
python3 scripts/aem_push_pricedb.py --model-id <MODEL_ID_FROM_STEP_1>
```
```
write-api(aemUrl: "<AUTHOR_URL>", code: `
  const entry   = <contents of aem/price-pairs/four-k-tv--entry.json>;
  const premium = <contents of aem/price-pairs/four-k-tv--premium.json>;
  const a = await aem.post('/adobe/sites/cf/fragments/create', entry);
  const b = await aem.post('/adobe/sites/cf/fragments/create', premium);
  return {a, b};
`)
```

**3 — publish model + fragments to the delivery tier**
```
write-api(aemUrl: "<AUTHOR_URL>", code: `
  return await aem.post('/adobe/sites/cf/models/publish', {ids: ['<MODEL_ID>']});
`)
```
Then publish the fragments themselves (the spec's Publishing & Unpublishing group), and the
GraphQL delivery API serves the database — which was the point of choosing AEM: a structured,
queryable, publicly-citable price index rather than a hand-rolled page.

## Then

Add one line per aired episode by re-running the emitter — it reads `evidence.json`, so the
database grows automatically as episodes air, and D6's off-platform hedge against the one
Fatal-rated risk goes live.
