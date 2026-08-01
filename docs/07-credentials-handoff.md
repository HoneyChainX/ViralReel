# 07 — Credentials Handoff

Two credentials stand between a finished render and a published video, and both of them can only
come from your own logged-in Google account: an **OAuth 2.0 client** for the YouTube Data API v3
(so `youtube-automation-agent` can upload on your behalf) and a **Gemini API key** (the free-tier
LLM that drives that agent's publish/SEO/analytics loop). Neither can be created by this repo,
by Claude Code, or by any agent that isn't sitting inside your browser session. This document
exists so you don't have to click through Google Cloud yourself: section 2 is a prompt you hand
verbatim to **Claude for Chrome**, which does the navigation while you supervise and do the two
things it is explicitly forbidden from doing — copying the secret values.

Nothing here produces a value this repo can verify for you. Every `<<FILL: …>>` below is a real
gap that only your account can close. Do not let any agent, including me, guess one.

---

## 1. Before you start

- Be signed into Chrome with **the Google account that owns or manages the YouTube channel.** The
  Cloud project can technically live anywhere, but the account you consent with during the OAuth
  walkthrough must be the channel's account, and that same account must be added as a test user.
- Have Claude for Chrome running with the browser on a blank tab. Watch it work. It is operating
  in a console that can create billable resources; approve only the actions that match the steps
  below, and reject anything that mentions billing, payment, or upgrading.
- You will need to run `make setup` first if you haven't — it creates the two vendor `.env` files
  these values land in (`scripts/setup.sh`). It will not overwrite an existing `.env`.

---

## 2. The prompt block

Copy everything between the fences and paste it to Claude for Chrome unedited.

```
You are operating in my own logged-in Chrome. Your job is to produce two credentials for a
YouTube publishing pipeline:

  (A) a Google Cloud OAuth 2.0 client (type: Desktop app) authorized for the YouTube Data API v3
  (B) a Gemini API key from Google AI Studio, free tier

HARD RULES — read these before step 1.

  R1. Never invent, guess, autocomplete, or "reconstruct" a value. If a screen does not show
      what these instructions say it will, STOP and describe exactly what you see instead. A
      wrong identifier here does not fail loudly — it fails silently, days later, mid-upload.
  R2. Never type a client secret or an API key into this chat. Those two values reach me by me
      copying them off the screen or out of a downloaded file. You may report the OAuth client
      ID in full (it is not a secret). Everything else secret: location only, never contents.
  R3. Do not enable billing, add a payment method, upgrade a plan, or accept a paid tier. If any
      screen requires one to continue, STOP and report it. This pipeline is $0 marginal cost by
      design and a billing prompt means we are on the wrong path.
  R4. Do not click "Publish app", do not request app verification, do not submit anything for
      review. The app stays in Testing. This is deliberate — see the note in step A5.
  R5. Do not delete or edit any existing Google Cloud project, credential, API key, or enabled
      API that you did not create during this session.
  R6. Google renames these console menus regularly. Every step below says WHAT the page does,
      not only what it is labelled. If a label doesn't match, navigate by function and tell me
      the label you actually found. Direct URLs may redirect — follow the redirect, that's fine.
  R7. Enable exactly the one API named below. Every additional enabled API is unused attack
      surface on a project that holds upload rights to a channel.

PART A — Google Cloud OAuth client

A1. Open https://console.cloud.google.com/ . Check the account avatar in the top-right. Report
    which Google account is active. If more than one account is signed in, ask me which one owns
    the YouTube channel before doing anything else, and switch to it.

A2. Create or select the project. Use the project picker in the top navigation bar (immediately
    right of the "Google Cloud" logo; it shows the current project name and opens a dialog with a
    "New Project" button). Create a new project named: price-archaeology
    - If asked for an organization or location, "No organization" is fine.
    - If asked to link a billing account, skip it. A project does not need billing for either of
      these credentials.
    Report the Project name and the Project ID exactly as the console displays them (the ID is
    often the name plus a numeric suffix — copy it, do not assume it matches the name).

A3. Enable the YouTube Data API v3. Navigation: main hamburger menu -> "APIs & Services" ->
    "Library". Direct URL to try: https://console.cloud.google.com/apis/library
    Search for: YouTube Data API v3
    Open the result titled exactly "YouTube Data API v3". Do NOT open "YouTube Analytics API" or
    "YouTube Reporting API" — similar names, wrong API. Click Enable and wait until the page
    shows it as enabled (usually by replacing the Enable button with "Manage" / "Disable").
    Report: enabled yes/no, and the exact title of the API you enabled.

A4. Read the quota, change nothing. From that API's page open the "Quotas" tab (may be labelled
    "Quotas & System Limits"). Find the default daily quota for this project. Report the number
    and its unit exactly as shown. Do not request a quota increase. This is a read-only step —
    I want the real number from my project, not a number from documentation.

A5. Configure the consent screen. Navigation: "APIs & Services" -> "OAuth consent screen". In
    current console versions this redirects to a section called "Google Auth Platform"
    (try https://console.cloud.google.com/auth/overview ). You are looking for the area that
    defines what a user sees when they grant this app access. Its sub-pages are currently named
    something like Branding, Audience, Data access, and Clients. Complete all four ideas below,
    wherever they now live:

    (a) App identity / "Branding": App name = Price Archaeology Publisher. User support email =
        my account. Developer contact email = my account. No logo needed. Save.

    (b) User type / "Audience": choose EXTERNAL. ("Internal" only appears on Google Workspace
        organizations and cannot accept outside test users — if only Internal is available, stop
        and tell me, because that changes the setup.)

    (c) Publishing status: leave it on TESTING. Do not publish.
        Relay this to me in your final report so I know you saw it: while the app is in Testing,
        Google expires issued refresh tokens after 7 days, which means the upload agent must be
        re-authorized weekly. That is an accepted trade for not entering app verification, which
        these YouTube scopes would otherwise require. Do not "fix" it by publishing the app.

    (d) Test users: add my Google account email — the same account that manages the YouTube
        channel. This is mandatory. While in Testing, only listed test users can complete the
        OAuth flow at all; skipping this produces an access_denied error later that looks like a
        scope problem and isn't.

    (e) Scopes / "Data access": use "Add or remove scopes" and add exactly these FOUR, then
        Update and Save:
            https://www.googleapis.com/auth/youtube.upload
            https://www.googleapis.com/auth/youtube
            https://www.googleapis.com/auth/youtube.readonly
            https://www.googleapis.com/auth/yt-analytics.readonly
        These are not a guess: they are the exact list requested by the publishing tool at
        vendor/yt-agent/modern-auth.js, which is what `npm run walkthrough` runs. Consenting
        to fewer than the tool requests fails at authorization time.
        Google will mark several of these as sensitive or restricted — that is expected and is
        not an error. Add no other scope. Do not begin the verification process it may offer.

    Report: user type, publishing status, test user email added, and whether each of the four
    scopes is present in the saved list.

A6. Create the OAuth client. Navigation: "APIs & Services" -> "Credentials" (direct URL to try:
    https://console.cloud.google.com/apis/credentials ), or the "Clients" page under Google Auth
    Platform. Click "Create credentials" -> "OAuth client ID".
    - Application type: DESKTOP APP. Not "Web application", not "TVs and Limited Input devices".
      The publishing tool completes its OAuth handshake on a local loopback address, which is
      what a Desktop client is configured for; the wrong type fails with redirect_uri_mismatch.
    - Name: price-archaeology-desktop
    - Click Create. A dialog appears showing Client ID and Client secret.
    - Click "Download JSON" (or the download icon on the client's row in the list). Report the
      exact filename and the folder it saved to.
    - Leave the dialog open on screen and tell me to copy the Client secret myself. Do not type
      it here, do not summarize it, do not report any part of it.
    - Report the Client ID in full. It is public information and ends in
      .apps.googleusercontent.com — if what you see does not end that way, say so.

PART B — Gemini API key (free tier)

B1. Open https://aistudio.google.com/ . Sign in with the same Google account as Part A if
    prompted. Report which account is active.

B2. Find the API key area — a control labelled "Get API key" or "API keys", usually in the
    left navigation or the top-right. Direct URL to try: https://aistudio.google.com/apikey
    If that URL does not resolve, navigate from the AI Studio home instead and tell me the path
    you used.

B3. Click "Create API key". If it asks which Google Cloud project to attach the key to, choose
    the same project from step A2 — one project per credential set makes revocation a single
    action later.

B4. Free tier only. Do not click "Set up billing", "Upgrade", "Enable paid tier", or equivalent.
    If key creation cannot complete without billing, STOP and report exactly what blocked it.

B5. Do not paste the key into this chat. Leave it visible on screen and tell me to copy it.
    Report only: the LAST 4 characters (so I can identify this key in the list later), the
    project it is attached to, and the tier shown.

B6. Find where the current free-tier rate limits are displayed or linked from this page. Report
    the link and any limits actually visible on screen. Do not quote limits from memory — these
    change and a stale number is worse than no number.

FINAL REPORT — reply with exactly this checklist, filled in:

  Google account used:
  Cloud project name:
  Cloud project ID:
  YouTube Data API v3 enabled (yes/no):
  Daily quota shown on the Quotas page (number + unit):
  Consent screen user type:
  Publishing status:
  Test user added (email):
  Scope youtube.upload present (yes/no):
  Scope youtube present (yes/no):
  Scope youtube.readonly present (yes/no):
  Scope yt-analytics.readonly present (yes/no):
  OAuth client application type (must read "Desktop"):
  OAuth client ID (full):
  Client secret — NOT reported; downloaded JSON filename and folder:
  Gemini key created (yes/no), last 4 chars, attached project, tier:
  Free-tier rate-limit link and visible limits:
  Anything on screen that contradicted these instructions:

IF YOU GET STUCK: report the page you are on, the control you clicked, and the exact error text.
Do not route around it by creating a different credential type, enabling a different API, or
turning on billing. A blocked step reported accurately is useful; a substituted step is not.
```

### Why Testing mode, and what it costs you

Leaving publishing status on **Testing** is the right call at launch, but it has one concrete
consequence worth internalizing before it surprises you: **refresh tokens issued by an app in
Testing status expire after 7 days.** In practice that means roughly weekly you will see uploads
fail with an `invalid_grant` error, and the fix is to re-run the walkthrough:

```bash
cd vendor/yt-agent && npm run walkthrough
```

The alternative — moving the app to production — requires Google's app verification review
because `youtube.upload` is a sensitive scope, and that is a process with its own review
timeline and requirements. Check Google's current OAuth policy before assuming what that
involves rather than trusting this paragraph; it changes.
Reference: https://developers.google.com/identity/protocols/oauth2

At one to two videos a day (`config/channel.yaml` → `cadence.hard_cap_per_day: 2`), a weekly
re-auth is cheap. If it ever stops being cheap, that is a deliberate decision to revisit, not a
reason to loosen anything in `docs/05-compliance.md`.

---

## 3. Where each value goes

Env var names below are copied exactly from `config/env.ytagent.template` and
`config/env.openmontage.template`. `make setup` copies those templates to the vendor `.env`
files; you edit the copies, never the templates.

**The OAuth values do not go in a file you edit.** An earlier version of this document said to
paste them into `vendor/yt-agent/.env` as `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` /
`YOUTUBE_REFRESH_TOKEN`. **The tool reads none of those names** — a repo-wide grep of
`vendor/yt-agent/` finds them only in the `.env` our own template wrote. Pasting them there does
nothing and the walkthrough would ask for them again.

What actually happens: `npm run walkthrough` **prompts you at the terminal** to paste the Client
ID and Client Secret (`walkthrough.js:350`), and writes them to
`vendor/yt-agent/config/credentials.json` (`utils/credential-manager.js:11`). The browser consent
step then writes the tokens to `vendor/yt-agent/config/tokens.json` (`modern-auth.js:11`).

| Value | Where it goes | How |
|---|---|---|
| OAuth Client ID (ends `.apps.googleusercontent.com`) | `vendor/yt-agent/config/credentials.json` | **pasted at the walkthrough prompt** — you never edit the file |
| OAuth Client secret | `vendor/yt-agent/config/credentials.json` | same prompt, masked input |
| Refresh token | `vendor/yt-agent/config/tokens.json` | written automatically by the browser consent step |
| Gemini API key | `vendor/yt-agent/.env` → `GEMINI_API_KEY` | env var, read at `index.js:97` |
| Dashboard password you invent | `vendor/yt-agent/.env` → `API_KEY` | env var, read at `index.js:133` |
| Literal `private` | `vendor/yt-agent/.env` → `DEFAULT_PRIVACY_STATUS` | **note the prefix**, read at `agents/publishing-scheduling-agent.js:130` |
| ElevenLabs key (outside this handoff) | `vendor/openmontage/.env` → `ELEVENLABS_API_KEY` | env var |

Target state of the parts of `vendor/yt-agent/.env` you actually edit:

```bash
GEMINI_API_KEY=              # <<FILL: AI Studio -> API keys -> Create API key (free tier)>>
API_KEY=                     # <<FILL: invent one; `openssl rand -hex 24` is fine>>
DEFAULT_PRIVACY_STATUS=private
```

**Sequence.** The walkthrough is interactive, so have the Client ID and Secret on screen (or the
downloaded JSON open) before you start it:

```bash
make setup                                   # creates both vendor .env files from the templates
# put GEMINI_API_KEY + API_KEY into vendor/yt-agent/.env
cd vendor/yt-agent && npm run walkthrough    # PROMPTS for client id + secret, then browser consent
```

During the walkthrough's consent screen you will see Google's "Google hasn't verified this app"
warning. That is the expected consequence of Testing status on a self-owned app — proceed with
the account you added as a test user.

### Verified against the installed tool, not assumed

Two claims in §2 were checked against `vendor/yt-agent/` rather than inferred, because both
fail silently and late:

- **Desktop app is the correct client type.** `modern-auth.js` spins up a temporary local server
  and uses `http://localhost:<port>/callback` as its redirect. A loopback redirect is what a
  Desktop client permits; a Web client rejects it with `redirect_uri_mismatch`.
  (Ignore `config/credentials.example.json` in that repo — it still shows the legacy
  `urn:ietf:wg:oauth:2.0:oob` flow, which Google retired. `modern-auth.js` is the live path.)
- **There are four scopes, not two.** An earlier draft of this document listed only
  `youtube.upload` and `youtube.readonly`. The tool actually requests four, including plain
  `youtube` and `yt-analytics.readonly`. Consenting to a subset produces an authorization
  failure that reads like a config problem and isn't. The list in §2(e) is copied from the
  source.

---

## 4. Verify it worked

```bash
make doctor
```

`scripts/doctor.sh` checks dependencies, keys, and the cost controls. The lines that prove this
handoff landed:

```
  OK    GEMINI_API_KEY set (free tier)
  OK    no paid generator keys — marginal cost stays $0.00
  OK    PRIVACY_STATUS=private
Ready.
```

A `WARN` on `ELEVENLABS_API_KEY` is not a failure — it means VO falls back to Piper. A `FAIL` on
`GEMINI_API_KEY` means the key never made it into `vendor/yt-agent/.env`. `make doctor` exits
non-zero if anything failed and prints `Not ready — fix the FAILs above.`

OAuth is verified by the presence of the two files the walkthrough writes — never by reading
their contents:

```
  OK    config/credentials.json present (client id + secret)
  OK    config/tokens.json present (refresh token)
```

A `FAIL` on `credentials.json` means the walkthrough never got your client ID; a `FAIL` on
`tokens.json` means the browser consent step didn't complete. The real end-to-end proof is a
private upload of a gated episode (`make publish SLUG=…`), which lands private by design and can
be deleted from YouTube Studio afterwards.

---

## 5. Security note

**Credentials live in four files, all gitignored:** `vendor/openmontage/.env`,
`vendor/yt-agent/.env`, `vendor/yt-agent/config/credentials.json`, and
`vendor/yt-agent/config/tokens.json`. `.gitignore` excludes `vendor/` wholesale plus `.env`,
`.env.*`, `credentials.json`, `tokens.json`, and `token.json` by name. Nothing in this
repository ever contains a credential — not a doc, not a config, not a test fixture, not a
comment.

> The two JSON files are the ones people forget, because nothing in this repo tells you to
> create them — the vendor's walkthrough writes them. They hold your client secret and refresh
> token in plaintext.

- **Never paste a key into a chat.** Not into Claude for Chrome, not into Claude Code, not into
  this repo's agents. That is why §2 forbids the browser agent from reporting the secret and the
  API key, and why it reports only a location and the last four characters.
- **CI will catch you.** `.github/workflows/gate.yml` runs a job named *"no secrets, no paid
  keys"* that scans every tracked file for a populated value on any of: `ELEVENLABS_API_KEY`,
  `FAL_KEY`, `RUNWAY_API_KEY`, `KLING_API_KEY`, `XAI_API_KEY`, `SUNO_API_KEY`,
  `ATLASCLOUD_API_KEY`, `HEYGEN_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`,
  `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`. A populated key fails the build. The scanner
  treats `KEY=` followed by a `#` comment as empty, which is why every example in this document
  is written that way — a realistic-looking fake value in a doc fails CI exactly like a real leak
  does, and that is the correct behaviour.
- **Move the downloaded JSON off disk when you're done.** Copy the two values into
  `vendor/yt-agent/.env`, then delete `client_secret_*.json` from your downloads folder. It is a
  plaintext credential sitting in the most-synced directory on your machine.
- **Assume a leaked key is burned.** If a key was ever pasted into a chat, committed, or
  screenshotted, deleting the line does not undo it — git history and chat logs keep it. Revoke
  and reissue: OAuth clients at Cloud Console → APIs & Services → Credentials (delete the client,
  which also invalidates its refresh token); Gemini keys in the AI Studio API keys list.
- **The empty paid-generator keys stay empty.** `FAL_KEY`, `RUNWAY_API_KEY`, `KLING_API_KEY`,
  `XAI_API_KEY`, `SUNO_API_KEY`, `ATLASCLOUD_API_KEY`, `HEYGEN_API_KEY`, `OPENAI_API_KEY` are
  blank as a cost control, not an oversight (`docs/04-stack.md`). `make doctor` fails if one gets
  set, and so does CI.
