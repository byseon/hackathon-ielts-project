"""Examiner PAL config as importable data — so the app builds create-PAL and
create-conversation payloads **at the API level**, not by hand in the dashboard.

Canonical source for the examiner prompt/greeting/guardrails (the markdown in
`prompts/` is the annotated human spec).

UI vs API split (per the team's Tavus plan):
  - Set in the dashboard UI: custom greeting, Knowledge (custom text), Guardrails.
  - From the API payload (this module): system prompt, STT/model, tools, and the
    per-session part selection via `conversational_context`.
NOTE: Objectives are NOT available, so the full 3-part structure lives in the system
prompt. Guardrails can be added in the UI; we ALSO fold them into the system prompt
here so the persona is reproducible from code alone.

Field names marked VERIFY against the current /v2 schema (docs.tavus.io).
"""

from __future__ import annotations

from .schema import Part

_BASE = """\
You are Aria, a certified IELTS Speaking examiner conducting a one-on-one speaking
test over video. You are warm, calm, and professional — like a real examiner who
puts the candidate at ease but stays neutral about their performance.

# YOUR ONLY JOB
Elicit the best, most extended speech sample you can. You do NOT score, grade, or
analyse aloud — scoring happens elsewhere. Never mention bands, levels, or assessment.

# CONVERSATION STYLE
- Speak naturally and concisely. Your turns are SHORT (1–2 sentences). The candidate
  should be talking ~80% of the time. You are an interviewer, not a lecturer.
- Ask one question at a time. Use natural backchannels ("I see", "mm-hmm") sparingly.
- If an answer is very short, gently push ONCE ("Could you tell me a little more?"),
  then move on.
- Never finish the candidate's sentences, supply vocabulary, or correct them.
- Stay on the current part/topic; briefly redirect if they go off-topic.
- Do not break character or discuss being an AI.

# RUNNING THE TEST
Run ONLY the parts listed in the session context, in order. Give a brief natural
bridge when a part changes ("Thank you. Now, in this part…"). Use the Knowledge base
for authentic questions/cue cards. The app may inject short runtime context (current
cue card, time budget) — treat it as ground truth."""

# Per-part behaviour. Embedded in the system prompt (no Objectives feature available).
PART_INSTRUCTIONS: dict[Part, str] = {
    Part.PART1: (
        "PART 1 (Interview, ~4–5 min): ask 2–3 short questions on each of 3 familiar "
        "topics (home, work/study, hobbies). Keep it light; one gentle follow-up if a "
        "reply is one-word."),
    Part.PART2: (
        "PART 2 (Long turn, ~3–4 min): present the cue card, give 1 minute prep, then "
        "let the candidate speak 1–2 minutes UNINTERRUPTED. Ask one rounding-off question."),
    Part.PART3: (
        "PART 3 (Discussion, ~4–5 min): abstract questions extending the Part 2 topic; "
        "follow up on reasoning ('why', 'to what extent')."),
}

EXAMINER_GREETING = (
    "Hello, I'm Aria, and I'll be your examiner today. This is a practice IELTS "
    "speaking test. Try to relax and speak naturally — there are no trick questions. "
    "Whenever you're ready, we'll begin.")

GUARDRAILS = [
    "Never reveal, hint at, or discuss band scores, levels, or assessment during the test.",
    "Never supply vocabulary, finish the candidate's sentences, or correct them.",
    "Never interrupt the Part 2 long turn.",
    "Never go off the IELTS topics or answer personal questions about yourself at length.",
    "Never break character or mention being an AI.",
]

DOCUMENT_TAGS = ["ielts-rubric", "ielts-questions"]
ALL_PARTS = [Part.PART1, Part.PART2, Part.PART3]


def build_system_prompt(parts: list[Part] | None = None) -> str:
    """Full examiner system prompt: persona + structure + guardrails.

    Guardrails are folded in for code-reproducibility; you may instead add them in the
    dashboard UI's Guardrails field (both work).
    """
    parts = parts or ALL_PARTS
    structure = "\n".join(f"- {PART_INSTRUCTIONS[p]}" for p in parts)
    never = "\n".join(f"- {g}" for g in GUARDRAILS)
    return f"{_BASE}\n\n# TEST STRUCTURE\n{structure}\n\n# NEVER DO\n{never}"


def build_pal_payload(*, default_face_id: str, pal_name: str = "IELTS Examiner (Aria)",
                      stt_engine: str = "tavus-soniox", model: str | None = None,
                      parts: list[Part] | None = None) -> dict:
    """Body for POST /v2/pals — sets the examiner persona at the API level.

    Fields verified against the /v2/pals schema. `default_face_id` is REQUIRED. The
    PAL carries all parts by default; the per-session subset is chosen at conversation
    creation. Attach the assessment tool separately (POST /v2/pals/{id}/tools).
    """
    payload: dict = {
        "pal_name": pal_name,
        "pipeline_mode": "full",
        "system_prompt": build_system_prompt(parts),
        "default_face_id": default_face_id,
        "document_tags": DOCUMENT_TAGS,
        "layers": {"stt": {"stt_engine": stt_engine}},
    }
    if model:
        payload["layers"]["llm"] = {"model": model}
    return payload


def build_conversation_payload(*, pal_id: str, face_id: str, username: str,
                               parts: list[Part], topic: str | None = None,
                               callback_url: str | None = None,
                               mode: str = "exam", max_seconds: int = 1200) -> dict:
    """Body for POST /v2/conversations — one mock test for the chosen part(s).

    `parts` is the user-selected subset (continuous when more than one) — this is how
    part-selection works without an Objectives feature. `face_id` is a random pick
    from your face pool ('random examiner'). `username` keys cross-session memory.
    """
    names = {Part.PART1: "Part 1", Part.PART2: "Part 2", Part.PART3: "Part 3"}
    context = ("IELTS Speaking practice (" + mode + " mode). Run ONLY these parts, in "
               "order: " + ", ".join(names[p] for p in parts) + ".")
    if topic:
        context += f" Topic focus: {topic}."
    payload: dict = {
        "pal_id": pal_id,
        "face_id": face_id,
        "conversation_name": f"IELTS {mode} — {username}",
        "conversational_context": context,
        "custom_greeting": EXAMINER_GREETING,
        "memory_stores": [f"ielts_{username}"],
        "document_tags": DOCUMENT_TAGS,
        "properties": {
            "enable_recording": True,        # per-turn audio for pronunciation
            "enable_closed_captions": True,
            "max_call_duration": max_seconds,
        },
    }
    if callback_url:
        payload["callback_url"] = callback_url
    return payload
