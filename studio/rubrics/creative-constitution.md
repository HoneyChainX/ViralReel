# The Creative Constitution

Principles every critique loop in this studio judges against — the studio-specific
"constitution" pattern (docs/11 §7). Generator agents draft; critic agents (or the same
agent in a second, adversarial pass) score the draft against these articles and return
structured objections; the draft is revised until the objections are empty or a human
gate decides. Mechanical style violations are `style-rules.yaml`'s job — this file is
for judgment.

## Articles

1. **Specificity beats intensity.** "A camel's shadow stretching across cooling sand"
   beats "an epic desert vista". If a line could caption anyone's video, it isn't ours.
2. **One idea per beat.** A beat that needs "and" twice is two beats; split it or cut one.
3. **The number is the star** (research formats): every creative choice frames the fact,
   never competes with it. On fiction formats: the dramatic question is the star.
4. **Contrast is craft.** Wall-to-wall anything — sound, motion, color, cuts — is the
   synthetic tell. Every piece needs a chosen rest: the silence, the still, the wide.
5. **Earn every transition.** A cut is the default and needs no defense; anything
   fancier must mean something (time, world, register). Decoration is not meaning.
6. **Details are load-bearing.** Foley that lands, captions clear of faces, odometer
   digits that align, a join nobody finds — audiences can't name these, but they feel
   their absence. No detail is below the studio's attention.
7. **Refuse the average.** When a draft matches what any competent generator would
   produce from the same brief, it is not done. Find the choice only this studio, with
   this evidence and this format, would make.
8. **Critique is specific or it is noise.** An objection must name the beat, the article
   violated, and a concrete fix direction. "Make it better" is banned from critic output.

## Loop contract (Self-Refine pattern, bounded)

- Maximum 3 revision rounds; unresolved objections escalate to the owning human gate.
- Critic output is structured: `{beat, article, objection, suggested_direction}`.
- The critic never rewrites — rewriting is the generator's job. One owner per artifact.
- A pass with zero objections still records WHAT was strongest — praise is calibration
  data for the next brief, not politeness.
