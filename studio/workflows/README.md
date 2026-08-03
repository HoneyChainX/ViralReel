# studio/workflows/

Approved generative looks, stored as ComfyUI graph JSON — one file per look, named
`<project>-<look>-v<N>.json`, each committed alongside a short sidecar note
(`<same-name>.md`) recording: model + checkpoint, key settings, a reference output path,
and who approved it.

A look that exists only as prompt folklore is not reproducible; a graph is. Pin per-project
workflow versions the way `config/platform.yaml` pins vendor refs — `gen-supervisor` owns
this directory (charter: `.claude/agents/gen-supervisor.md`).

Empty at platform bring-up: the first entries arrive with the first generative project.
