.PHONY: help setup doctor test episode gate publish published clean-vendor \
        platform platform-doctor ralph

SHELL := /bin/bash
ROOT  := $(shell pwd)
EP    := $(ROOT)/content/episodes/$(SLUG)

help:
	@echo "Price Archaeology — studio commands"
	@echo ""
	@echo "  make setup                  clone vendors, install deps, template .env files"
	@echo "  make doctor                 verify every dependency, key and cost control"
	@echo "  make test                   gate regression suite (also runs in CI)"
	@echo "  make episode SLUG=<slug>    research -> script -> assets -> render"
	@echo "  make gate SLUG=<slug>       run the 10 compliance checks (required before publish)"
	@echo "  make publish SLUG=<slug>    upload PRIVATE via youtube-automation-agent"
	@echo ""
	@echo "  make platform PROFILE=core        install studio-platform modules (docs/10)"
	@echo "  make platform-doctor PROFILE=core verify the platform; exit 1 on any red check"
	@echo "  make ralph JOB=<job>              run a bounded ralph loop (ralph/README.md)"
	@echo ""
	@echo "Stages 3 (hook selection) and 11 (publish) stop for a human. See docs/06-runbook.md."

setup:
	@bash scripts/setup.sh

doctor:
	@bash scripts/doctor.sh

# The gate is the only thing between a bad number and YouTube. These tests
# assert every individual check on both a compliant and a seeded-violation
# episode, and that no bypass flag has been added.
test:
	@python3 -m unittest discover tests -v

# Orchestrates the studio agents. Each stage writes its artifact to
# content/episodes/$(SLUG)/ and the next stage reads it from disk —
# no verbal handoffs (docs/03-studio-team.md).
episode:
	@test -n "$(SLUG)" || (echo "usage: make episode SLUG=<slug>"; exit 1)
	@mkdir -p $(EP)/assets
	@echo "Episode workspace: $(EP)"
	@echo ""
	@echo "Run these in Claude Code, in order:"
	@echo "  1. @trend-archaeologist  build the evidence pack for $(SLUG)"
	@echo "  2. @head-of-format       approve/kill and assign segment"
	@echo "  3. @hook-writer          12 hooks          <-- YOU CHOOSE ONE"
	@echo "  4. @script-editor        95-130 word script"
	@echo "  5. @archive-sourcer      assets + licenses.json"
	@echo "  6. @motion-director      scene_plan.json"
	@echo "  7. @voice-director       vo.mp3"
	@echo "  8. @post-supervisor      render to out/$(SLUG).mp4"
	@echo "  9. make gate SLUG=$(SLUG)"

gate:
	@test -n "$(SLUG)" || (echo "usage: make gate SLUG=<slug>"; exit 1)
	@python3 scripts/gate.py --slug $(SLUG)

# Manual-first (docs/DECISIONS.md D1): verifies the gate, then prints the handoff.
# The actual upload happens in the founder's browser via handoffs/upload-episode.md.
# There is deliberately no --force.
publish:
	@test -n "$(SLUG)" || (echo "usage: make publish SLUG=<slug>"; exit 1)
	@python3 scripts/gate.py --slug $(SLUG) --require-pass
	@echo ""
	@echo "Gate PASS. Manual-first upload:"
	@echo "  1. Fill handoffs/upload-episode.md from content/episodes/$(SLUG)/packaging.json"
	@echo "  2. Hand the prompt block to Claude for Chrome (uploads PRIVATE)"
	@echo "  3. Review playback, flip public, pin the source comment"
	@echo "  4. REQUIRED: make published SLUG=$(SLUG)   <- keeps the 2/day cap real"

# Record a completed upload in the C6 log. Not optional — an unlogged upload
# makes the throughput cap blind.
published:
	@test -n "$(SLUG)" || (echo "usage: make published SLUG=<slug>"; exit 1)
	@python3 scripts/log_publish.py --slug $(SLUG)

# Studio platform (docs/10-platform.md). PROFILE defaults to the manifest's
# default (core). The doctor is loud on purpose — never pipe it to /dev/null.
platform:
	@bash scripts/studio/install.sh $(if $(PROFILE),--profile $(PROFILE),)

platform-doctor:
	@bash scripts/studio/doctor.sh $(if $(PROFILE),--profile $(PROFILE),)

# Bounded autonomous loops (ralph/README.md). Lists jobs when JOB is omitted.
ralph:
	@bash ralph/ralph.sh $(JOB) $(if $(MAX),--max $(MAX),)

clean-vendor:
	rm -rf vendor
