# ASSESSMENT.md — System Architecture & Design Decisions

Canonical reference for the IELTS Speaking assessment subsystem (the voice-ML
backend). For long-form rationale see [`ielts-speaking-coach-design.md`](ielts-speaking-coach-design.md);
for prompts see [`../prompts/`](../prompts/).

---

## 1. What we're building (from the user story)

A web app where a learner talks to a randomly-chosen Tavus examiner, practices any
subset of the IELTS Speaking parts, and gets a band-scored report card with
specific, quoted, pronunciation-aware feedback.

| User-story requirement | How the system delivers it |
|---|---|
| Click "Start mock test" → Tavus examiner on video | Create a Conversation from the Examiner **PAL** + a **Face**; render with CVI |
| Customize which part(s) to practice | **Per-Part modules** (`parts/`); app passes a `TestPlan` = ordered subset of parts |
| Examiner random every time | Pick a random **Face id** from a curated pool per session (PAL stays constant) |
| Username, no password; history saved & viewable | App DB keyed by username + Tavus `memory_stores:["ielts_{username}"]` for continuity |
| Real 3-part structure in PAL prompt + objectives | **Objectives** encode Part 1→2→3 steps; system prompt holds the persona |
| Parts modular; multiple parts = continuous convo | One Conversation; app advances Objectives / injects `overwrite-context` per part |
| Call ends → transcript → **Claude grades** 4 criteria, band 0–9 + quoted feedback | Async **Assessment Engine**: features → Claude rubric judges → Scorecard |
| "Transcript is not enough — pronunciation matters" | **Charsiu GOP** on per-turn audio feeds the Pronunciation judge |
| Clean report card | `Scorecard` JSON → report UI; `CoachingSession.conversational_summary()` |

---

## 2. Architecture — two brains

Conversation quality (low latency, natural) and assessment rigor (slow, analytic)
have conflicting requirements, and the in-call LLM degrades past ~5k tokens — so we
**decouple** them.

```
 IN-CALL (Tavus CVI, low latency)            ASYNC ASSESSMENT ENGINE (no latency budget)
 ┌───────────────────────────┐               ┌────────────────────────────────────────┐
 │ Examiner PAL              │  utterances   │ A. features  (fluency/lexical/grammar/   │
 │  • Objectives = 3 parts   │──events──────▶│    pronunciation) from timings + audio   │
 │  • Guardrails             │  + recording  │ B. judges    (Claude, 1 per criterion,   │
 │  • Knowledge Base (RAG)   │   (MP4 audio) │    evidence-grounded, exemplar-anchored) │
 │  • STT tavus-soniox       │               │ C. aggregate (IELTS half-band rounding)  │
 │  • hosted LLM (Llama 3.3) │◀──cues────────│ coaching: features → 1 warm spoken cue   │
 └───────────────────────────┘ append-context└────────────────────────────────────────┘
                                / echo                         │
                                                               ▼  Scorecard + report card
```

- **Examiner PAL** only elicits speech and runs the structure. Never scores in-call.
- **Assessment Engine** does all numeric/analytic work off-call (this repo).
- **Coaching loop** (Coach mode) sends one distilled cue back into the call so the
  learner feels heard, without breaking flow or the token budget.

---

## 3. The assessment pipeline (3 layers)

**A — Deterministic features** (`src/assessment/features/`, mostly pure stdlib):
the objective evidence base. Fluency from word/phone timings (speech rate, pauses,
runs, fillers, repetitions, discourse markers); Lexical (MTLD, rare-word ratio,
basic-word overuse); Grammar (clause complexity, subordination, T-units via spaCy);
Pronunciation (Charsiu GOP, or a confidence proxy fallback).

