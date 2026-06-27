---
name: tavus-cvi
description: How to use the Tavus Conversational Video Interface (CVI) API — create a PAL (persona/examiner), start a real-time video conversation, embed it with @tavus/cvi-ui, enable Magic Canvas + Raven perception, and have Tavus SCORE the test itself via a post-call action. Use whenever building or debugging the Tavus part of this IELTS project.
---

# Tavus CVI — practical reference

Tavus CVI = a real-time, photorealistic AI video agent that sees, hears, and talks back.
For this project it IS the examiner. You configure three things: a **PAL** (the brain /
system prompt), a **Face** (the avatar — use a stock one), and a **Conversation** (a live
video room the user joins).

- **Base URL:** `https://tavusapi.com/v2`
- **Auth header:** `x-api-key: $TAVUS_API_KEY` (server-side only — never in the browser)
- **Naming note:** new API uses `pal_id` / `face_id`; legacy aliases `persona_id` /
  `replica_id` still work (much online example code uses the legacy names). Pick one set
  and stay consistent. `PAL` == persona; `Face` == replica.

## 1. Pick a stock Face (replica)

You do NOT need to train a custom face for the hackathon. Use a stock one.

- List faces: `GET https://tavusapi.com/v2/faces` (legacy: `/v2/replicas`) with the
  `x-api-key` header, or browse them in the Tavus dashboard / PAL Maker.
- A face id looks like `r90bbd427f71`. Put your chosen one in `TAVUS_FACE_ID`.
- Prefer a calm, professional-looking face for an examiner.

## 2. Create the examiner PAL (persona)

The IELTS examiner behavior lives in `system_prompt`. See the **ielts-examiner** skill for
the actual prompt text to drop in here.

```bash
curl -X POST https://tavusapi.com/v2/pals \
  -H "x-api-key: $TAVUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "pal_name": "IELTS Speaking Examiner",
    "pipeline_mode": "full",
    "default_face_id": "'"$TAVUS_FACE_ID"'",
    "system_prompt": "<<< IELTS examiner system prompt — see ielts-examiner skill >>>",
    "layers": {
      "llm": { "model": "tavus-gemini-2.5-flash" },
      "tts": { "tts_engine": "cartesia" },
      "stt": { "engine": "tavus" }
    }
  }'
```

**LLM model = a latency lever.** Options (speed ⚡ / intelligence 🧠 / naturalness 💬):
`tavus-glm-4.7` (⚡⚡ 🧠🧠🧠 — smart but slower, the global default), `tavus-gemini-2.5-flash`
(⚡⚡ 🧠🧠 💬💬💬 — latency-optimized + most natural), `tavus-gpt-oss` (⚡⚡⚡ 🧠 — snappiest).
For this examiner we use **`tavus-gemini-2.5-flash`**: glm-4.7 felt laggy in the live demo,
and the IELTS script is prescriptive enough that the lighter model follows it reliably while
responding faster and sounding more natural. Keep the system prompt under ~5,000 tokens
(ours ≈ 640) for best speed + instruction-following. `speculative_inference: true` also helps.

Response → `{ "pal_id": "pcb7a34da5fe", ... }`. **Create the PAL once and reuse the id**
(store it in env/config). You don't need to recreate it per test.

Key body fields:
- `system_prompt` (required) — the examiner's instructions.
- `pipeline_mode` (required) — `"full"` (Tavus runs the whole STT→LLM→TTS pipeline). Use
  `"echo"` only if you're driving text yourself (not us).
- `default_face_id` (required) — the stock face.
- `layers` (optional) — override `llm` (model, temperature, tools), `tts` (engine/voice),
  `stt` (engine, hotwords), `perception` (Raven — skip for now),
  `conversational_flow` (turn-taking/interruptibility).

Per-conversation flavor (e.g. "today we run Part 2 only") is better passed at conversation
time via `conversational_context` than baked into the PAL — keeps the PAL reusable.

## 3. Start a conversation (the live video room)

