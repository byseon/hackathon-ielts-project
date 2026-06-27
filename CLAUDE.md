# PAL — IELTS Speaking Practice with an AI Examiner

> Built for the **"Build a PAL: Tavus × Lovable Hackathon."** Build fast, demo well, use
> BOTH sponsor tools. This file is the source of truth for what we're building and the
> decisions already made. Edit freely.

## The product in one sentence

An L2 English learner has a realistic, face-to-face **IELTS Speaking** mock test with an
AI video examiner (Tavus CVI), then immediately gets a **band-score report** (0–9 on the
four official criteria) with specific, quoted feedback — generated **by Tavus itself** via a
**post-call action** that scores the transcript *and the Raven perception/delivery analysis*.
No external LLM key required.

## Why this is demoable in a short hackathon

The two sponsor tools do the heavy lifting. **Tavus CVI** gives us a real-time,
photorealistic, talking-and-listening video examiner out of the box, **and even does the
scoring** — a Tavus *post-call action* turns the transcript + perception analysis into the
band report and POSTs it to us. **Lovable** generates and deploys the surrounding app (UI +
Supabase backend) from prompts. Our differentiated work is small and high-value: the
examiner's script (a prompt), the Magic Canvas cue card, and the band-score report schema
(a Tavus tool definition) — the app just receives and renders it.

## Deadline, judging & submission (drives every decision)

- **Hard deadline: 4:00 PM PT today.** If it isn't uploaded by then it can't win. Scope
  ruthlessly; have a working end-to-end demo early, then improve.
- **Must use BOTH PAL Maker and Lovable.** Grab free Lovable Pro + Tavus credits first.
- **A PAL = something you talk to, real back-and-forth** (not a one-way loop). Our examiner
  conversation is exactly this — lean into the genuine dialogue in the pitch.
- **Judged 1–5 on three criteria (15 pts):**
  - *Creativity* — novel use of a PAL. Angle: "the first affordable, realistic IELTS
    Speaking examiner with instant expert scoring."
  - *Functionality* — works end-to-end, solves a real problem, smooth. → A clean,
    complete happy-path demo beats half-built breadth.
  - *Technical Execution* — how well it's built AND **how well it uses the tools.
    Magic Canvas (inside PAL Maker) is explicitly called out.** → Use Magic Canvas.
- **Submission (community.tavus.io):** a **1–2 min video** (what you built, how it works,
  what's standout) + a **short written piece**. Budget ~30 min at the end for these — a
  great build with no video can't qualify.

## The stack (this is the hackathon's intended toolchain)

- **Tavus PALmaker / CVI** — the examiner. A PAL (persona + system prompt) + a stock Face
  (avatar) + a live Conversation (video room). See the `tavus-cvi` skill.
- **Magic Canvas** (a Tavus Canvas skill, in-call) — the examiner renders interactive UI
  during the call. Use it to display the **Part 2 cue card + a visible 1-minute prep
  timer**. This is the cheapest way to win Technical Execution points — design it in.
- **Tavus Post-Call Action = the judge** (a Tavus *tool*, `trigger_type: post_call`). After
  the call, Tavus reads the transcript **and the Raven perception analysis** and fills the
  tool's arguments (the band-score report) with its own LLM, then POSTs them to our endpoint.
  This is how Tavus does the scoring — no external LLM, and it folds in a real *delivery*
  signal a transcript alone can't give. Tool `submit_ielts_assessment` (`t4efc3c554914`) is
  created + attached. See the `tavus-cvi` and `ielts-examiner` skills.
- **Raven-1 perception** — on the examiner PAL, with end-of-call queries about the
  candidate's confidence, composure and delivery. Feeds the post-call judge (esp. Fluency &
  Pronunciation, which a text transcript scores weakly).
- **Lovable** — prompt-to-app builder. Generates the React frontend AND a Supabase backend
  (Postgres, auth, edge functions, secret manager), deploys with one click. See the
  `lovable` skill.
- **Supabase** (provisioned by Lovable) — holds `TAVUS_API_KEY` as an edge-function secret,
  calls Tavus to start the call, and **receives the post-call assessment POST** and stores
  the report row. No scoring LLM call of our own. The browser never sees an API key.

## Decisions already made (don't relitigate)

- **Test scope:** User chooses which parts to run (Part 1, 2, 3, any subset). Multiple
  parts = **one continuous conversation** (no restarts). **Default = full 3-part test.**
  Implemented by passing the chosen parts in the conversation's `conversational_context`.
- **Differentiator = post-call band-score report.** Scoring happens *after* the call
  (matches the real exam). Not real-time coaching.
