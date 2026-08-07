#!/usr/bin/env python3
"""OAuth 2.1 for the studio connector — the lock on the front door.

claude.ai will only add a custom connector that either speaks OAuth or has no
authentication at all. Authless is not a real option here: the server can start
renders and read the repo on somebody else's personal computer, and anyone who
learned the URL could drive it. So this module makes the studio its own
authorization server.

The model is deliberately single-owner. There are no accounts, no signup, no
user table — one passphrase, set at install time, held as a scrypt hash. When
Claude sends you to the consent page you type it, and that is the whole login.
A second person is not a feature this needs, and every account system is another
thing that can be wrong on a machine nobody is watching.

What the MCP SDK already does, and this module therefore does not repeat:
verifying the PKCE S256 challenge, validating redirect URIs against what the
client registered, serving the protected-resource and authorization-server
metadata, and mounting /authorize, /token, /register and /revoke.

What this module owns: storage, the consent step, and token lifetime.

    python3 server/studio_auth.py set-passphrase     # interactive, at install
    python3 server/studio_auth.py status
    python3 server/studio_auth.py revoke-all
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    OAuthAuthorizationServerProvider,
    RefreshToken,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

ROOT = Path(__file__).resolve().parents[1]
# Overridable so the test suite never touches the real credential store, and so
# an operator can keep it off a synced or backed-up path if they want to.
DB_PATH = Path(os.environ.get("VIRALREEL_AUTH_DB") or (ROOT / "var" / "auth.db"))

# An access token is cheap to refresh and expensive to leak, so it is short.
ACCESS_TTL = 3600            # 1 hour
REFRESH_TTL = 30 * 24 * 3600  # 30 days
CODE_TTL = 300               # 5 minutes — an authorization code is a one-shot
CONSENT_TTL = 900            # a consent page left open all afternoon is stale

# A passphrase prompt reachable from the public internet is a brute-force target.
MAX_FAILURES = 8
LOCKOUT_SECONDS = 900

SCHEMA = """
CREATE TABLE IF NOT EXISTS owner (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  salt BLOB NOT NULL,
  hash BLOB NOT NULL,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS clients (
  client_id TEXT PRIMARY KEY,
  data      TEXT NOT NULL,
  created_at REAL NOT NULL
);
-- Codes and tokens are stored as SHA-256 digests. A copy of this database is
-- then a list of what exists, not a set of working credentials.
CREATE TABLE IF NOT EXISTS codes (
  code_hash TEXT PRIMARY KEY,
  data      TEXT NOT NULL,
  expires_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS tokens (
  token_hash TEXT PRIMARY KEY,
  kind       TEXT NOT NULL,          -- access | refresh
  client_id  TEXT NOT NULL,
  data       TEXT NOT NULL,
  expires_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS pending (
  req_id     TEXT PRIMARY KEY,
  data       TEXT NOT NULL,
  expires_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS failures (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS tokens_client ON tokens(client_id);
"""


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    fresh = not DB_PATH.exists()
    c = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA busy_timeout=30000")
    c.executescript(SCHEMA)
    if fresh:
        # It holds the credential that guards the machine; nobody else needs read.
        try:
            os.chmod(DB_PATH, 0o600)
        except OSError:
            pass
    return c


# ── the owner's passphrase ──────────────────────────────────────────────────

def set_passphrase(passphrase: str) -> None:
    if len(passphrase) < 12:
        raise ValueError("use at least 12 characters — this is reachable from the internet")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(passphrase.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    with connect() as c:
        c.execute("DELETE FROM owner")
        c.execute("INSERT INTO owner(id, salt, hash, created_at) VALUES (1,?,?,?)",
                  (salt, digest, time.time()))


def has_passphrase() -> bool:
    with connect() as c:
        return c.execute("SELECT 1 FROM owner WHERE id=1").fetchone() is not None


def _locked_out() -> int:
    """Seconds remaining in a lockout, or 0."""
    cutoff = time.time() - LOCKOUT_SECONDS
    with connect() as c:
        c.execute("DELETE FROM failures WHERE at < ?", (cutoff,))
        n = c.execute("SELECT COUNT(*) AS n FROM failures").fetchone()["n"]
        if n < MAX_FAILURES:
            return 0
        oldest = c.execute("SELECT MIN(at) AS a FROM failures").fetchone()["a"]
    return max(1, int(LOCKOUT_SECONDS - (time.time() - oldest)))


def check_passphrase(candidate: str) -> bool:
    if _locked_out():
        return False
    with connect() as c:
        row = c.execute("SELECT salt, hash FROM owner WHERE id=1").fetchone()
    if not row:
        return False
    digest = hashlib.scrypt(candidate.encode(), salt=row["salt"],
                            n=2**14, r=8, p=1, dklen=32)
    ok = hmac.compare_digest(digest, row["hash"])
    with connect() as c:
        if ok:
            c.execute("DELETE FROM failures")
        else:
            c.execute("INSERT INTO failures(at) VALUES (?)", (time.time(),))
    return ok


# ── the provider ────────────────────────────────────────────────────────────

class StudioAuthProvider(OAuthAuthorizationServerProvider):
    """Single-owner authorization server backed by SQLite."""

    def __init__(self, issuer_url: str):
        self.issuer_url = issuer_url.rstrip("/")

    # -- clients ------------------------------------------------------------

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        with connect() as c:
            row = c.execute("SELECT data FROM clients WHERE client_id=?",
                            (client_id,)).fetchone()
        if not row:
            return None
        return OAuthClientInformationFull.model_validate_json(row["data"])

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        # Dynamic registration is open by design: it is how Claude introduces
        # itself, and registering a client grants nothing on its own. The
        # passphrase at the consent step is what actually authorises anything.
        with connect() as c:
            c.execute(
                "INSERT OR REPLACE INTO clients(client_id, data, created_at) VALUES (?,?,?)",
                (client_info.client_id, client_info.model_dump_json(), time.time()))

    # -- authorize ----------------------------------------------------------

    async def authorize(self, client: OAuthClientInformationFull,
                        params: AuthorizationParams) -> str:
        """Park the request and send the browser to our own consent page.

        Returning a URL rather than a code is the whole point: the human has to
        appear and prove they are the owner before any code exists.
        """
        req_id = secrets.token_urlsafe(24)
        payload = {
            "client_id": client.client_id,
            "client_name": (client.client_name or client.client_id),
            "redirect_uri": str(params.redirect_uri),
            "redirect_uri_provided_explicitly": params.redirect_uri_provided_explicitly,
            "code_challenge": params.code_challenge,
            "state": params.state,
            "scopes": params.scopes or [],
            "resource": params.resource,
        }
        with connect() as c:
            c.execute("DELETE FROM pending WHERE expires_at < ?", (time.time(),))
            c.execute("INSERT INTO pending(req_id, data, expires_at) VALUES (?,?,?)",
                      (req_id, json.dumps(payload), time.time() + CONSENT_TTL))
        return f"{self.issuer_url}/consent?{urlencode({'req': req_id})}"

    def load_pending(self, req_id: str) -> dict | None:
        with connect() as c:
            row = c.execute("SELECT data, expires_at FROM pending WHERE req_id=?",
                            (req_id,)).fetchone()
        if not row or row["expires_at"] < time.time():
            return None
        return json.loads(row["data"])

    def complete_consent(self, req_id: str) -> str | None:
        """Owner proved themselves: mint the code and return the redirect URL."""
        pending = self.load_pending(req_id)
        if not pending:
            return None
        code = secrets.token_urlsafe(32)
        record = {
            "scopes": pending["scopes"],
            "client_id": pending["client_id"],
            "code_challenge": pending["code_challenge"],
            "redirect_uri": pending["redirect_uri"],
            "redirect_uri_provided_explicitly": pending["redirect_uri_provided_explicitly"],
            "resource": pending["resource"],
        }
        with connect() as c:
            c.execute("DELETE FROM pending WHERE req_id=?", (req_id,))
            c.execute("INSERT INTO codes(code_hash, data, expires_at) VALUES (?,?,?)",
                      (_digest(code), json.dumps(record), time.time() + CODE_TTL))
        query = {"code": code}
        if pending.get("state"):
            query["state"] = pending["state"]
        sep = "&" if "?" in pending["redirect_uri"] else "?"
        return f"{pending['redirect_uri']}{sep}{urlencode(query)}"

    async def load_authorization_code(self, client: OAuthClientInformationFull,
                                      authorization_code: str) -> AuthorizationCode | None:
        with connect() as c:
            row = c.execute("SELECT data, expires_at FROM codes WHERE code_hash=?",
                            (_digest(authorization_code),)).fetchone()
        if not row or row["expires_at"] < time.time():
            return None
        data = json.loads(row["data"])
        if data["client_id"] != client.client_id:
            return None
        return AuthorizationCode(code=authorization_code, expires_at=row["expires_at"], **data)

    async def exchange_authorization_code(self, client: OAuthClientInformationFull,
                                          authorization_code: AuthorizationCode) -> OAuthToken:
        # Single use. Deleting before issuing means a replay finds nothing even
        # if two requests arrive together.
        with connect() as c:
            deleted = c.execute("DELETE FROM codes WHERE code_hash=?",
                                (_digest(authorization_code.code),)).rowcount
        if not deleted:
            raise ValueError("authorization code already used")
        return self._issue(client.client_id, authorization_code.scopes,
                           authorization_code.resource)

    # -- tokens -------------------------------------------------------------

    def _issue(self, client_id: str, scopes: list[str], resource: str | None) -> OAuthToken:
        access = secrets.token_urlsafe(32)
        refresh = secrets.token_urlsafe(32)
        now = time.time()
        with connect() as c:
            c.execute(
                "INSERT INTO tokens(token_hash, kind, client_id, data, expires_at) VALUES (?,?,?,?,?)",
                (_digest(access), "access", client_id,
                 json.dumps({"scopes": scopes, "resource": resource}), now + ACCESS_TTL))
            c.execute(
                "INSERT INTO tokens(token_hash, kind, client_id, data, expires_at) VALUES (?,?,?,?,?)",
                (_digest(refresh), "refresh", client_id,
                 json.dumps({"scopes": scopes, "resource": resource}), now + REFRESH_TTL))
            c.execute("DELETE FROM tokens WHERE expires_at < ?", (now,))
        return OAuthToken(access_token=access, token_type="Bearer",
                          expires_in=ACCESS_TTL, refresh_token=refresh,
                          scope=" ".join(scopes) if scopes else None)

    async def load_refresh_token(self, client: OAuthClientInformationFull,
                                 refresh_token: str) -> RefreshToken | None:
        with connect() as c:
            row = c.execute(
                "SELECT client_id, data, expires_at FROM tokens WHERE token_hash=? AND kind='refresh'",
                (_digest(refresh_token),)).fetchone()
        if not row or row["expires_at"] < time.time() or row["client_id"] != client.client_id:
            return None
        data = json.loads(row["data"])
        return RefreshToken(token=refresh_token, client_id=row["client_id"],
                            scopes=data["scopes"], expires_at=int(row["expires_at"]))

    async def exchange_refresh_token(self, client: OAuthClientInformationFull,
                                     refresh_token: RefreshToken,
                                     scopes: list[str]) -> OAuthToken:
        # Rotation: the presented refresh token dies here. A stolen one is then
        # usable at most once, and the theft shows up as the owner being logged
        # out rather than as nothing at all.
        with connect() as c:
            row = c.execute("SELECT data FROM tokens WHERE token_hash=? AND kind='refresh'",
                            (_digest(refresh_token.token),)).fetchone()
            resource = json.loads(row["data"]).get("resource") if row else None
            c.execute("DELETE FROM tokens WHERE token_hash=?", (_digest(refresh_token.token),))
        # A refresh may narrow scope but never widen it.
        granted = [s for s in (scopes or refresh_token.scopes) if s in refresh_token.scopes]
        return self._issue(client.client_id, granted or refresh_token.scopes, resource)

    async def load_access_token(self, token: str) -> AccessToken | None:
        with connect() as c:
            row = c.execute(
                "SELECT client_id, data, expires_at FROM tokens WHERE token_hash=? AND kind='access'",
                (_digest(token),)).fetchone()
        if not row or row["expires_at"] < time.time():
            return None
        data = json.loads(row["data"])
        return AccessToken(token=token, client_id=row["client_id"], scopes=data["scopes"],
                           expires_at=int(row["expires_at"]), resource=data.get("resource"))

    async def revoke_token(self, token) -> None:
        raw = getattr(token, "token", None) or str(token)
        with connect() as c:
            c.execute("DELETE FROM tokens WHERE token_hash=?", (_digest(raw),))


# ── the consent page ────────────────────────────────────────────────────────

CONSENT_HTML = """<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ViralReel studio - authorize</title>
<style>
 body{{font:16px/1.5 system-ui,sans-serif;background:#14161a;color:#e8e8ea;
      display:flex;min-height:100vh;align-items:center;justify-content:center;margin:0}}
 .card{{background:#1d2026;padding:2rem;border-radius:12px;max-width:26rem;width:92%;
        border:1px solid #2c313a}}
 h1{{font-size:1.1rem;margin:0 0 .25rem}} p{{color:#9aa1ad;font-size:.9rem}}
 .who{{background:#262b33;padding:.6rem .8rem;border-radius:8px;margin:1rem 0;font-size:.9rem}}
 input{{width:100%;padding:.7rem;border-radius:8px;border:1px solid #39404b;
        background:#12141a;color:#e8e8ea;font-size:1rem;box-sizing:border-box}}
 button{{width:100%;padding:.7rem;margin-top:.8rem;border:0;border-radius:8px;
         background:#c96442;color:#fff;font-size:1rem;cursor:pointer}}
 .err{{color:#ff8a80;font-size:.9rem;margin-top:.7rem}}
 ul{{color:#9aa1ad;font-size:.85rem;padding-left:1.1rem}}
</style>
<div class="card">
  <h1>Authorize access to your studio</h1>
  <p>Something is asking to control this render host.</p>
  <div class="who"><strong>{client}</strong></div>
  <p>If you did not just add a connector in Claude, close this page.</p>
  <ul>
    <li>Queue and cancel jobs from a fixed allowlist</li>
    <li>Read host status, job logs, films and releases</li>
  </ul>
  <form method="post">
    <input type="hidden" name="req" value="{req}">
    <input type="password" name="passphrase" placeholder="Studio passphrase"
           autofocus autocomplete="current-password">
    <button type="submit">Authorize</button>
  </form>
  {error}
</div>
"""


def render_consent(client_name: str, req_id: str, error: str = "") -> str:
    import html
    err = f'<div class="err">{html.escape(error)}</div>' if error else ""
    return CONSENT_HTML.format(client=html.escape(client_name),
                               req=html.escape(req_id), error=err)


# ── cli ─────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("set-passphrase", help="set the owner passphrase")
    sp.add_argument("--stdin", action="store_true", help="read it from stdin instead of prompting")
    sub.add_parser("status", help="what the auth store currently holds")
    sub.add_parser("revoke-all", help="invalidate every token and registered client")

    a = ap.parse_args()

    if a.cmd == "set-passphrase":
        if a.stdin:
            value = sys.stdin.readline().strip()
        else:
            value = getpass.getpass("New studio passphrase: ")
            if value != getpass.getpass("Repeat: "):
                print("they do not match", file=sys.stderr)
                return 1
        try:
            set_passphrase(value)
        except ValueError as e:
            print(f"rejected: {e}", file=sys.stderr)
            return 1
        print("passphrase set. It is never stored in the clear and cannot be recovered —")
        print("run this again to change it.")
        return 0

    if a.cmd == "status":
        with connect() as c:
            clients = c.execute("SELECT client_id, created_at FROM clients").fetchall()
            live = c.execute(
                "SELECT kind, COUNT(*) n FROM tokens WHERE expires_at > ? GROUP BY kind",
                (time.time(),)).fetchall()
        print(f"passphrase set: {'yes' if has_passphrase() else 'NO — run set-passphrase'}")
        lock = _locked_out()
        if lock:
            print(f"LOCKED OUT for another {lock}s after repeated failures")
        print(f"registered clients: {len(clients)}")
        for row in clients:
            print(f"  {row['client_id']}")
        for row in live:
            print(f"live {row['kind']} tokens: {row['n']}")
        print(f"database: {DB_PATH}")
        return 0

    if a.cmd == "revoke-all":
        with connect() as c:
            c.execute("DELETE FROM tokens")
            c.execute("DELETE FROM codes")
            c.execute("DELETE FROM pending")
            c.execute("DELETE FROM clients")
        print("every token and client removed — reconnect the connector in Claude to re-authorize")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
