# PAL — IELTS Speaking demo app (runnable reference)

A zero-dependency, runnable version of the IELTS Speaking flow: pick parts → talk to the
Tavus video examiner → get a band-score report. Pure Python stdlib + vanilla JS, so it runs
with nothing but `python3`. In production this same flow is built in Lovable (React +
Supabase edge functions); this app is the tested reference of the exact request shapes.

## Run

```bash
cd app
# LIVE (real Tavus examiner — needs the key in your shell):
TAVUS_API_KEY=$TAVUS_API_KEY python3 server.py
# DEMO (no Tavus call, no credits — great for offline UI demos):
DEMO_MODE=1 python3 server.py
```
Open http://localhost:8000.

| Env | Default | Purpose |
|-----|---------|---------|
| `TAVUS_API_KEY` | — | Server-side only. Without it the app auto-runs in demo mode. |
| `TAVUS_PAL_ID`  | `pea55f8508c2` | The examiner PAL (Magic Canvas + Raven + post-call judge). |
| `TAVUS_FACE_ID` | `r68fe8906e53` | Stock examiner face. |
| `PORT` | `8000` | |
| `DEMO_MODE` | off | `1` forces a fake conversation URL. |

## Test

```bash
cd app
python3 -m unittest discover -s tests -v      # 23 tests, ~0.5s
```

## Endpoints (mirror the Supabase edge functions)

- `POST /api/start-test` `{parts:[1,2,3], candidate_name?}` → `{conversation_url, conversation_id}`.
  Sends a per-part `custom_greeting` so the examiner opens straight into the exam.
- `POST /api/end-test` `{conversation_id}` — ends the live Tavus call so post-call scoring
  begins immediately (instead of waiting out the leave-timeout).
- `POST /api/score` — webhook receiver for **Tavus's post-call action**; stores the flat band
  report. (Point the tool's `delivery.api.url` here when you have a public URL.)
- `GET  /api/report/<conversation_id>` → `{status:"pending"|"ready", report?}`. If the report
  hasn't been POSTed in, it **polls Tavus's verbose conversation** and extracts the post-call
  action's generated body — so scoring works locally with no public webhook URL.

## Scoring latency notes

The post-call band report is **not** instant: Tavus only runs the post-call action after the
call ends, once the transcript + Raven perception finalize (typically up to ~a minute). The app
ends the call on "Finish", then polls every 2s and shows a "scoring…" state. If you ever need it
faster for a demo, the "Load sample report" button renders a realistic report immediately via
the real `/api/score` → store → poll path.

## Examiner config (on PAL `pea55f8508c2`)

- LLM `tavus-gemini-2.5-flash` (latency-optimized + natural), `speculative_inference` on.
- `conversational_flow`: `turn_taking_patience: "medium"` (responsive), `idle_engagement: "off"`
  (protects the Part 2 pause). A tight ~640-token prescriptive system prompt keeps it on the
  IELTS script.

## The 1-minute pause — verified safe

IELTS Part 2 gives the candidate a silent minute to prepare. Tavus allows this because:

1. **No silence-based call termination exists.** The only call-ending timeouts are
   `max_call_duration`, `participant_absent_timeout` (fires only *before* anyone joins) and
   `participant_left_timeout` (fires only after someone *leaves*). A participant sitting
   quietly trips none of them. (See `tests/test_app.py::test_no_silence_killing_timeout_present`.)
2. **The examiner stays silent during the pause.** The PAL's `conversational_flow` is set to
   `idle_engagement: "off"` (never breaks silence) and `turn_taking_patience: "high"` (won't
   grab natural pauses). Set once on PAL `pea55f8508c2`.
3. The UI shows a visible 60-second prep timer; the examiner waits until the candidate begins.

Confirmed live on 2026-06-27: a real conversation was created with the silent-prep context,
joined, and ended cleanly.
