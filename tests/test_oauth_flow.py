"""The connector's OAuth flow, walked end to end exactly as claude.ai walks it.

This is the boundary that faces the public internet: discovery, dynamic client
registration, PKCE, the owner consent step, token exchange, refresh rotation and
revocation. An authorization server that merely works is not the interesting
half — most of the assertions below are that it *refuses*: no token, wrong
passphrase, wrong PKCE verifier, replayed code, spent refresh token, revoked
token.

It boots the real server on a loopback port and speaks raw HTTP to it, so it
exercises the SDK's handlers and our provider together rather than either alone.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The connector is optional infrastructure: without the MCP SDK installed there
# is nothing to test. CI installs it, and CI also treats a skip as a failure, so
# a skip here means the dependency silently vanished — which is what we want to
# hear about.
try:
    import httpx  # noqa: F401
    import mcp  # noqa: F401
    HAVE_DEPS = True
except Exception:  # pragma: no cover
    HAVE_DEPS = False

REDIRECT = "https://claude.ai/api/mcp/auth_callback"
PASSPHRASE = "correct-horse-battery-staple"


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@unittest.skipUnless(HAVE_DEPS, "mcp/httpx not installed")
class OAuthFlow(unittest.TestCase):
    """One server for the whole class — booting uvicorn per test is wasteful."""

    @classmethod
    def setUpClass(cls):
        import httpx

        cls.tmp = Path(tempfile.mkdtemp())
        cls.port = free_port()
        cls.origin = f"http://127.0.0.1:{cls.port}"
        cls.env = dict(os.environ, VIRALREEL_AUTH_DB=str(cls.tmp / "auth.db"))

        cls._run_auth("set-passphrase", "--stdin", stdin=PASSPHRASE + "\n")

        boot = (
            "import importlib.util,sys;"
            f"spec=importlib.util.spec_from_file_location('s',{str(ROOT / 'server' / 'studio_mcp.py')!r});"
            "m=importlib.util.module_from_spec(spec);sys.modules['s']=m;spec.loader.exec_module(m);"
            f"srv=m.build_server({cls.origin!r});"
            f"srv.run(transport='streamable-http',host='127.0.0.1',port={cls.port},"
            "streamable_http_path='/mcp')"
        )
        cls.proc = subprocess.Popen([sys.executable, "-c", boot], cwd=ROOT, env=cls.env,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        cls.client = httpx.Client(timeout=20, follow_redirects=False)
        for _ in range(100):
            if cls.proc.poll() is not None:
                raise RuntimeError("server exited: " +
                                   cls.proc.stderr.read().decode()[-2000:])
            try:
                cls.client.get(f"{cls.origin}/.well-known/oauth-authorization-server")
                break
            except Exception:
                time.sleep(0.3)
        else:
            raise RuntimeError("server never became reachable")

    @classmethod
    def tearDownClass(cls):
        cls.client.close()
        cls.proc.terminate()
        try:
            cls.proc.wait(timeout=10)
        except Exception:
            cls.proc.kill()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    @classmethod
    def _run_auth(cls, *args, stdin=None):
        env = getattr(cls, "env", None) or dict(
            os.environ, VIRALREEL_AUTH_DB=str(cls.tmp / "auth.db"))
        return subprocess.run(
            [sys.executable, str(ROOT / "server" / "studio_auth.py"), *args],
            cwd=ROOT, env=env, input=stdin, text=True, capture_output=True, check=True)

    # -- helpers ------------------------------------------------------------

    def register(self):
        r = self.client.post(f"{self.origin}/register", json={
            "client_name": "Claude (test)", "redirect_uris": [REDIRECT],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"], "token_endpoint_auth_method": "none"})
        self.assertIn(r.status_code, (200, 201), r.text[:300])
        return r.json()["client_id"]

    def authorize(self, client_id):
        verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
        state = secrets.token_urlsafe(12)
        r = self.client.get(f"{self.origin}/authorize", params={
            "response_type": "code", "client_id": client_id, "redirect_uri": REDIRECT,
            "code_challenge": challenge, "code_challenge_method": "S256",
            "state": state, "resource": f"{self.origin}/mcp"})
        self.assertIn(r.status_code, (302, 307), r.text[:300])
        req_id = re.search(r"req=([^&]+)", r.headers["location"]).group(1)
        return verifier, state, req_id

    def consent(self, req_id, passphrase=PASSPHRASE):
        return self.client.post(f"{self.origin}/consent",
                                data={"req": req_id, "passphrase": passphrase})

    def full_token(self):
        """A complete happy-path authorization, returning the token payload."""
        client_id = self.register()
        verifier, _, req_id = self.authorize(client_id)
        code = re.search(r"[?&]code=([^&]+)",
                         self.consent(req_id).headers["location"]).group(1)
        r = self.client.post(f"{self.origin}/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": client_id, "code_verifier": verifier})
        self.assertEqual(r.status_code, 200, r.text[:300])
        return client_id, r.json()

    def mcp(self, token, method, params=None, session=None):
        headers = {"Accept": "application/json, text/event-stream",
                   "Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if session:
            headers["mcp-session-id"] = session
        body = {"jsonrpc": "2.0", "id": 1, "method": method}
        if params is not None:
            body["params"] = params
        return self.client.post(f"{self.origin}/mcp", headers=headers, json=body)

    # -- discovery ----------------------------------------------------------

    def test_protected_resource_metadata_is_served(self):
        """RFC 9728 — the MCP spec requires it of every remote server."""
        r = self.client.get(f"{self.origin}/.well-known/oauth-protected-resource/mcp")
        if r.status_code != 200:
            r = self.client.get(f"{self.origin}/.well-known/oauth-protected-resource")
        self.assertEqual(r.status_code, 200)
        self.assertIn("authorization_servers", r.json())

    def test_authorization_server_metadata_advertises_s256(self):
        meta = self.client.get(f"{self.origin}/.well-known/oauth-authorization-server").json()
        for key in ("issuer", "authorization_endpoint", "token_endpoint",
                    "registration_endpoint"):
            self.assertIn(key, meta)
        self.assertIn("S256", meta["code_challenge_methods_supported"])

    # -- refusals -----------------------------------------------------------

    def test_mcp_requires_a_token(self):
        r = self.mcp(None, "tools/list")
        self.assertEqual(r.status_code, 401)
        self.assertIn("bearer", r.headers.get("www-authenticate", "").lower())

    def test_garbage_token_refused(self):
        self.assertEqual(self.mcp("not-a-real-token", "tools/list").status_code, 401)

    def test_wrong_passphrase_issues_no_code(self):
        client_id = self.register()
        _, _, req_id = self.authorize(client_id)
        r = self.consent(req_id, "definitely-wrong")
        self.assertEqual(r.status_code, 401)
        self.assertNotIn("code=", r.headers.get("location", ""))

    def test_wrong_pkce_verifier_refused(self):
        client_id = self.register()
        _, _, req_id = self.authorize(client_id)
        code = re.search(r"[?&]code=([^&]+)",
                         self.consent(req_id).headers["location"]).group(1)
        r = self.client.post(f"{self.origin}/token", data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT,
            "client_id": client_id, "code_verifier": "wrong-verifier"})
        self.assertNotEqual(r.status_code, 200)

    def test_authorization_code_is_single_use(self):
        client_id = self.register()
        verifier, _, req_id = self.authorize(client_id)
        code = re.search(r"[?&]code=([^&]+)",
                         self.consent(req_id).headers["location"]).group(1)
        data = {"grant_type": "authorization_code", "code": code,
                "redirect_uri": REDIRECT, "client_id": client_id,
                "code_verifier": verifier}
        self.assertEqual(self.client.post(f"{self.origin}/token", data=data).status_code, 200)
        self.assertNotEqual(self.client.post(f"{self.origin}/token", data=data).status_code, 200)

    def test_expired_consent_request_is_rejected(self):
        r = self.consent("a-request-that-never-existed")
        self.assertEqual(r.status_code, 400)

    # -- happy path ---------------------------------------------------------

    def test_authorize_does_not_issue_a_code_before_consent(self):
        """The redirect must go to our consent page, never straight back to the
        client with a code — otherwise the passphrase would be decorative."""
        client_id = self.register()
        r = self.client.get(f"{self.origin}/authorize", params={
            "response_type": "code", "client_id": client_id, "redirect_uri": REDIRECT,
            "code_challenge": "x" * 43, "code_challenge_method": "S256", "state": "s"})
        location = r.headers["location"]
        self.assertIn("/consent", location)
        self.assertNotIn("code=", location)

    def test_consent_page_names_the_client(self):
        client_id = self.register()
        _, _, req_id = self.authorize(client_id)
        page = self.client.get(f"{self.origin}/consent", params={"req": req_id})
        self.assertEqual(page.status_code, 200)
        self.assertIn("Claude (test)", page.text)

    def test_state_is_returned_unmodified(self):
        client_id = self.register()
        _, state, req_id = self.authorize(client_id)
        self.assertIn(f"state={state}", self.consent(req_id).headers["location"])

    def test_token_grants_access_to_the_tools(self):
        _, payload = self.full_token()
        self.assertEqual(payload["token_type"], "Bearer")
        self.assertGreater(payload["expires_in"], 0)

        init = self.mcp(payload["access_token"], "initialize", {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "test", "version": "1"}})
        self.assertEqual(init.status_code, 200, init.text[:300])
        session = init.headers.get("mcp-session-id")
        tools = self.mcp(payload["access_token"], "tools/list", session=session)
        self.assertIn("studio_status", tools.text)

    def test_refresh_token_rotates(self):
        client_id, payload = self.full_token()
        first = payload["refresh_token"]
        r = self.client.post(f"{self.origin}/token", data={
            "grant_type": "refresh_token", "refresh_token": first, "client_id": client_id})
        self.assertEqual(r.status_code, 200, r.text[:300])
        self.assertNotEqual(r.json()["refresh_token"], first, "refresh token was not rotated")
        reuse = self.client.post(f"{self.origin}/token", data={
            "grant_type": "refresh_token", "refresh_token": first, "client_id": client_id})
        self.assertNotEqual(reuse.status_code, 200, "spent refresh token still works")

    def test_revoke_all_kills_live_tokens(self):
        _, payload = self.full_token()
        token = payload["access_token"]
        self.assertEqual(self.mcp(token, "initialize", {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "t", "version": "1"}}).status_code, 200)
        self._run_auth("revoke-all")
        self.assertEqual(self.mcp(token, "tools/list").status_code, 401)


@unittest.skipUnless(HAVE_DEPS, "mcp not installed")
class PassphraseStore(unittest.TestCase):
    """The credential store, without a server in the way."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        os.environ["VIRALREEL_AUTH_DB"] = str(self.tmp / "auth.db")
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "studio_auth_t", ROOT / "server" / "studio_auth.py")
        self.auth = importlib.util.module_from_spec(spec)
        sys.modules["studio_auth_t"] = self.auth
        spec.loader.exec_module(self.auth)

    def tearDown(self):
        os.environ.pop("VIRALREEL_AUTH_DB", None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_short_passphrase_refused(self):
        with self.assertRaises(ValueError):
            self.auth.set_passphrase("short")

    def test_roundtrip(self):
        self.auth.set_passphrase("a-long-enough-passphrase")
        self.assertTrue(self.auth.has_passphrase())
        self.assertTrue(self.auth.check_passphrase("a-long-enough-passphrase"))
        self.assertFalse(self.auth.check_passphrase("something-else-entirely"))

    def test_passphrase_is_not_stored_in_the_clear(self):
        secret = "a-long-enough-passphrase"
        self.auth.set_passphrase(secret)
        blob = (self.tmp / "auth.db").read_bytes()
        self.assertNotIn(secret.encode(), blob)

    def test_repeated_failures_lock_out(self):
        self.auth.set_passphrase("a-long-enough-passphrase")
        for _ in range(self.auth.MAX_FAILURES):
            self.auth.check_passphrase("wrong")
        self.assertGreater(self.auth._locked_out(), 0)
        # Locked out means locked out, even for the right passphrase.
        self.assertFalse(self.auth.check_passphrase("a-long-enough-passphrase"))


if __name__ == "__main__":
    unittest.main()
