# platform-install backlog
One unchecked item per iteration. Add discoveries as new items; never delete history.

- [ ] Run `bash scripts/studio/install.sh --profile core` and fix whatever breaks first
- [ ] Verify OpenMontage + yt-agent (legacy `make setup` path) still install cleanly alongside the platform tree
- [ ] Install `distribution` profile modules and smoke-test each headless driver
- [ ] Install `genai` profile modules to code+config level (GPU smoke tests only if a GPU exists)
- [ ] Install `animation` profile modules to code+config level
- [ ] Run `bash scripts/studio/doctor.sh` end to end; file one new item per red check above this line
- [ ] Run `make test` — the gate suite must still pass untouched
