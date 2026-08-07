---
name: animation-principles
description: Evaluate and direct animation against the twelve classic principles (Disney's Illusion of Life) — squash & stretch, anticipation, staging, arcs, timing, secondary action, appeal and the rest — as a review rubric for keyframes, generated motion, and 3D animation. Use when reviewing or briefing any animated shot, diagnosing why motion feels dead/floaty/uncanny, or when the user invokes /animation-principles. The animation-director's review rubric, packaged.
---

You are reviewing motion against the twelve principles — not as trivia, but as a
diagnostic: when a shot feels wrong, one of these is usually the reason. Name the
principle, the beat, and the fix direction (critique contract: `{beat, principle,
objection, direction}` — same shape as the creative constitution's loop).

## The twelve, as diagnostics

1. **Squash & stretch** — volume-preserving deformation sells weight. Rigid objects in
   motion read as sliding cutouts. Fix: deform on impact/launch, keep volume constant.
2. **Anticipation** — action without wind-up reads as teleporting. Every major action
   gets a counter-move first (crouch before jump, pull-back before dash).
3. **Staging** — one idea readable at a time; silhouette test: does the pose read in
   solid black? If two things move at once, the eye misses both.
4. **Straight-ahead vs pose-to-pose** — fluid chaos (fire, water) animates straight
   ahead; performance animates pose-to-pose with breakdowns. Wrong method = mushy acting
   or stiff physics.
5. **Follow-through & overlapping action** — nothing stops all at once: hair, cloth,
   soft mass settle AFTER the body. Dead stops are the #1 synthetic tell.
6. **Slow in / slow out** — ease curves, not linear velocity. Linear moves read as
   mechanical; our house default is sine ease unless the action demands snap.
7. **Arcs** — living things move in arcs, not straight lines. Check wrists, heads,
   ball paths; a straight-line limb path is a rig or keyframe bug.
8. **Secondary action** — a supporting movement that enriches the main one (a tail
   flick during a walk) without stealing staging. Missing it = lifeless; overdone =
   noise (see the constitution's contrast article).
9. **Timing** — frame counts ARE the acting: fewer frames = snappy/light, more =
   heavy/deliberate. A weight problem is a timing problem before it's a pose problem.
10. **Exaggeration** — push past reference reality to read at a glance; at Shorts
    resolution and 200 ms attention, subtlety is invisibility.
11. **Solid drawing / solid posing** — forms have volume and weight in space; twinning
    (perfect symmetry) kills life. In 3D: check from a second camera angle.
12. **Appeal** — clarity + charisma of design in the pose itself. If a still frame
    isn't interesting, motion won't save it.

## House applications

- **Programmatic motion (Remotion/GSAP)**: principles 2, 5, 6, 9 are directly
  encodable — anticipation offsets, overlap staggers, ease curves, frame-count timing.
  The gsap-* and hyperframes motion-doctrine skills carry the implementation grammar;
  this skill is WHY.
- **Generated video (gen-supervisor's lane)**: use as a shot-review rubric — engines
  most often fail 5 (dead stops), 7 (linear drift), and 12 (mushy silhouettes).
- **3D (bpy lane)**: keyframe interpolation defaults to sine ease-in-out; check arcs
  with motion paths; twinning check from a second camera.
- Review output is structured objections, max 3 revision rounds, escalate to the
  founder's gate after — per the creative constitution's loop contract.
