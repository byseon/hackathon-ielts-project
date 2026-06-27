"""Tavus integration for the IELTS Speaking demo.

Pure, testable helpers + a thin urllib client. The API key is read from the
environment and NEVER sent to the browser (this module only runs server-side).

In production this logic lives in a Supabase edge function (Lovable). This file
is the runnable reference of the exact same request shape.
"""
import json
import os
import urllib.request
import urllib.error

TAVUS_BASE_URL = "https://tavusapi.com/v2"

# Live resources already created in Tavus (reuse — don't recreate per session).
DEFAULT_PAL_ID = "pea55f8508c2"   # IELTS Speaking Examiner (Magic Canvas + Raven + post-call judge)
DEFAULT_FACE_ID = "r68fe8906e53"  # stock face "Mary - Office"

# IELTS cap: 20 min is plenty for a full 3-part test (Tavus max is 3600s).
MAX_CALL_DURATION = 1200

PART_LABELS = {
    1: "Part 1 (Introduction and interview)",
    2: "Part 2 (Individual long turn with a cue card)",
    3: "Part 3 (Two-way discussion)",
}


def build_conversational_context(parts, candidate_name=None):
    """Per-session steering passed to the examiner PAL.

    `parts` is a list/subset of [1, 2, 3]. Multiple parts run as ONE continuous
    test. This is how the "user picks parts" requirement is implemented without
    editing the PAL.
    """
    parts = sorted({int(p) for p in parts}) if parts else [1, 2, 3]
    for p in parts:
        if p not in PART_LABELS:
            raise ValueError(f"invalid part: {p!r} (must be 1, 2 or 3)")

    name = (candidate_name or "").strip()
    name_clause = f" The candidate's name is {name}." if name else ""

    if len(parts) == 1:
        label = PART_LABELS[parts[0]]
        body = f"Run only {label} of the IELTS Speaking test."
    else:
        labels = ", ".join(PART_LABELS[p] for p in parts)
        body = (
            "Run the following parts of the IELTS Speaking test back-to-back as "
            f"ONE continuous test, in order: {labels}."
        )

    pause_note = (
        " In Part 2, after presenting the cue card, invite the candidate to take "
        "up to a minute to prepare and to begin speaking whenever they are ready; "
        "stay silent while they prepare and do not interrupt natural pauses while "
        "they speak."
    )
    return body + (pause_note if 2 in parts else "") + name_clause


def build_custom_greeting(parts, candidate_name=None):
    """The examiner's exact first line — launches straight into the exam so the
    candidate immediately knows it's an IELTS test (not an open chat)."""
    parts = sorted({int(p) for p in parts}) if parts else [1, 2, 3]
    name = (candidate_name or "").strip()
    who = "I'm Emma, and I'll be your examiner for today's IELTS Speaking test."
    first = parts[0]
    if first == 1:
        ask = (f"To begin, could you tell me your full name, please?" if not name
               else f"To begin, can you confirm your full name for me, {name}?")
        return f"Hello, {who} {ask}"
    if first == 2:
        return (f"Hello, {who} Today we'll focus on Part 2, the long turn. "
                "I'm going to give you a topic to talk about, so let me show you your cue card.")
    return (f"Hello, {who} Today we'll do Part 3, a two-way discussion about learning "
            "and skills. Let's begin.")


