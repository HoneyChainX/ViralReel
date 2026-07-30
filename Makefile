.PHONY: help setup doctor test episode gate publish clean-vendor

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

# Refuses to run unless gate.json says PASS. There is deliberately no --force.
publish:
	@test -n "$(SLUG)" || (echo "usage: make publish SLUG=<slug>"; exit 1)
	@python3 scripts/gate.py --slug $(SLUG) --require-pass
	@cd vendor/yt-agent && node -e "console.log('handing $(SLUG) to youtube-automation-agent (privacy=private)')"
	@echo "Uploaded PRIVATE. A human flips it public — see docs/05-compliance.md C10."

clean-vendor:
	rm -rf vendor
