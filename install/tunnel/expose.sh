#!/usr/bin/env bash
# Publish the studio connector at a public HTTPS URL, without opening a port.
#
#   bash install/tunnel/expose.sh --tailscale     # no domain needed
#   bash install/tunnel/expose.sh --cloudflare    # needs a domain on Cloudflare
#   bash install/tunnel/expose.sh --status
#   bash install/tunnel/expose.sh --off
#
# claude.ai reaches a custom connector from Anthropic's cloud, not from your
# laptop — so a tailnet-only address or a LAN IP cannot work by construction.
# The server itself stays bound to 127.0.0.1; both tunnels below proxy to
# loopback, so nothing is ever exposed on the local network either.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PORT="${VIRALREEL_MCP_PORT:-8787}"

say()  { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; }
warn() { printf '  \033[33mWARN\033[0m  %s\n' "$1"; }
die()  { printf '  \033[31mFAIL\033[0m  %s\n' "$1" >&2; exit 1; }

next_steps() {
  local url="$1"
  cat <<EOF

  Public URL:  $url
  Connector:   $url/mcp

  1. Point the service at it and restart:

       sudo bash install/services/install-services.sh --with-connector \\
            --public-url "$url"

  2. In Claude: Settings > Connectors > Add custom connector
     Paste:  $url/mcp

  3. Claude sends you to $url/consent — enter the studio passphrase
     (set it with: server/.venv/bin/python server/studio_auth.py set-passphrase)

  The URL is baked into the OAuth metadata. If it changes, redo step 1 and
  re-add the connector, or Claude's stored registration will point nowhere.
EOF
}

# ── tailscale funnel ────────────────────────────────────────────────────────

do_tailscale() {
  command -v tailscale >/dev/null 2>&1 || die \
    "tailscale not installed. https://tailscale.com/download/linux"

  local st
  st="$(tailscale status --json 2>/dev/null)" || die "tailscale is not running — try: sudo tailscale up"
  echo "$st" | grep -q '"BackendState": *"Running"' || die "tailscale is not connected — run: sudo tailscale up"

  local dns
  dns="$(echo "$st" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print((d.get('Self') or {}).get('DNSName','').rstrip('.'))" 2>/dev/null)"
  [ -n "$dns" ] || die "could not read this machine's MagicDNS name — enable MagicDNS in the admin console"

  say "Enabling Funnel on 443 -> 127.0.0.1:$PORT"
  # --bg or it dies with the shell; Funnel only accepts 443/8443/10000 and only
  # proxies to 127.0.0.1, which is exactly how the service is bound.
  if ! tailscale funnel --bg --https=443 "http://127.0.0.1:${PORT}"; then
    cat >&2 <<'EOF'
  Funnel refused. The usual causes, in order:
    1. HTTPS certificates are off: admin console > DNS > enable HTTPS.
       Note this publishes the machine name to public certificate transparency
       logs, so rename the node first if that matters.
    2. The funnel node attribute is not in your policy: admin console >
       Access controls > Funnel > "Add Funnel to policy".
    3. Funnel is not available on this plan or node.
EOF
    exit 1
  fi
  ok "funnel is up"
  next_steps "https://${dns}"
}

# ── cloudflare tunnel ───────────────────────────────────────────────────────

do_cloudflare() {
  command -v cloudflared >/dev/null 2>&1 || die \
    "cloudflared not installed. https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"

  if [ -n "${CLOUDFLARE_TUNNEL_TOKEN:-}" ]; then
    say "Running the named tunnel from CLOUDFLARE_TUNNEL_TOKEN"
    warn "this runs in the foreground; install it as a service to survive a reboot"
    exec cloudflared tunnel run --token "$CLOUDFLARE_TUNNEL_TOKEN"
  fi

  cat <<EOF

  A Cloudflare named tunnel needs a domain already on Cloudflare. There is no
  free named-tunnel path without one — if you do not have a domain, use
  --tailscale instead, which needs none.

  1. Dashboard > Networking > Tunnels > Create tunnel. Copy the token.
  2. Route it:  Published application
                Hostname     studio.yourdomain.com
                Service URL  http://localhost:$PORT
  3. Run it here:
         export CLOUDFLARE_TUNNEL_TOKEN=...
         bash install/tunnel/expose.sh --cloudflare

  Then follow the connector steps with https://studio.yourdomain.com

  Two limits that matter and are already designed around:
    * the proxy read timeout is 125s (HTTP 524) — every studio tool returns
      immediately and long work goes to the queue, so this never bites
    * Cloudflare's terms reserve the right to limit free accounts serving
      video, which is why finished films still ship as a GitHub release link
      rather than being downloaded through the tunnel
EOF
}

# ── status / off ────────────────────────────────────────────────────────────

do_status() {
  say "Local server"
  if curl -sf -o /dev/null "http://127.0.0.1:${PORT}/.well-known/oauth-authorization-server"; then
    ok "connector answering on 127.0.0.1:${PORT} with OAuth metadata"
  elif curl -sf -o /dev/null "http://127.0.0.1:${PORT}/mcp" 2>/dev/null; then
    warn "something is on ${PORT} but serves no OAuth metadata — started without --public-url?"
  else
    warn "nothing answering on 127.0.0.1:${PORT} (systemctl status viralreel-mcp)"
  fi

  if command -v tailscale >/dev/null 2>&1; then
    say "Tailscale Funnel"
    tailscale funnel status 2>&1 | sed 's/^/  /' || true
  fi
  if command -v cloudflared >/dev/null 2>&1; then
    say "cloudflared"
    pgrep -a cloudflare[d] | sed 's/^/  /' || echo "  not running"
  fi
}

do_off() {
  if command -v tailscale >/dev/null 2>&1; then
    tailscale funnel --https=443 off 2>/dev/null && ok "funnel off" || warn "no funnel was running"
  fi
  pkill -f 'cloudflare[d] tunnel run' 2>/dev/null && ok "cloudflared stopped" || true
  echo ""
  echo "  The connector is now unreachable from the internet. Claude will show it"
  echo "  as failing until it is exposed again; the queue and Remote Control are"
  echo "  unaffected."
}

case "${1:---status}" in
  --tailscale)  do_tailscale ;;
  --cloudflare) do_cloudflare ;;
  --status)     do_status ;;
  --off)        do_off ;;
  -h|--help)    sed -n '2,12p' "$0" ;;
  *) die "unknown option: $1  (--tailscale | --cloudflare | --status | --off)" ;;
esac