- **Build the app with Lovable; build the PAL in Tavus PALmaker.** Don't hand-roll a React
  app or a Node server unless Lovable can't express something.
- **Use a STOCK Tavus face** — no custom replica training.
- **One pre-written test** (fixed Part 1/2/3 question set) so the demo is deterministic.

## Architecture

```
Lovable-generated app (React, in the browser)
  │  1. user picks parts → POST to Supabase edge fn  start-test  { parts: [1,2,3] }
  ▼
Supabase Edge Function: start-test (holds TAVUS_API_KEY)        Tavus API (tavusapi.com/v2)
  │  2. create/reuse examiner PAL ──────────────────────────────►  POST /v2/pals → pal_id
  │  3. create conversation (callback_url = scoring fn) ────────►  POST /v2/conversations
  │                                                                 → conversation_url
  │  4. return conversation_url
  ▼
Browser embeds conversation_url (iframe or @tavus/cvi-ui)  ◄── live video call (Daily room)
  │  5. user finishes → end conversation
  ▼
Tavus scores it itself (post-call action submit_ielts_assessment):
  │  6. Tavus reads transcript + Raven perception analysis → its LLM fills the band report
  │  7. Tavus POSTs the filled report (flat JSON) ────────────►  Supabase Edge Function: score
  ▼                                                              (just receives + stores — no LLM call)
Supabase score fn writes the report row to Postgres, keyed by conversation_id
  ▼
Browser reads/subscribes to the reports table → renders the report card
```

### Runnable local demo app (`app/`)

A zero-dependency, **tested** reference of the whole flow lives in `app/` (Python stdlib +
vanilla JS — runs with only `python3`, mirrors the Supabase edge functions). Use it to demo
offline, or as the spec for the Lovable build.
- Run: `cd app && python3 server.py` (LIVE with `TAVUS_API_KEY`) or `DEMO_MODE=1 python3 server.py`.
- Test: `cd app && python3 -m unittest discover -s tests -v` → **23 tests pass**.
- `POST /api/start-test` → real Tavus conversation (verified live 2026-06-27);
  `POST /api/end-test` ends the call so scoring starts immediately; `POST /api/score` is the
  webhook receiver; `GET /api/report/<id>` returns the report — and if it hasn't been received
  it **polls Tavus's verbose conversation** for the post-call action's output, so scoring works
  locally with no public URL. See `app/README.md`.

Three skills document the moving parts — **read them before building**:
- `.claude/skills/tavus-cvi/SKILL.md` — Tavus CVI API: create PAL, create conversation,
  embed, transcript webhook. Exact endpoints + payloads.
- `.claude/skills/lovable/SKILL.md` — how to build this app in Lovable: prompting strategy,
  wiring Supabase edge functions to Tavus, storing secrets, embedding the video call.
- `.claude/skills/ielts-examiner/SKILL.md` — IELTS test structure, the examiner PAL
  system-prompt template, and the band-score rubric encoded as the Tavus post-call action.

## Secrets (store in Supabase edge-function secret manager via Lovable — NOT in the client)

```
TAVUS_API_KEY=        # call Tavus from edge functions (already set in dev shell)
TAVUS_FACE_ID=r68fe8906e53   # stock face "Mary - Office" (professional exam-room look)
TAVUS_PAL_ID=pea55f8508c2    # "IELTS Speaking Examiner" PAL — Magic Canvas + Raven perception + post-call judge
TAVUS_SCORE_TOOL_ID=t4efc3c554914  # post-call action that writes the band report
# No scoring-LLM key needed — Tavus does the judging. (OpenAI/Claude only if you later want a richer rubric.)
```

> **Live resources already created** (2026-06-27), reuse these IDs — don't recreate per session:
> - Examiner PAL `pea55f8508c2`: face `r68fe8906e53`, **Magic Canvas** on, **Raven-1
>   perception** on (confidence/delivery queries).
> - Post-call action `t4efc3c554914` (`submit_ielts_assessment`) **attached** to the PAL.
>   Its `delivery.api.url` is a **placeholder** — patch it to the deployed Supabase `score`
>   URL once Lovable gives you one:
>   ```
>   curl -X PATCH https://tavusapi.com/v2/tools/t4efc3c554914 \
>     -H "x-api-key: $TAVUS_API_KEY" -H "Content-Type: application/json" \
>     -d '[{"op":"replace","path":"/delivery/api/url","value":"https://<project>.functions.supabase.co/score"}]'
>   ```

