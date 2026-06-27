# PAL — IELTS Speaking Practice with an AI Video Examiner

Practise the **IELTS Speaking** test face-to-face with a real-time AI video examiner, then get
an instant **band-score report** (0–9 on all four official criteria) with quoted, actionable
feedback. Built for the **Tavus × Lovable "Build a PAL" hackathon**.

The headline trick: **Tavus grades the test itself.** No external scoring LLM — a Tavus
*post-call action* reads the transcript *and* the candidate's on-camera delivery (Raven
perception) and fills out the band report, which the app just stores and renders.

> This repo contains (1) a **runnable reference app** in `app/` (Python stdlib + vanilla JS,
> zero dependencies) and (2) the **Tavus configuration + domain knowledge** as Claude Code
> skills in `.claude/skills/`. In production the same flow is rebuilt in **Lovable**
> (React + Supabase edge functions); the app here is the tested spec of every request shape.

---

## Table of contents
- [How it works](#how-it-works)
- [The Tavus configuration (already live)](#the-tavus-configuration-already-live)
- [The app](#the-app)
- [Data schema](#data-schema)
- [The 1-minute Part-2 pause](#the-1-minute-part-2-pause)
- [Latency tuning](#latency-tuning)
- [Security](#security)
- [Production mapping (Lovable + Supabase)](#production-mapping-lovable--supabase)
- [Repo layout](#repo-layout)
- [Status / what's left](#status--whats-left)

---

## How it works

```
 Browser (vanilla JS)                Local server (Python)              Tavus API (tavusapi.com/v2)
 ─────────────────────              ──────────────────────             ───────────────────────────
 1. pick parts + name ──POST /api/start-test──▶ build conversational_context
                                                + custom_greeting ──POST /v2/conversations──▶ create room
                            ◀── {conversation_url, conversation_id} ◀──────────────────────── conversation_url
 2. embed conversation_url in an <iframe> ───────────────────────────▶  live video call (Daily room)
    ‹ candidate talks to "Emma" the examiner; Magic Canvas shows the Part-2 cue card ›
 3. click "Finish" ──────POST /api/end-test──▶ POST /v2/conversations/{id}/end  (call ends now)
                                                                          │
                                          Tavus runs the post-call action: reads transcript
                                          + Raven perception → its LLM fills the band report
                                                                          │
 4. poll GET /api/report/{id} ──▶ if not received yet, server polls
                                  GET /v2/conversations/{id}?verbose=true
                                  and extracts the post-call action's body
                            ◀── {status:"ready", report:{...}} ◀──────────  generated report
 5. render the band-score report card
```

Two ways the report can reach the app:
- **Push** — Tavus POSTs it to the post-call action's `delivery.api.url` (set this to `/api/score`
  once you have a public URL).
- **Pull** — the app polls Tavus's verbose conversation and reads the generated body itself.
  The generated body is stored on the conversation **even if the push delivery fails**, so the
  pull path works on `localhost` with no tunnel. This is what makes the local demo self-contained.

---

## The Tavus configuration (already live)

Created once in Tavus and **reused** (don't recreate per session):

| Resource | ID | Notes |
|---|---|---|
| Examiner **PAL** | `pea55f8508c2` | "IELTS Speaking Examiner" — system prompt = the Emma examiner script |
| **Face** (avatar) | `r68fe8906e53` | stock face "Mary – Office" (professional exam-room look) |
| **Post-call action** (the judge) | `t4efc3c554914` | tool `submit_ielts_assessment`, `trigger_type: post_call`, attached to the PAL |

PAL layer config that matters:
- **LLM:** `tavus-gemini-2.5-flash` — latency-optimized + natural; the prescriptive prompt keeps
  it on the IELTS script. (`speculative_inference: true`.)
- **Perception:** `raven-1` with end-of-call queries about confidence / composure / delivery —
  the only *delivery* signal we have (no isolated audio), feeds Fluency & Pronunciation scoring.
- **Conversational flow:** `turn_taking_patience: "medium"`, `idle_engagement: "off"` — see
  [the pause](#the-1-minute-part-2-pause) and [latency](#latency-tuning).
- **Magic Canvas:** enabled — the examiner renders the Part-2 cue card on screen during the call.

The whole IELTS rubric lives in the post-call tool's field descriptions (band anchors, "quote the
candidate's words", conservative pronunciation note). Tune scoring by `PATCH /v2/tools/t4efc3c554914`
— no redeploy. Full API bodies are in `.claude/skills/tavus-cvi/SKILL.md`.

---

## The app

Zero dependencies — runs with only `python3` (stdlib `http.server` + vanilla HTML/JS).

```bash
cd app

# LIVE (real Tavus examiner — needs the key in your shell):
TAVUS_API_KEY=... python3 server.py        # → http://localhost:8000

# DEMO (no Tavus call, no credits — UI-only walkthrough):
DEMO_MODE=1 python3 server.py

# Tests (37, ~0.5s, no network):
python3 -m unittest discover -s tests -v
```

| Env var | Default | Purpose |
|---|---|---|
| `TAVUS_API_KEY` | — | Server-side only. Without it the app auto-runs in demo mode. |
| `TAVUS_PAL_ID`  | `pea55f8508c2` | Examiner PAL. |
| `TAVUS_FACE_ID` | `r68fe8906e53` | Examiner face. |
| `PORT` | `8000` | HTTP port. |
| `DEMO_MODE` | off | `1` forces a fake conversation URL + no Tavus calls. |

---

## Data schema

### 1. `POST /api/start-test` — open a test
**Request**
```json
{ "parts": [1, 2, 3], "candidate_name": "Alex" }   // parts: any subset of 1,2,3; name optional
```
**Response** `200`
```json
{ "conversation_id": "c46f3c9ed2f35406",
  "conversation_url": "https://tavus.daily.co/c46f3c9ed2f35406",
  "parts": [1, 2, 3], "demo_mode": false }
```
Errors: `400` invalid part · `502` Tavus error / no `conversation_url`.

### 2. The conversation payload the server sends to Tavus
Built by `tavus.build_conversation_payload()`:
```json
{
  "pal_id": "pea55f8508c2",
  "face_id": "r68fe8906e53",
  "conversation_name": "IELTS Speaking mock test",
  "conversational_context": "Run the following parts ... as ONE continuous test, in order: ...",
  "custom_greeting": "Hello, I'm Emma, and I'll be your examiner ... tell me your full name, please?",
  "properties": {
    "max_call_duration": 1200,
    "participant_absent_timeout": 120,
    "participant_left_timeout": 10,
    "enable_recording": false,
    "enable_closed_captions": true,
    "language": "english"
  }
}
```
- `conversational_context` is how **part selection** is implemented (no PAL edit). Multiple parts
  run as one continuous test; `custom_greeting` is tailored to the first selected part.
- All durations are **seconds**. None of these timeouts end the call for silence — see the pause.

### 3. `POST /api/end-test` — end the live call
**Request** `{ "conversation_id": "c46f..." }` → **Response** `{ "status": "ended" }`.
Ending the call makes Tavus start post-call scoring immediately instead of waiting out
`participant_left_timeout`.

### 4. `POST /api/score` — the band report (Tavus → app)
Receiver for the post-call action. The body is the **flat band-score report** (17 fields, no
nesting — chosen for reliable AI-fill). This is the canonical data schema of the product:

| Field | Type | Meaning |
|---|---|---|
| `overall_band` | number | Mean of the four criteria, rounded to nearest 0.5 (0–9). |
| `fc_band` | number | Fluency & Coherence band (0–9, whole/half). |
| `fc_evidence` | string | 1–2 sentences quoting the candidate, justifying the FC band. |
| `fc_improvement` | string | One concrete technique to raise fluency/coherence. |
| `lr_band` | number | Lexical Resource band. |
| `lr_evidence` | string | Evidence (quoted) for LR. |
| `lr_improvement` | string | One vocabulary upgrade. |
| `gra_band` | number | Grammatical Range & Accuracy band. |
| `gra_evidence` | string | Evidence (quoted), noting specific errors. |
| `gra_improvement` | string | One grammar fix / complex structure, with example. |
| `pron_band` | number | Pronunciation band (conservative; uses perception, no isolated audio). |
| `pron_evidence` | string | Evidence referencing delivery/perception + the no-audio caveat. |
| `pron_improvement` | string | One pronunciation/delivery focus. |
| `summary` | string | 2–3 sentence overall verdict and current level. |
| `action_1` / `action_2` / `action_3` | string | Top three prioritized next steps. |

The server keeps only known fields and coerces the five `*_band` fields to numbers
(`normalize_report`). Optionally a `conversation_id` accompanies the body to key the row; if
absent it's stored under `"latest"` (fine for a single-active-test demo).
**Response** `{ "status": "ok", "conversation_id": "..." }`. Errors: `400` if no report fields.

### 5. `GET /api/report/<conversation_id>` — read the report
```json
{ "status": "pending" }                          // not scored yet (call still finalizing)
{ "status": "ready", "report": { ...17 fields } } // done
```
If nothing has been received, the server **pulls** it from Tavus (verbose conversation) and caches it.

### 6. Report store
In the local app: an in-memory `dict` `{ conversation_id → report }` (`App.reports`). In
production: a Postgres `reports` table with one column per field above plus
`conversation_id text primary key` and `created_at timestamptz default now()`.

### 7. The Tavus event the pull-path parses
From `GET /v2/conversations/{id}?verbose=true`, under `events[]`:
```json
{
  "event_type": "application.post_call_action_executed",
  "properties": {
    "tool_id": "t4efc3c554914",
    "status": "success",                 // or "error" if the push delivery URL failed — body still present
    "request": { "url": "...", "method": "POST", "body": "{\"overall_band\":6.5, ...}" },
    "response": { "http_status": 200, "body": "ok" }
  }
}
```
`properties.request.body` is a JSON **string** = our band report. `tavus.extract_report_from_events()`
finds the event for `tool_id == t4efc3c554914` and parses it.

---

## The 1-minute Part-2 pause

IELTS Part 2 gives the candidate a silent minute to prepare. Verified safe on Tavus:

1. **No silence-based call termination exists.** The only call-ending timeouts are
   `max_call_duration`, `participant_absent_timeout` (fires only *before* anyone joins) and
   `participant_left_timeout` (only after someone *leaves*). A quiet candidate trips none.
2. **The examiner stays silent during the pause** because the PAL has `idle_engagement: "off"`
   (the PAL never proactively breaks silence — it only speaks in response to input). This — **not**
   `turn_taking_patience` — is what protects the pause. The flow is pause-driven: the candidate
   begins whenever ready and the examiner doesn't interrupt natural thinking pauses.
3. The UI shows a visible 60-second prep timer; covered by `tests/test_app.py`.

---

## Latency tuning

Lessons learned from a live run that "didn't feel real-time":
- **`turn_taking_patience: "medium"`, not `"high"`.** High patience adds a long beat after the
  candidate stops talking before every reply — pure latency — and does *nothing* for the pause.
- **A fast LLM:** `tavus-gemini-2.5-flash` (vs the slower default `tavus-glm-4.7`).
- **A tight, prescriptive prompt** (~640 tokens) so the faster model still runs the script and
  stays well under the ~5,000-token sweet spot for speed + instruction-following.
- **End the call explicitly** on Finish so scoring starts immediately (don't wait the leave-timeout).

---

## Security

- **The Tavus API key is server-side only — never in the browser.** The browser only ever
  receives a `conversation_url`. In production it lives in Supabase's edge-function secret manager.
- **No scoring-LLM key** is needed at all — Tavus does the judging (one less secret, no 401 risk).
- The `/api/score` receiver needs no secret; if exposed publicly, verify Tavus's HMAC signature.
- No secrets are committed to this repo.

---

## Production mapping (Lovable + Supabase)

| Local reference (`app/`) | Production (Lovable) |
|---|---|
| `POST /api/start-test` | Supabase edge function `start-test` |
| `POST /api/score` | Supabase edge function `score` (set as the tool's `delivery.api.url`) |
| `GET /api/report/<id>` | Read the `reports` table (Supabase Realtime pushes the row) |
| in-memory `reports` dict | Postgres `reports` table |
| vanilla JS frontend | React frontend generated by Lovable |

The exact Lovable prompts are in `.claude/skills/lovable/SKILL.md`. The one wiring step after
deploy: point the post-call tool at the live receiver —
```bash
curl -X PATCH https://tavusapi.com/v2/tools/t4efc3c554914 \
  -H "x-api-key: $TAVUS_API_KEY" -H "Content-Type: application/json" \
  -d '[{"op":"replace","path":"/delivery/api/url","value":"https://<project>.functions.supabase.co/score"}]'
```

---

## Repo layout

```
CLAUDE.md                       Source-of-truth brief: decisions, architecture, build order
README.md                       This file
app/
  server.py                     Zero-dep HTTP server (routes + static)
  app_core.py                   Handlers, report schema, store, sample report
  tavus.py                      Tavus client + payload/greeting/context builders + report pull
  public/                       index.html · styles.css · app.js (UI + 60s prep timer)
  tests/test_app.py             37 unit + HTTP smoke tests
  README.md                     App-focused run/test/endpoint notes
.claude/skills/
  tavus-cvi/SKILL.md            Tavus CVI API: PAL, conversation, perception, post-call action
  ielts-examiner/SKILL.md       IELTS structure, examiner prompt, band rubric
  lovable/SKILL.md              How to rebuild this in Lovable + Supabase
```

---

## Status / what's left

- ✅ Tavus PAL + face + Magic Canvas + Raven perception + post-call judge — **live**.
- ✅ Runnable app: start → live examiner → end → score (pull path) → report card — verified live.
- ✅ 1-minute pause safe; latency tuned; 37 tests passing.
- ⏳ Point the post-call tool's `delivery.api.url` at the deployed `score` endpoint (curl above)
  once the Lovable/Supabase app is live. Until then the app's pull path covers scoring locally.
