# IELTS Speaking Coach — Assessment Backend

A voice-ML backend that scores **IELTS Speaking** turns against the official
criteria and turns the result into an **interactive coaching conversation** with a
Tavus PAL (the "examiner"). Built for the Tavus Labs hackathon.

> **Architecture & decisions: [`docs/ASSESSMENT.md`](docs/ASSESSMENT.md)** ·
> long-form rationale: [`docs/ielts-speaking-coach-design.md`](docs/ielts-speaking-coach-design.md) ·
> prompts: [`prompts/`](prompts/) · Tavus setup: [`scripts/setup_tavus.py`](scripts/setup_tavus.py)

## The idea in one picture

```
in-call (Tavus CVI):   Examiner PAL  ──►  elicits speech  ──► utterance + speaking events
                                                                +  isolated per-turn audio
                                  │
   async (this backend):         ▼
   A. features (fluency/lexical/grammar/pronunciation)   ← from word-timings + audio
   B. rubric judges (1 per criterion, RAG-anchored)      → bands + evidence
   C. aggregate (IELTS half-band rounding)               → scorecard
   coaching: features → ONE warm cue → injected back into the call (append-context / echo)
```

Two brains on purpose: the in-call PAL stays lean and low-latency (just talks); all
scoring/analysis happens off-call so it never slows the conversation.

## Layout

| Path | What |
|---|---|
| `src/assessment/schema.py` | Data contracts: `Turn`, `*Features`, `JudgeResult`, `Scorecard` |
| `src/assessment/features/` | **Layer A** — fluency (timings), lexical (MTLD), grammar (spaCy), pronunciation (Charsiu GOP / proxy) |
| `src/assessment/aggregate.py` | **Layer C** — IELTS half-band rounding + overall band |
| `src/assessment/coaching.py` | features → conversational coaching cue (mode/part gated) |
| `src/assessment/session.py` | stateful session: live cues, adaptive focus, conversational wrap-up |
| `src/assessment/stt.py` | assessment-grade verbatim transcription (Soniox) |
| `src/assessment/judges/` | **Layer B** — LLM rubric judges (prompts in `prompts/`) |
| `examples/demo.py` | end-to-end Layer-A demo (no deps) |
| `examples/server.py` | zero-dependency browser demo for functionality testing |

## Run it (no install needed)

```bash
# unit tests
python -m pytest -q

# CLI demo (prints features + scorecard for a synthetic Part-2 turn)
PYTHONPATH=src python examples/demo.py

# browser demo — open http://localhost:8000
PYTHONPATH=src python examples/server.py
```

The core (schema + fluency + lexical + aggregation + coaching) is **pure stdlib**.
Heavier capabilities are optional extras, gated so they never block the core:

```bash
pip install -e ".[lexical]"   # rare-word frequency bands (wordfreq)
pip install -e ".[nlp]"       # grammar parsing (spaCy) + python -m spacy download en_core_web_sm
pip install -e ".[pron]"      # Charsiu GOP pronunciation + forced alignment (torch/transformers)
pip install -e ".[env]"       # optional .env auto-loading (python-dotenv)
```

The rubric judges (Layer B) call the **Tavus hosted LLM** over an OpenAI-compatible
endpoint using stdlib `urllib` — no SDK needed. One `TAVUS_API_KEY` covers STT, the
LLM, and the Knowledge Base (RAG). See [`.env.example`](.env.example).

## Key engineering decisions

- **STT for assessment is decoupled** from the in-call STT. Re-transcribe the
  isolated per-turn audio with **disfluencies kept** + word timestamps + confidence
  (Soniox). Whisper-family ASR normalises fillers away and must not be used here.
- **Pronunciation needs acoustics.** Primary path: **Charsiu** (MIT, wav2vec2)
  forced alignment → Goodness-of-Pronunciation. A zero-dep proxy (STT confidence)
  keeps the pipeline runnable until the model is wired.
- **Scoring is evidence-grounded.** Every judge band must cite a quote or feature;
  calibration is by comparison to retrieved band exemplars (RAG), not abstraction.