Two Tavus → app callbacks land at your Supabase endpoints: the **post-call action** POSTs the
band report to its own `delivery.api.url` (the `score` fn), and any conversation events
(incl. `application.post_call_action_executed`) go to the conversation's `callback_url`. Both
are public HTTPS — Lovable/Supabase gives you one, no tunnel needed in prod.

## Build order (time-boxed — get a full happy path working by ~2:30 PM, polish after)

1. **Tavus first, by hand.** In PALmaker (or curl per the `tavus-cvi` skill) create the
   examiner PAL and start one conversation. Confirm you can join the `conversation_url` and
   the examiner talks. This is the demo's spine — prove it before anything else.
2. **Lovable app shell** → "Start mock test" button → an edge function that returns a
   `conversation_url` → embed it. Get a live examiner inside YOUR app.
3. **Magic Canvas cue card** → make the examiner render the Part 2 cue card + a 1-minute
   prep timer on screen. This is the Technical-Execution showpiece; don't skip it.
4. **Score endpoint** → build the Supabase `score` edge function (receives the post-call
   POST, upserts the report row). Then **patch the tool's `delivery.api.url`** to that URL
   (curl above). The judging is already built into Tavus — you only host the receiver.
5. **Verify the judge** → run one real test, confirm Tavus POSTs the filled band report and
   the row lands in Postgres. (Observe via `application.post_call_action_executed`.)
6. **Report card UI** (prompt Lovable to read the reports table). Polish last.
7. **Part selection** → UI control → pass chosen parts into `conversational_context`.

> If you fall behind, the minimum winnable demo is: Lovable app → examiner runs **Part 2**
> with a **Magic Canvas cue card + timer** → Tavus post-call band-score report card. That
> alone hits all three judging criteria and leans hard on Tavus (CVI + Magic Canvas +
> perception + post-call action). Add Parts 1 & 3 only if time allows.

## Submission checklist (do NOT leave to the last 5 minutes — start by ~3:30 PM)

- [ ] **1–2 min video**: the problem (no affordable IELTS Speaking prep) → live demo of a
      real back-and-forth with the examiner → the Magic Canvas cue card → the band-score
      report. State plainly that it's built on PAL Maker + Magic Canvas + Lovable.
- [ ] **Written piece**: what it is, how it works (the architecture diagram above), what's
      standout. AI-generated is allowed.
- [ ] Submit on **community.tavus.io** before **4:00 PM PT**.
- [ ] Team of 2–5 confirmed.

## Demo-day risks / honesty notes

- **Pronunciation scoring from a transcript is weak** (no audio) — mitigated by feeding the
  **Raven perception analysis** (confidence/composure/delivery) into the post-call judge. The
  rubric still scores Pronunciation conservatively and says so; lean on FC/LR/GRA.
- **The 1-minute Part 2 prep pause is safe (verified).** Tavus has no silence-based call
  termination — the only timeouts are `max_call_duration`, `participant_absent_timeout` (only
  *before* anyone joins) and `participant_left_timeout` (only after someone *leaves*); a quiet
  candidate trips none. The examiner stays silent because the PAL's `conversational_flow` has
  `idle_engagement: "off"` (that — NOT `turn_taking_patience` — is what protects the pause). The
  UI shows a 60s prep timer.
- **Latency tuning (learned live):** keep `turn_taking_patience: "medium"` (setting it `high`
  makes every reply feel laggy and does nothing for the pause), and use a fast LLM —
  `tavus-gemini-2.5-flash` on the PAL. The system prompt is kept tight (~640 tokens) and
  prescriptive so a faster model still runs the IELTS script reliably; `custom_greeting` opens
  each call straight into the exam.
- **The post-call judge needs a transcript** — it won't fire on an empty/aborted call, and
  it runs *once* after the call ends (slight delay while transcript + perception finalize).
  Have the report card show a "scoring…" state and subscribe for the row.
- Tavus naming changed: new = `pal_id`/`face_id`, legacy = `persona_id`/`replica_id`. Both
  work; be consistent. See the `tavus-cvi` skill.
- Decide the Tavus embed approach early: simplest is an **iframe / Tavus Embed deployment**;
  `@tavus/cvi-ui` React components give more control but Lovable must accept the dependency.
- **Rehearse the exact demo path.** Fixed questions + a scripted run = no surprises.

## Canonical docs

- Tavus index: https://docs.tavus.io/llms.txt · Full: https://docs.tavus.io/llms-full.txt
- Tavus OpenAPI: https://docs.tavus.io/openapi.yaml
- Lovable docs: https://docs.lovable.dev · Supabase integration:
  https://docs.lovable.dev/integrations/supabase