```bash
curl -X POST https://tavusapi.com/v2/conversations \
  -H "x-api-key: $TAVUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "pal_id": "pcb7a34da5fe",
    "face_id": "'"$TAVUS_FACE_ID"'",
    "conversation_name": "IELTS mock — full test",
    "conversational_context": "Run Parts 1, 2 and 3 in one continuous session. Candidate name: Alex.",
    "custom_greeting": "Hello, my name is Emma and I will be your examiner today. Can you tell me your full name, please?",
    "callback_url": "'"$PUBLIC_CALLBACK_URL"'/api/tavus-webhook",
    "properties": {
      "max_call_duration": 1200,
      "enable_recording": false,
      "enable_closed_captions": true,
      "language": "english",
      "participant_absent_timeout": 60
    }
  }'
```

Response (the important field is `conversation_url`):
```json
{
  "conversation_id": "c123456",
  "conversation_url": "https://tavus.daily.co/c123456",
  "status": "active"
}
```

- `conversation_url` is a Daily room URL — hand it to the React `<Conversation>` component
  (or an iframe). It's join-able immediately.
- `conversational_context` is your per-session steering — e.g. which parts to run, the
  candidate's name. This is how you implement the "user picks parts" requirement without
  editing the PAL.
- `custom_greeting` — the examiner's exact first line. Good for a clean demo open.
- `properties.max_call_duration` is in **seconds** (cap it so demos can't run away).
- `callback_url` is where Tavus POSTs events, including the transcript (section 6).

End a conversation explicitly when the user is done (frees resources, triggers transcript):
```
POST https://tavusapi.com/v2/conversations/{conversation_id}/end
```

## 4. Embed in React with @tavus/cvi-ui

```bash
npx @tavus/cvi-ui@latest init
npx @tavus/cvi-ui@latest add conversation
# pulls in @daily-co/daily-react and @daily-co/daily-js
```

```tsx
import { CVIProvider } from './components/cvi/components/cvi-provider';
import { Conversation } from './components/cvi/components/conversation';

export default function TestRoom({ conversationUrl }: { conversationUrl: string }) {
  return (
    <CVIProvider>
      <div style={{ width: '100%', height: '100vh' }}>
        <Conversation
          conversationUrl={conversationUrl}
          onLeave={() => {
            // user clicked leave → tell backend to end the call & kick off scoring
            // POST /api/end-test { conversationId }
          }}
        />
      </div>
    </CVIProvider>
  );
}
```

Flow: browser asks **your backend** to start the test → backend calls Tavus (section 3) →
returns `conversation_url` → you render `<Conversation conversationUrl={...}>`. The browser
never touches `TAVUS_API_KEY`.

**iframe alternative** (no React, fastest possible):
```html
<iframe src="CONVERSATION_URL"
  allow="camera; microphone; fullscreen; display-capture; autoplay"
  style="width:100%; height:600px; border:none;"></iframe>
```

## 5. Getting the transcript (for scoring)

Set `callback_url` on the conversation. After the call ends, Tavus POSTs the
**`application.transcription_ready`** event to it:

```json
{
  "event_type": "application.transcription_ready",
  "conversation_id": "c123456",
  "message_type": "application",
  "timestamp": "2026-06-27T18:40:00Z",
  "properties": {
    "transcript": [
      { "role": "assistant", "content": "Hello, my name is Emma..." },
      { "role": "user",      "content": "My name is Alex Chen." },
      { "role": "assistant", "content": "Thank you. In the first part..." }
    ]
  }
}
```

For THIS project you **don't have to handle the transcript yourself** — the post-call action
(section 8) does the scoring and POSTs the finished report. You only need `callback_url` if
you want to observe events. Useful ones: `application.perception_analysis` (the delivery
summary), `application.post_call_action_executed` (confirms the judge ran + shows what it
sent), plus `system.replica_joined`, `system.shutdown`, `conversation.utterance`.
`application.transcription_ready` (shape above) is handy for debugging or if you ever want to
re-score externally.

**Dev tip:** webhooks need a public HTTPS URL. Use `ngrok http 3000` or `cloudflared` and
point `PUBLIC_CALLBACK_URL` at it. If you can't tunnel, poll
`GET /v2/conversations/{id}?verbose=true` after the call to read the transcript instead.

## 6. Magic Canvas (in-call interactive UI — judged for Technical Execution)

Magic Canvas lets the PAL render interactive cards (text, charts, questions, inputs,
calendars, alerts) in a side rail next to the examiner's face during the call. The
hackathon explicitly rewards good Magic Canvas use — **use it.**

**Enable on the examiner PAL** (once):
```bash
curl -X PUT https://tavusapi.com/v2/pals/$TAVUS_PAL_ID/skills/magic_canvas \
  -H "x-api-key: $TAVUS_API_KEY" -H "Content-Type: application/json" \
  -d '{ "config": {} }'
# DELETE on the same URL to remove. {} enables all components except scheduling_embed.
```

**Components (all v1):**
- Interactive (user submits/skips): `question` (multiple-choice + optional "Other"),
  `input` (text/email/number/phone), `calendar`, `scheduling_embed`.
- Display-only (dismiss): `text` (formatted card), `chart` (data viz), `alert` (notice).

**How it flows:** the PAL decides when to show a card (drive this from the system prompt —
e.g. "When you begin Part 2, display the cue card text on the canvas"). The card renders
in the rail. When the user interacts, the PAL reacts conversationally AND Tavus sends a
`canvas.interaction` webhook to your `callback_url`.

**Frontend:** the hosted `<tavus-embed>` / `<tavus-widget>` tags render canvas
automatically; or use the React `<MagicCanvas>` component from `@tavus/cvi-ui`.

**IELTS uses:**
- **Part 2 cue card** → a `text` card showing the topic + bullet points (the showpiece).
  Trigger it from the PAL prompt at the start of Part 2.
- **1-minute prep timer** → there's no dedicated timer component; show it as an `alert`
  ("1 minute prep — begin when ready") or implement the countdown in the Lovable UI.
- **End-of-test** → an `input`/`question` card for a quick self-rating, or a `chart` of the
  band scores IF you score in-call (the post-call report is otherwise rendered in Lovable).

## 7. Raven perception (a real delivery signal)

The examiner PAL runs the **`raven-1`** perception model (default for new PALs; we set it
explicitly). It watches the candidate during the call and answers end-of-call queries we
defined — confidence, composure, eye contact, signs of hesitation/ease. This is the only
**delivery** signal available (we have no isolated audio), and it feeds the post-call judge
so Fluency & Pronunciation aren't scored from text alone.

Enabled on the PAL via `layers.perception`:
```bash
curl -X PATCH https://tavusapi.com/v2/pals/$TAVUS_PAL_ID \
  -H "x-api-key: $TAVUS_API_KEY" -H "Content-Type: application/json" \
  -d '[{ "op": "add", "path": "/layers/perception", "value": {
      "perception_model": "raven-1",
      "perception_analysis_queries": [
        "On a scale of 1 to 100, how confident and composed did the candidate appear while speaking?",
        "Did the candidate maintain natural eye contact and engagement, or did they seem hesitant, nervous, or distracted?",
        "Describe the candidate overall delivery: signs of ease, effort, or hesitation while producing spoken English."
      ] } }]'
```
The answers arrive as an `application.perception_analysis` event on `callback_url`, and Tavus
also feeds them into the post-call action (section 8) automatically.

## 8. Post-call action = Tavus does the scoring (NO external LLM)

This is how Tavus grades the test. A **post-call action** is a Tavus *tool* with
`trigger_type: "post_call"`. After the call ends, Tavus reads the **transcript + perception
analysis**, uses its own LLM to fill the tool's open arguments — which we define to BE the
band-score report — and POSTs that JSON to our endpoint. Runs once per conversation; needs a
transcript (won't fire on an empty call).

**Already created + attached** (reuse, don't recreate): tool `submit_ielts_assessment` =
`t4efc3c554914` on PAL `pea55f8508c2`. We use a **flat** parameter schema (no nested objects)
for reliable AI-fill, and put the whole IELTS rubric in the `description`s. The live body:

```bash
curl -X POST https://tavusapi.com/v2/tools \
  -H "x-api-key: $TAVUS_API_KEY" -H "Content-Type: application/json" \
  -d '{
    "name": "submit_ielts_assessment",
    "description": "After an IELTS Speaking mock test ends, score the candidate (the user role) as a strict, fair, certified IELTS examiner on the four 0-9 criteria (whole/half bands): Fluency & Coherence, Lexical Resource, Grammatical Range & Accuracy, Pronunciation. Score only the candidate; quote their words as evidence. Use the perception analysis (confidence/delivery) for Fluency & Pronunciation (no isolated audio). Anchors: 5 modest, 6 competent, 7 good operational command, 8 very good. Do not penalise a skipped part.",
    "trigger_type": "post_call",
    "parameters": {
      "type": "object",
      "properties": {
        "overall_band":     { "type": "number", "description": "Mean of the four bands, rounded to nearest 0.5. 0-9." },
        "fc_band":          { "type": "number", "description": "Fluency & Coherence band; factor in visible fluency/hesitation from perception." },
        "fc_evidence":      { "type": "string", "description": "1-2 sentences, quoting the candidate, justifying the FC band." },
        "fc_improvement":   { "type": "string", "description": "One concrete higher-band fluency/coherence technique." },
        "lr_band":          { "type": "number", "description": "Lexical Resource band: range/precision, collocation, idiom, paraphrase." },
        "lr_evidence":      { "type": "string", "description": "1-2 sentences, quoting the candidate, justifying the LR band." },
        "lr_improvement":   { "type": "string", "description": "One concrete vocabulary upgrade vs what they used." },
        "gra_band":         { "type": "number", "description": "Grammatical Range & Accuracy band: structure variety, error frequency." },
        "gra_evidence":     { "type": "string", "description": "1-2 sentences, quoting the candidate, noting specific errors." },
        "gra_improvement":  { "type": "string", "description": "One concrete grammar fix / complex structure, with an example." },
        "pron_band":        { "type": "number", "description": "Pronunciation band; no audio, so conservative + use perception/delivery." },
        "pron_evidence":    { "type": "string", "description": "1-2 sentences referencing perception/delivery, stating the no-audio limit." },
        "pron_improvement": { "type": "string", "description": "One concrete pronunciation/delivery focus." },
        "summary":          { "type": "string", "description": "2-3 sentence overall verdict and current level." },
        "action_1":         { "type": "string", "description": "Most important specific next step to raise the band." },
        "action_2":         { "type": "string", "description": "Second most important next step." },
        "action_3":         { "type": "string", "description": "Third most important next step." }
      },
      "required": ["overall_band","fc_band","fc_evidence","fc_improvement","lr_band","lr_evidence","lr_improvement","gra_band","gra_evidence","gra_improvement","pron_band","pron_evidence","pron_improvement","summary","action_1","action_2","action_3"]
    },
    "delivery": { "api": { "url": "https://REPLACE-WITH-SUPABASE-PROJECT.functions.supabase.co/score", "method": "POST" } }
  }'
```
Then attach: `POST /v2/pals/$TAVUS_PAL_ID/tools` with `{"tool_ids":["t4efc3c554914"]}`.

- **Delivery:** with no `body_template`, Tavus auto-routes all filled args as the JSON POST
  body — so the `score` fn receives exactly the flat object above. `delivery.api` only (no
  app-message after the call). Auth optional (`auth.type: hmac` to verify the sender).
- **Patch the URL** when Supabase is live:
  `PATCH /v2/tools/t4efc3c554914` → `[{"op":"replace","path":"/delivery/api/url","value":"https://<project>.functions.supabase.co/score"}]`
- **Tune the rubric** by patching field `description`s on the tool — no redeploy.
- **Observe it ran:** an `application.post_call_action_executed` event hits `callback_url`
  with `status` + the exact `request.body` Tavus sent (also on `GET /conversations/{id}?verbose=true`).
- **No public URL? Pull the report instead of receiving it.** The generated `request.body` is
  stored on the conversation **even when the delivery POST fails** (e.g. the URL is still the
  placeholder, or you're on localhost). So you don't need a webhook for a local demo: after the
  call ends, poll `GET /v2/conversations/{id}?verbose=true`, find the event with
  `event_type == "application.post_call_action_executed"` (and your `tool_id`), and parse
  `properties.request.body` (a JSON string) → that's the band report. The runnable `app/` does
  exactly this (`tavus.fetch_post_call_report`), which is why scoring works with no tunnel.
- **Make scoring start promptly:** explicitly end the call (`POST /conversations/{id}/end`) on
  "Finish" — otherwise Tavus waits out `participant_left_timeout` before the post-call action
  even runs. The post-call action needs a transcript, so it only fires after a real exchange.
- **Char limit:** tool `description` + `parameters` JSON must total ≤ 10,000 chars (ours ≈ 3.8k).

## 9. Letting the candidate pause (the 1-minute Part 2 prep) — conversational_flow

IELTS Part 2 gives the candidate a silent minute to prepare. Two facts make this safe on
Tavus (verified live 2026-06-27):

1. **No silence-based call termination.** The only call-ending timeouts (conversation
   `properties`) are `max_call_duration`, `participant_absent_timeout` (fires only *before*
   anyone joins) and `participant_left_timeout` (only after someone *leaves*). A participant
   sitting quietly trips none of them. There is no "idle/silence ends the call" timer.
2. **The examiner must not break the silence.** This is what protects the pause — and it's
   `idle_engagement`, NOT `turn_taking_patience`. They're independent (docs are explicit):
   - `idle_engagement: "off"` (default) — the PAL *never* proactively breaks silence; it only
     speaks in response to user input. This is the ONLY setting the pause depends on.
     (`patient`/`eager` would re-engage after a pause — don't use them here.)
   - `turn_taking_patience` controls how long the PAL waits *after the candidate stops
     talking* before replying — i.e. it's a **latency knob**, not a pause knob. We use
     `"medium"` (the default). ⚠️ Do NOT set this to `"high"` to "protect the pause" — it
     does nothing for the pause and makes every reply feel laggy/unbearable. (We learned this
     the hard way: `high` made the live demo feel non-real-time.)
   ```bash
   curl -X PATCH https://tavusapi.com/v2/pals/$TAVUS_PAL_ID \
     -H "x-api-key: $TAVUS_API_KEY" -H "Content-Type: application/json" \
     -d '[{"op":"replace","path":"/layers/conversational_flow/turn_taking_patience","value":"medium"}]'
   ```
   Other knobs in this layer: `pal_interruptibility` (how easily the user interrupts the PAL),
   `voice_isolation`, `wake_phrase`. The greeting is always non-interruptible regardless.

The UI still shows a visible 60-second prep countdown; the examiner waits silently until the
candidate begins. See the runnable `app/` for the timer + the conversation payload.

## Gotchas

- API key is **server-side only**. Browser gets `conversation_url`, nothing else.
- The post-call judge runs **once, after** the call — not mid-conversation. It needs a
  transcript, so it won't fire on an empty/aborted call.
- `max_call_duration` and timeouts are in **seconds**.
- Stock faces only for the hackathon — custom replica training takes too long.
- If you see `persona_id`/`replica_id` in old examples, they map to `pal_id`/`face_id`.
- Recording is off by default; only enable it if you actually need audio later.

## Canonical docs

- Index: https://docs.tavus.io/llms.txt · Full: https://docs.tavus.io/llms-full.txt
- OpenAPI: https://docs.tavus.io/openapi.yaml
- React examples: https://github.com/Tavus-Engineering/tavus-examples
