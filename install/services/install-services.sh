#!/usr/bin/env bash
# Install the studio's systemd units so the box behaves like a server.
#
#   sudo bash install/services/install-services.sh            # jobd only
#   sudo bash install/services/install-services.sh --with-remote-control
#   sudo bash install/services/install-services.sh --uninstall
#
# Run it with sudo but from the operator's checkout: the units must run as the
# human who owns the repo and the claude.ai login, never as root.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UNIT_DIR=/etc/systemd/system
WITH_RC=0
UNINSTALL=0
NAME="${VIRALREEL_HOST_NAME:-viralreel-studio}"

while [ $# -gt 0 ]; do
  case "$1" in
    --with-remote-control) WITH_RC=1 ;;
    --uninstall)           UNINSTALL=1 ;;
    --name)                NAME="$2"; shift ;;
    *) echo "unknown flag: $1" >&2; exit 2 ;;
  esac
  shift
done

say()  { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
warn() { printf '\033[33m  ! %s\033[0m\n' "$1"; }
die()  { printf '\033[31m  ✗ %s\033[0m\n' "$1" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run with sudo — units are installed into $UNIT_DIR"

# SUDO_USER is who called sudo; falling back to root would install services that
# cannot read the operator's claude.ai credentials.
TARGET_USER="${SUDO_USER:-}"
[ -n "$TARGET_USER" ] && [ "$TARGET_USER" != "root" ] \
  || die "could not determine the non-root user — run as: sudo bash $0 (not from a root shell)"
TARGET_GROUP="$(id -gn "$TARGET_USER")"

UNITS=(viralreel-jobd.service)
[ "$WITH_RC" -eq 1 ] && UNITS+=(viralreel-remote-control.service)

if [ "$UNINSTALL" -eq 1 ]; then
  say "Removing studio services"
  for u in viralreel-jobd.service viralreel-remote-control.service; do
    systemctl disable --now "$u" 2>/dev/null || true
    rm -f "$UNIT_DIR/$u"
    echo "  removed $u"
  done
  systemctl daemon-reload
  exit 0
fi

# Without systemd these files are inert. That is the difference between a render
# that survives a logout and one that does not, so refuse rather than pretend.
[ -d /run/systemd/system ] || die \
  "systemd is not running. Under WSL2: put 'systemd=true' under [boot] in /etc/wsl.conf, then run 'wsl --shutdown' from Windows and reopen the distro."

say "Installing units for user '$TARGET_USER' from $ROOT"
for u in "${UNITS[@]}"; do
  src="$ROOT/install/services/$u"
  [ -f "$src" ] || die "missing unit template: $src"
  sed -e "s|__USER__|$TARGET_USER|g" \
      -e "s|__GROUP__|$TARGET_GROUP|g" \
      -e "s|__ROOT__|$ROOT|g" \
      -e "s|__NAME__|$NAME|g" \
      "$src" > "$UNIT_DIR/$u"
  chmod 0644 "$UNIT_DIR/$u"
  echo "  installed $u"
done

systemctl daemon-reload
for u in "${UNITS[@]}"; do
  systemctl enable "$u" >/dev/null 2>&1 && echo "  enabled  $u"
done

say "Starting the job worker"
systemctl restart viralreel-jobd.service
sleep 2
if systemctl is-active --quiet viralreel-jobd.service; then
  echo "  viralreel-jobd is running"
else
  warn "viralreel-jobd did not stay up — journalctl -u viralreel-jobd -n 40"
fi

if [ "$WITH_RC" -eq 1 ]; then
  say "Remote Control"
  # The login is interactive and cannot be scripted; starting the service before
  # it exists just produces a restart loop, so check first and say so plainly.
  if sudo -u "$TARGET_USER" test -d "/home/$TARGET_USER/.claude"; then
    systemctl restart viralreel-remote-control.service
    sleep 3
    systemctl is-active --quiet viralreel-remote-control.service \
      && echo "  running — find the session at claude.ai/code" \
      || warn "did not stay up — journalctl -u viralreel-remote-control -n 40"
  else
    warn "no ~/.claude for $TARGET_USER yet. Log in first, then start the service:"
    echo "      cd $ROOT && claude      # then /login, and accept the trust prompt"
    echo "      sudo systemctl start viralreel-remote-control"
  fi
fi

cat <<EOF

Installed. Useful from here:

  systemctl status viralreel-jobd
  journalctl -u viralreel-jobd -f
  python3 scripts/studio/jobd.py enqueue doctor
  python3 scripts/studio/jobd.py list

EOF