**B — Rubric judges** (`src/assessment/judges/`): four Claude judges, one per
criterion, each fed *only its* features + transcript + retrieved band descriptors &
exemplars. Returns `{band, confidence, evidence[], feedback[]}` — **every band must
cite a quote or feature**. This is how "you said X, a band-7 answer would say Y"
feedback is produced, and how pronunciation (which Claude can't hear) still gets
scored — via the GOP features.

**C — Aggregate** (`src/assessment/aggregate.py`): mean of the four bands, rounded
to the nearest half-band by the official rule (.25→.5, .75→next whole). Each
criterion is weighted toward the part that reveals it best (`CRITERION_PRIMARY_PART`:
Fluency←Part 2, Grammar←Part 3).

---

## 4. Decision log

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | **Two brains** (in-call examiner vs async assessor) | Latency vs rigor conflict; Tavus LLM degrades >5k tokens | Scoring inside the conversation |
| D2 | **All-Tavus** for STT + LLM + Knowledge Base (one key) | Bundled with hackathon credits; fewer secrets | Separate Soniox / vector DB / LLM keys |
| D3 | **Charsiu (MIT)** for pronunciation **and** word timings | Open, local, no key; alignment does double duty (GOP + timings) | Azure Speech (lock-in, extra key) |
| D4 | **Claude** as judge LLM, via OpenAI-compatible client | User story; low-hallucination, strong rubric reasoning | Single generalist scorer |
| D5 | **STT = tavus-soniox** | Keeps fillers/disfluencies that Fluency is scored on | Whisper (normalises fillers away) |
| D6 | **Per-Part modules** | Team builds one part at a time; parts reveal different criteria | One monolithic assessor |
| D7 | **Evidence-grounded + exemplar calibration** | LLMs are uncalibrated scoring in the abstract; citations enable feedback | "Just ask the LLM for a band" |
| D8 | **Deterministic Layer-A features** | Objective, reproducible evidence; cheap; STT-robust (timings from alignment) | LLM-only feature inference |
| D9 | **Coaching cue loop** (append-context/echo) | Interactive, tutor-like experience | Static end-only report |

---

## 5. Module map

```
src/assessment/
  schema.py        data contracts: Turn, *Features, JudgeResult, Scorecard
  config.py        env config (one TAVUS_API_KEY covers STT/LLM/RAG)
  features/        Layer A: fluency, lexical, grammar, pronunciation
  judges/          Layer B: OpenAI-compatible client + 4 rubric judges
  aggregate.py     Layer C: IELTS half-band rounding
  parts/           per-Part modules (Part1/2/3): structure, questions, cue policy
  coaching.py      features → conversational coaching cue (mode/part gated)
  session.py       stateful session: live cues, adaptive focus, spoken wrap-up
  stt.py           word/phone timings via Charsiu forced alignment on the recording
examples/
  demo.py          end-to-end Layer-A demo (no deps)
  server.py        zero-dependency browser demo for functionality testing
scripts/
  setup_tavus.py   configure the Examiner PAL + upload Knowledge Base docs
```

Status: Layers A & C and coaching/session/parts are implemented and tested
(33 tests). Layer-B judges and the Charsiu/forced-alignment backends are scaffolded
behind clean interfaces (proxy fallbacks keep everything runnable now).

---

## 6. What you need to do on your end (Tavus setup)

You already have an Examiner PAL: **`pece42dab07f`** ("test examiner"). To make it
exam-ready, configure it in the PAL editor (or run `scripts/setup_tavus.py`):

1. **Advanced settings** → paste the Examiner **system prompt**
   (`prompts/examiner-pal-system-prompt.md`); set **Model** (hosted Llama 3.3 is
   fine) and **STT engine = `tavus-soniox`**.
2. **Custom Greeting** → e.g. *"Hello, I'm Aria. Welcome to your IELTS speaking
   practice. Shall we begin?"*
3. **Objectives** → encode the 3-part flow (one objective per part — see the
   Objectives spec in `prompts/examiner-pal-system-prompt.md`). This is what makes
   the parts modular and lets the user pick a subset.
4. **Guardrails** → "Never reveal band scores or assessment during the test", "Never
   supply vocabulary or correct the candidate" (exam mode), "Stay on the current
   topic".
5. **Knowledge** → upload the band descriptors + question bank + exemplars (tags
   `ielts-rubric`, `ielts-questions`, `ielts-exemplars`).
6. **Faces** → collect a **pool of Face ids** (stock faces are fine) so the app can
   pick a random examiner per session. Note each id.
7. **Recording** → on Conversation create, set `properties.enable_recording=true`
   and a `recording_storage` bucket (S3/GCS) + a `callback_url` webhook so we receive
   `application.recording_ready` (the per-turn audio the pronunciation layer needs).
8. **`.env`** → `cp .env.example .env`; set `TAVUS_API_KEY`,
   `TAVUS_PAL_ID=pece42dab07f`, a `TAVUS_FACE_ID` (or the pool in app config), and —
   if judging with Claude — `LLM_BASE_URL`/`LLM_API_KEY`/`LLM_MODEL`.

Open question to confirm with Tavus: whether their hosted LLM is callable
**standalone** for off-call judging. If not, point `LLM_BASE_URL` at Anthropic's
OpenAI-compatible endpoint for the Claude judges (per the user story).

---

## 7. Data contract (the integration boundary)

The app/backend gives us `Turn`s (from utterance events + the recording) and gets
back a `Scorecard`. Both are plain dataclasses (`schema.py`), JSON-serialisable.
This is the seam between the voice-ML backend and the rest of the app — keep it
stable; everything else can change behind it.
