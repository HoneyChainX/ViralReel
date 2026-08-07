---
name: character-bible
description: Lock character identity across generated shots with structured asset bibles — fixed CHARACTER_IDs, JSON casting sheets (demographics, micro-details, costume manifest, render syntax), the 5-part scene-composer prompt frame, and spatial separation for multi-character shots (anti prompt-bleeding). Use when creating or prompting recurring characters for any video/image generation engine, or when the user invokes /character-bible. gen-supervisor's casting-sheet charter, operationalized.
---

You are building or applying a **character bible** — the model-sheet discipline of a
real studio, translated to generation engines. Identity consistency is an owned upfront
decision, not an emergent property (gen-supervisor charter). Natural-language drift
("yellow pullover" one scene, "mustard sweater" the next) is how continuity dies; a
bible makes every term canonical.

## 1. The casting sheet (one file per character, versioned)

`studio/casting/<project>/<CHARACTER_ID>.json` — the ID is permanent (`LEO_001` style):

```json
{
  "character_id": "LEO_001",
  "demographics": { "archetype": "", "apparent_age": 0, "proportions": "" },
  "micro_details": { "hair": "", "skin_texture": "", "facial_features": "" },
  "costume_manifest": { "primary_upper": "", "primary_lower": "", "footwear": "" },
  "voice_ref": "kokoro voice id or null — locks with voice-director",
  "render_syntax": { "style": "", "depth": "" },
  "reference_images": ["path or seed refs once they exist"],
  "canon_phrases": ["the EXACT reusable strings — never paraphrase these in prompts"]
}
```

Micro-details are the drift anchors: fabric weave, freckle placement, scuff marks —
surface patterns the model can re-match across angles. Write them once, quote them
verbatim forever.

## 2. The scene composer (single character)

Every shot prompt assembles in this fixed order — never freehand:

1. **CORE SUBJECT** — inject the casting sheet's canon phrases verbatim.
2. **ACTION / EMOTION** — what the character does and feels, one beat.
3. **ENVIRONMENT / SETTING** — background, props, atmosphere.
4. **LIGHTING & CAMERA** — lens, movement, light direction (obey the project's
   cinematography bible from previs-director).
5. **TECHNICAL SUFFIX** — the render_syntax block, identical across every shot.

## 3. Multi-character shots (anti prompt-bleeding)

Feature-blending between characters is an attention problem — solve it spatially:

- **Strict spatial grouping**: anchor each character to a frame zone (`FRAME LEFT:`,
  `FRAME RIGHT:`) with their full canon block inside that zone's text only.
- **The shared anchor**: place an object/effect at `FRAME CENTER` that both relate to —
  it gives the model the interaction bridge so it doesn't invent one by blending.
- Order: GLOBAL ENVIRONMENT → character A zone → center anchor → character B zone →
  INTERACTION line → technical suffix.
- Two characters max per generated shot on current engines; more = storyboard the
  shot as a sequence of two-shots (film-editor's cut hides what attention can't hold).

## House rules

- Casting sheets lock at previs, like voice IDs lock in channel.yaml. Changes are
  versioned edits with a reason, never silent drift.
- Chains inherit the bible: every segment of a continuous shot cites the same sheet
  (continuity-supervisor's charter already requires this).
- GPU-phase reinforcement: reference images/LoRAs/IPAdapter attach to the sheet's
  `reference_images` — the sheet is the source of truth, the embedding is derived.
- Provenance law: casting sheets are for fiction lanes; nothing here touches archival
  evidence on provenance channels.
