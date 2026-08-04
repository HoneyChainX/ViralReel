# Timed-Text Style Guide (localization-director's law)

Modeled on Netflix's Timed Text Style Guides, sized for Shorts + films.

## Universal
- Reading speed: ≤ 17 chars/sec (adult), ≤ 13 chars/sec (kids' formats).
- Max 2 lines × 42 characters. Break at clause boundaries; never split a name,
  number, or price.
- In-cue within 100 ms of speech start; out-cue when the line is read or the
  speaker stops, whichever is later. Never bridge a hard cut by more than 200 ms.
- Placement: bottom-center default; move, don't cover — faces (MediaPipe check)
  and on-screen evidence (odometer, price stamps, citation chips) always win.
- Burned-in track uses brand-designer's caption type; .srt sidecars carry no styling.

## SDH (same-language, deaf & hard-of-hearing)
- Speaker IDs in caps with colon when speaker is off-screen or ambiguous.
- Sound events in brackets, present tense, specific: [waves crash], not [sound].
- Music: [gentle piano] etc.; lyrics in italics with ♪ when licensed lyrics appear.

## Machine translation honesty
- MT tracks (Argos/OPUS-MT) ship as subtitles, disclosed in the upload metadata.
- Numbers, prices, units, and proper nouns are verified against the evidence pack
  per language — never trusted to MT blind.
- A language ships only after spot-QC of 10 random cues; a bad pack is pulled, not
  patched line-by-line.