def build_conversation_payload(parts, candidate_name=None, pal_id=None, face_id=None,
                               callback_url=None):
    """The exact JSON body POSTed to Tavus POST /v2/conversations.

    What keeps both the silent prep minute and the candidate's mid-answer thinking
    pauses SAFE is PAUSE-DRIVEN turn-taking, NOT a hard-coded timer:
      * idle_engagement="off" — the examiner never proactively breaks silence, so
        it stays quiet through the prep minute and only speaks once the candidate
        yields a turn (it physically cannot "count a minute then talk").
      * turn_detection_model="sparrow-1" + turn_taking_patience="medium" — semantic
        turn detection decides when the candidate has actually finished a thought
        rather than cutting in after a fixed gap. These live on the PAL (see the
        tavus-cvi skill), set once. (Do NOT use turn_taking_patience="high": it
        adds latency to every reply and does nothing for the pause.)
      * No silence-based timeout exists. The only call-ending timeouts are below,
        and none of them fire while a participant is present and simply quiet:
          - max_call_duration: hard cap on total length
          - participant_absent_timeout: only before anyone joins
          - participant_left_timeout: only after someone leaves
    """
    payload = {
        "pal_id": pal_id or os.environ.get("TAVUS_PAL_ID", DEFAULT_PAL_ID),
        "face_id": face_id or os.environ.get("TAVUS_FACE_ID", DEFAULT_FACE_ID),
        "conversation_name": "IELTS Speaking mock test",
        "conversational_context": build_conversational_context(parts, candidate_name),
        "custom_greeting": build_custom_greeting(parts, candidate_name),
        "properties": {
            "max_call_duration": MAX_CALL_DURATION,
            "participant_absent_timeout": 120,
            "participant_left_timeout": 10,
            "enable_recording": False,
            "enable_closed_captions": True,
            "language": "english",
        },
    }
    if callback_url:
        payload["callback_url"] = callback_url
    return payload


def create_conversation_via_tavus(payload, api_key, timeout=30):
    """Real Tavus call. Returns the parsed JSON response dict.

    Raises TavusError on a non-2xx response.
    """
    if not api_key:
        raise TavusError("TAVUS_API_KEY is not set")
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{TAVUS_BASE_URL}/conversations",
        data=data,
        method="POST",
        headers={"x-api-key": api_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        raise TavusError(f"Tavus returned {e.code}: {detail}") from e
    except urllib.error.URLError as e:
        raise TavusError(f"could not reach Tavus: {e.reason}") from e


def end_conversation(conversation_id, api_key, timeout=15):
    """End the live call immediately so post-call scoring starts now instead of
    waiting for the participant-left timeout. Idempotent enough for a demo."""
    if not api_key:
        raise TavusError("TAVUS_API_KEY is not set")
    req = urllib.request.Request(
        f"{TAVUS_BASE_URL}/conversations/{conversation_id}/end",
        data=b"", method="POST",
        headers={"x-api-key": api_key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        # already ended / not found is fine for our purposes
        if e.code in (404, 409, 400):
            return e.code
        raise TavusError(f"end failed {e.code}: {e.read().decode('utf-8','replace')}") from e
    except urllib.error.URLError as e:
        raise TavusError(f"could not reach Tavus: {e.reason}") from e


SCORE_TOOL_ID = "t4efc3c554914"


def fetch_post_call_report(conversation_id, api_key, tool_id=SCORE_TOOL_ID, timeout=20):
    """Pull the band report Tavus generated, WITHOUT needing a public webhook.

    The post-call action's generated `request.body` is stored on the conversation
    regardless of whether the delivery POST succeeded, and is returned under
    `events` on the verbose GET. Returns the parsed flat report dict, or None if
    the action hasn't run yet (call still finalizing).
    """
    if not api_key:
        raise TavusError("TAVUS_API_KEY is not set")
    url = f"{TAVUS_BASE_URL}/conversations/{conversation_id}?verbose=true"
    req = urllib.request.Request(url, headers={"x-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise TavusError(f"verbose GET {e.code}: {e.read().decode('utf-8','replace')}") from e
    except urllib.error.URLError as e:
        raise TavusError(f"could not reach Tavus: {e.reason}") from e

    return extract_report_from_events(data.get("events") or [], tool_id)


def extract_report_from_events(events, tool_id=SCORE_TOOL_ID):
    """Find the post_call_action_executed event for our tool and parse its body."""
    for ev in events:
        if ev.get("event_type") != "application.post_call_action_executed":
            continue
        props = ev.get("properties") or {}
        if tool_id and props.get("tool_id") not in (tool_id, None):
            continue
        body = (props.get("request") or {}).get("body")
        if body is None:
            continue
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except (json.JSONDecodeError, ValueError):
                continue
        if isinstance(body, dict) and body:
            return body
    return None


class TavusError(Exception):
    pass
