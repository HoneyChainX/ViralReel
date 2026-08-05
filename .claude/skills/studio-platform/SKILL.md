---
name: studio-platform
description: Operate the studio platform — list/install/verify/pin the 42-module manifest (config/platform.yaml), run the doctor, launch bounded ralph loops, and follow the install doctrine (CPU-torch routes, SHA pins, paid-modules-off). Use for platform maintenance, adding modules, diagnosing broken vendor tools, or when the user invokes /studio-platform. The pipeline-td agent's workflow, packaged.
---

You are operating the studio platform (docs/10-platform.md). The manifest
`config/platform.yaml` is the single source of truth; vendors clone to `vendor/<id>`,
never forked, never patched — configuration happens from outside.

## Commands

```
python3 scripts/studio/platform.py list [--profile X]     # what exists, what's enabled
bash scripts/studio/install.sh --profile X                # install a profile's modules
bash scripts/studio/doctor.sh --profile all               # verify — loud on purpose
python3 scripts/studio/platform.py pin --profile X        # SHA-pin verified installs
make ralph JOB=platform-install                           # bounded loop finishes the job
python3 -m unittest tests.test_platform                   # manifest invariants
```

## Doctrine (hard rules, enforced by loader + tests)
- `cost: paid` modules MUST ship `enabled: false` — paid connectors are per-project
  founder decisions, never defaults.
- `install: desktop` modules are human-installed; installer skips, doctor doesn't gate.
- Refs stay `main` until a verified install, then pin the exact SHA with a dated
  comment. Pip-only modules (bpy, usd-core) legitimately stay `main` — nothing to pin.
- **CPU-torch route**: any module whose deps pull torch gets
  `pip install torch --index-url https://download.pytorch.org/whl/cpu` FIRST in its
  install_cmd (full CUDA torch is ~6GB and has exhausted this host before).
- A red doctor check is fixed or the module disabled with a dated note — never muted.
- New modules require: a research entry in docs/11 (license verified at source, not
  from aggregators), an owning agent, and profile placement.

## Adding a module (the sweep pattern)
1. Verify repo/license/maintenance at the source (docs/11 records seven sweeps of
   precedent — including SEO farms fabricating releases; trust nothing unverified).
2. Manifest entry with role, license, cost, gpu, headless, install, doctor checks,
   and notes naming the owning agent.
3. Install → verify import/CLI → doctor green → pin → tests → commit with the
   research recorded in docs/11.

## Disk discipline (ephemeral hosts)
Session disk is a fixed allowance. Before big installs: clear pip/npm caches, prefer
`--no-cache-dir`, delete regenerable render intermediates. The doctor's job is truth;
yours is not to let the host lie to it.
