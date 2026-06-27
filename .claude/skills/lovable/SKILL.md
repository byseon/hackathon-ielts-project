---
name: lovable
description: How to build and ship this IELTS app with Lovable (the prompt-to-app builder, a co-sponsor of this hackathon). Covers what Lovable is and isn't, the prompting strategy, wiring a Supabase edge function to start the Tavus call, receiving Tavus's post-call band-score report (Tavus does the scoring — no external LLM), storing secrets, embedding the video call, and rendering the report. Use when building the app UI/backend for this project.
---

# Lovable — build & ship the app

**What it is:** an AI app builder. You describe the app in plain English in a chat, and it
generates a **React frontend + a Supabase backend** (Postgres DB, auth, serverless **edge
functions**, secret manager) and deploys it with one click. There is no "Lovable API" to
call — you *prompt* it, then edit/iterate in chat, and it ships a real full-stack app.

**Why we use it:** it's a hackathon co-sponsor (you get credits + judges reward using it),
and it removes nearly all frontend/backend boilerplate so we can focus on the Tavus examiner.

**Mental model for this project:** Lovable builds the *app the PAL lives in*. The Tavus
PAL/examiner — and the **scoring**, which Tavus does itself via a post-call action — is built
separately in Tavus (see `tavus-cvi` + `ielts-examiner` skills). Lovable's job is just: the
landing UI, the "start test" flow, the embedded video call, the report card, and **two thin
Supabase edge functions** — `start-test` (calls Tavus to open the call) and `score` (receives
Tavus's post-call report and stores it). No scoring LLM call of our own.

## The golden rule: the API key goes in a Supabase edge function, never the client

Lovable apps run in the browser. **Never** put `TAVUS_API_KEY` in frontend code. Use Supabase
**edge functions** (server-side) and Lovable's **secret manager**. When you prompt Lovable to
call an external API that needs a key, it detects the need and prompts you with a UI to paste
the secret, stored in Supabase's edge-function secret manager. (The `score` fn needs **no**
secret — it just receives Tavus's POST; optionally verify the HMAC signature.)

## Setup

1. In Lovable, connect **Supabase** (Settings → Integrations). This provisions the Postgres
   DB, auth, edge functions, and secret storage. Most backend features require this.
2. Add secrets when prompted (only one real key): `TAVUS_API_KEY`, plus
   `TAVUS_FACE_ID=r68fe8906e53` and `TAVUS_PAL_ID=pea55f8508c2` (the examiner PAL already
   created in Tavus — Magic Canvas + Raven perception + the post-call scoring action
   `t4efc3c554914` all attached). **No OpenAI/Anthropic key needed — Tavus does the scoring.**

## Prompting strategy (build incrementally — one capability per prompt)

Lovable works best with small, specific, sequential prompts. Suggested sequence:

1. **Scaffold the UI**
   > "Build a clean single-page app called PAL for practicing the IELTS Speaking test.
   > A hero section explaining it, a control to choose which test parts to run (Part 1,
   > Part 2, Part 3 — checkboxes, all selected by default), and a big 'Start mock test'
   > button. Modern, calm, exam-prep aesthetic."

2. **Edge function: start the Tavus conversation**
   > "Create a Supabase edge function `start-test` that takes a JSON body `{ parts: number[] }`.
   > It calls the Tavus API `POST https://tavusapi.com/v2/conversations` with header
   > `x-api-key: TAVUS_API_KEY` and body including `pal_id: TAVUS_PAL_ID`,
   > `face_id: TAVUS_FACE_ID`, a `conversational_context` string telling the examiner which
   > parts to run continuously, and `properties.max_call_duration: 1200`. Return BOTH the
   > `conversation_url` and `conversation_id` from the response.
   > Wire the Start button to call this function and store the returned values."

   (The band report does **not** come back through `callback_url` — Tavus's *post-call action*
   POSTs it straight to the `score` function, step 4. You may still set `callback_url` to the
   `score` fn if you want the `application.post_call_action_executed` / transcript events too,
   but it's optional.)

3. **Embed the live video call**
   > "When we have a conversation_url, show the Tavus video call full-width by embedding it
   > in an iframe with `allow='camera; microphone; fullscreen; display-capture; autoplay'`.
   > Add a 'Finish test' button."
   (For richer control you can instead use `@tavus/cvi-ui`'s `CVIProvider` + `Conversation`
   components — see `tavus-cvi` skill — but the iframe is the fastest path inside Lovable.)

4. **Reports table + `score` receiver edge function** (Tavus already did the scoring)
   > "Create a Postgres table `reports`: conversation_id text primary key, overall_band
   > numeric, fc_band numeric, fc_evidence text, fc_improvement text, lr_band numeric,
   > lr_evidence text, lr_improvement text, gra_band numeric, gra_evidence text,
   > gra_improvement text, pron_band numeric, pron_evidence text, pron_improvement text,
   > summary text, action_1 text, action_2 text, action_3 text, created_at timestamptz
   > default now().
   > Create a public Supabase edge function `score` that accepts a POST with a JSON body
   > containing exactly those fields (plus possibly a `conversation_id`). It does NOT call
   > any AI — it just upserts the body into `reports` keyed by `conversation_id` and returns
   > 200 'ok'. Don't require auth on it."

   Then **point Tavus's post-call action at this function** (one-time, from a terminal):
   ```bash
   curl -X PATCH https://tavusapi.com/v2/tools/t4efc3c554914 \
     -H "x-api-key: $TAVUS_API_KEY" -H "Content-Type: application/json" \
     -d '[{"op":"replace","path":"/delivery/api/url","value":"https://<project>.functions.supabase.co/score"}]'
   ```
   Now every finished test makes Tavus fill the band report (from transcript + perception)
   and POST it straight into your `reports` table. If `conversation_id` isn't in the body,
   read it from the `application.post_call_action_executed` event on your `callback_url`, or
   pass it as a fixed param — but a single-active-test demo can just upsert the latest row.

5. **Report card UI**
   > "After the test ends, subscribe to (or poll) the `reports` table for the latest row and
   > render a report card: overall band big at the top, then the four criteria
   > (Fluency & Coherence, Lexical Resource, Grammatical Range & Accuracy, Pronunciation),
   > each showing its band + evidence + improvement, then the three action items. Show a
   > 'scoring…' state until the row arrives (Tavus takes a few seconds post-call)."

## Tips & gotchas

- **Iterate in small prompts.** One feature per message; verify before moving on. Big
  one-shot prompts produce messy apps that are hard to fix under time pressure.
- **Let Lovable own the schema.** Describe the data you want; let it write the SQL/edge
  functions. Then tweak.
- **The webhook URL is public.** Supabase edge functions get a public HTTPS URL — use it as
  the Tavus `callback_url`. No ngrok/tunnel needed (unlike a laptop dev server).
- **Realtime makes the report feel instant.** Ask Lovable to use Supabase Realtime to push
  the new `reports` row to the client instead of polling.
- **Keep the Tavus PAL in PALmaker**, not in Lovable — reference it by `TAVUS_PAL_ID`. This
  keeps the examiner's behavior editable without redeploying the app.
- **If Lovable balks at an external dependency** (e.g. `@tavus/cvi-ui`), fall back to the
  iframe embed — it always works.

## Docs

- Lovable: https://docs.lovable.dev
- Supabase integration: https://docs.lovable.dev/integrations/supabase
- Supabase edge functions & secrets: https://supabase.com/docs/guides/functions
