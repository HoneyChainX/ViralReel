#!/bin/bash
# SessionStart hook: install the Claude Code plugin set into remote (web)
# session containers. Containers start clean, so plugins must be reinstalled;
# both `marketplace add` and `plugin install` are idempotent, and the container
# state is cached after the hook completes, so re-runs are near-instant.
#
# This hook is replicated across the HoneyChainX repos. Multi-repo sessions run
# every repo's copy, so the marker below lets whichever copy runs first do the
# work and the rest exit instantly.
set -uo pipefail

# Local machines manage their own plugins — only run on Claude Code on the web.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Bump the version when the plugin list changes so already-cached containers
# pick up the new set on their next session.
PLUGINS_VERSION=1
MARKER="$HOME/.claude/.plugins-bootstrap-v$PLUGINS_VERSION"
if [ -f "$MARKER" ]; then
  exit 0
fi

failed=()

add_marketplace() {
  claude plugin marketplace add "$1" || failed+=("marketplace:$1")
}

install_plugin() {
  claude plugin install "$1" || failed+=("$1")
}

add_marketplace anthropics/claude-plugins-official
add_marketplace anthropics/knowledge-work-plugins

for p in \
  frontend-design superpowers playwright feature-dev vercel figma \
  chrome-devtools-mcp telegram huggingface-skills cloudflare \
  code-modernization shopify-ai-toolkit; do
  install_plugin "$p@claude-plugins-official"
done

# These two are not in claude-plugins-official; they live in knowledge-work-plugins.
for p in searchfit-seo product-tracking-skills; do
  install_plugin "$p@knowledge-work-plugins"
done

if [ "${#failed[@]}" -gt 0 ]; then
  # Leave no marker so the next session retries the failed installs.
  echo "WARNING: some plugin installs failed: ${failed[*]}" >&2
else
  mkdir -p "$(dirname "$MARKER")"
  touch "$MARKER"
fi

# Never block session start on a failed install — plugins are a convenience.
exit 0
