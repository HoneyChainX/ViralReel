#!/usr/bin/env python3
"""
Build AEM Content Fragment payloads for the price database from verified evidence packs.

Why this exists: the founder asked for AEM to host the price database (docs/DECISIONS.md D6).
`list-aem-environments` returns no accessible environments, so nothing can be POSTed from this
session — but the AEM work itself does not depend on that. This script converts
`content/episodes/*/evidence.json` into request bodies matching the real
`POST /adobe/sites/cf/fragments/create` contract (read from the live spec via lookup-api-spec:
required `title`, `parentPath`, `modelId`; optional `description`, `name`, `fields`).

So the moment an AEM author URL exists, publishing is one `write-api` call per payload — no
rework, no guessing endpoint shapes.

Usage:
  python3 scripts/aem_push_pricedb.py --model-id <id> [--slug four-k-tv] \
      [--parent-path /content/dam/price-archaeology/price-pairs]

Output: aem/price-pairs/<slug>--<claim-id>.json, one request body each, plus
        aem/price-pairs/_write-api-calls.md with the exact call to run per payload.

Refuses to emit a fragment for any claim with fewer than two sources or no primary source —
the same rule gate check C2 enforces on video. An under-sourced pair must not exist in the
public database either.
"""

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "aem" / "price-pairs"

# Which claim pairs form a publishable price pair, per episode. Anchor + current, same tier.
PAIRS = {
    "four-k-tv": [
        {"anchor": "c1-2016-entry-55in-4k", "current": "c2-2026-entry-55in-4k", "tier": "entry"},
        {"anchor": "c3-2016-premium-55in-4k-led", "current": "c4-2026-premium-55in-4k-led", "tier": "premium"},
    ],
}


def sources_ok(claim):
    """Rule 2: >=2 independent sources, >=1 primary. Same bar as gate check C2."""
    srcs = claim.get("sources") or []
    return len(srcs) >= 2 and any(s.get("kind") == "primary" for s in srcs)


def slim_sources(claim):
    return [
        {k: s.get(k) for k in ("url", "kind", "publisher", "quote", "accessed", "series_id")
         if s.get(k) is not None}
        for s in claim.get("sources", [])
    ]


def pct(a, b):
    return None if not a else round((b - a) / a * 100, 1)


def build(slug, model_id, parent_path):
    ep = ROOT / "content" / "episodes" / slug
    ev = json.loads((ep / "evidence.json").read_text())
    claims = {c["id"]: c for c in ev["claims"]}
    quality = claims.get("c5-bls-constant-quality-televisions", {})

    emitted, refused = [], []
    for pair in PAIRS.get(slug, []):
        a, c = claims.get(pair["anchor"]), claims.get(pair["current"])
        if not a or not c:
            refused.append(f"{pair['anchor']}/{pair['current']}: claim missing from evidence.json")
            continue
        for cl in (a, c):
            if not sources_ok(cl):
                refused.append(f"{cl['id']}: under-sourced (needs >=2 sources, >=1 primary)")
        if not (sources_ok(a) and sources_ok(c)):
            continue

        fields = [
            {"name": "slug", "type": "text", "values": [slug]},
            {"name": "productName", "type": "text", "values": [ev["object"]]},
            {"name": "category", "type": "text", "values": ["televisions"]},
            {"name": "tier", "type": "enumeration", "values": [pair["tier"]]},
            {"name": "anchorYear", "type": "number", "values": [a["year"]]},
            {"name": "anchorPrice", "type": "number", "values": [a["value"]]},
            {"name": "anchorPriceKind", "type": "enumeration", "values": ["manufacturer-msrp"]},
            {"name": "currentYear", "type": "number", "values": [c["year"]]},
            {"name": "currentPrice", "type": "number", "values": [c["value"]]},
            {"name": "currentPriceKind", "type": "enumeration", "values": ["retail-listing"]},
            {"name": "currency", "type": "text", "values": [c.get("currency", "USD")]},
            {"name": "nominalChangePct", "type": "number", "values": [pct(a["value"], c["value"])]},
            {"name": "verdict", "type": "enumeration", "values": [ev["verdict"]]},
            {"name": "causeMechanism", "type": "enumeration",
             "values": [ev.get("primary_cause", {}).get("mechanism")]},
            {"name": "sourcesJson", "type": "multiline-text",
             "values": [json.dumps(slim_sources(a) + slim_sources(c), indent=2)]},
        ]
        if a.get("inflation_adjusted_value"):
            fields += [
                {"name": "anchorPriceAdjusted", "type": "number",
                 "values": [a["inflation_adjusted_value"]]},
                {"name": "realChangePct", "type": "number",
                 "values": [pct(a["inflation_adjusted_value"], c["value"])]},
                {"name": "inflationSeriesId", "type": "text", "values": ["BLS CPI-U CUUR0000SA0"]},
            ]
        if quality:
            fields.append({"name": "qualityAdjustedSeriesId", "type": "text",
                           "values": ["BLS CUUR0000SERA01"]})
        if ev.get("spec_note"):
            fields.append({"name": "caveat", "type": "multiline-text", "values": [ev["spec_note"]]})

        name = f"{slug}--{pair['tier']}"
        body = {
            "title": f"{pair['tier'].title()} 55-inch 4K TV — {a['year']} vs {c['year']}",
            "description": f"Verified price pair from episode {slug}. Verdict: {ev['verdict']}.",
            "modelId": model_id,
            "parentPath": parent_path,
            "name": name,
            "fields": [f for f in fields if f["values"] and f["values"][0] is not None],
        }
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"{name}.json").write_text(json.dumps(body, indent=2) + "\n")
        emitted.append(name)

    return emitted, refused


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="four-k-tv")
    ap.add_argument("--model-id", required=True,
                    help="Content Fragment Model id returned by POST /adobe/sites/cf/models")
    ap.add_argument("--parent-path", default="/content/dam/price-archaeology/price-pairs")
    args = ap.parse_args()

    emitted, refused = build(args.slug, args.model_id, args.parent_path)

    for r in refused:
        print(f"  REFUSED  {r}", file=sys.stderr)
    for e in emitted:
        print(f"  emitted  aem/price-pairs/{e}.json")

    if emitted:
        calls = ["# write-api calls — one per payload\n",
                 "Run each with the AEM connector's `write-api` tool, passing your author URL:\n"]
        for e in emitted:
            calls.append(
                f"\n## {e}\n```\nwrite-api(\n  aemUrl: \"<your-author-url>\",\n  code: `\n"
                f"    const body = {json.dumps({'$ref': f'aem/price-pairs/{e}.json'})};\n"
                f"    return await aem.post('/adobe/sites/cf/fragments/create', body);\n  `\n)\n```\n")
        (OUT / "_write-api-calls.md").write_text("".join(calls))
        print(f"  emitted  aem/price-pairs/_write-api-calls.md")

    print(f"\n{len(emitted)} fragment(s) ready, {len(refused)} refused.")
    return 1 if refused and not emitted else 0


if __name__ == "__main__":
    sys.exit(main())
