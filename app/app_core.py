"""Core request logic for the IELTS demo, framework-free and unit-testable.

The `App` class holds the in-memory report store and a pluggable conversation
creator (so tests can inject a fake instead of hitting Tavus). Each handler
returns `(status_code, body_dict)`.
"""
import os

import tavus

# The flat band-report schema Tavus's post-call action POSTs to /api/score.
# (Mirrors the live tool `submit_ielts_assessment` t4efc3c554914.)
REPORT_FIELDS = [
    "overall_band",
    "fc_band", "fc_evidence", "fc_improvement",
    "lr_band", "lr_evidence", "lr_improvement",
    "gra_band", "gra_evidence", "gra_improvement",
    "pron_band", "pron_evidence", "pron_improvement",
    "summary", "action_1", "action_2", "action_3",
]
NUMERIC_FIELDS = {"overall_band", "fc_band", "lr_band", "gra_band", "pron_band"}

# A realistic sample so the report card is demoable without a full live call.
SAMPLE_REPORT = {
    "overall_band": 6.5,
    "fc_band": 6,
    "fc_evidence": "You spoke at reasonable length but relied on fillers, e.g. "
                   "\"emm, I think, you know, it is quite difficult to say.\"",
    "fc_improvement": "Replace fillers with discourse markers like \"What I mean "
                      "is...\" or \"To put it another way...\" to sound more fluent.",
    "lr_band": 7,
    "lr_evidence": "Good range — you used \"meticulous\", \"a steep learning "
                   "curve\" and \"rewarding\" accurately.",
    "lr_improvement": "Add topic collocations: instead of \"learn a skill\" try "
                      "\"acquire a proficiency\" or \"hone an ability\".",
    "gra_band": 6,
    "gra_evidence": "Mostly accurate, but complex tenses slipped: \"If I would "
                    "have more time, I will practise every day.\"",
    "gra_improvement": "Use the second conditional correctly: \"If I had more "
                       "time, I would practise every day.\"",
    "pron_band": 6,
    "pron_evidence": "No isolated audio is scored; from delivery/perception you "
                     "appeared composed but hesitated on longer sentences.",
    "pron_improvement": "Practise sentence stress on content words and keep a "
                        "steady pace through clause boundaries.",
    "summary": "A competent speaker at a solid Band 6.5. Vocabulary is your "
               "strength; tightening grammatical accuracy and reducing hesitation "
               "would push you toward Band 7.",
    "action_1": "Drill the conditional and past-tense forms until they are automatic.",
    "action_2": "Record yourself answering Part 2 cue cards and cut filler words.",
    "action_3": "Build a bank of topic-specific collocations for common IELTS themes.",
}


def normalize_report(body):
    """Keep only known fields; coerce band fields to numbers when possible."""
    report = {}
    for field in REPORT_FIELDS:
        if field not in body:
            continue
        value = body[field]
        if field in NUMERIC_FIELDS and value is not None:
            try:
                value = float(value)
            except (TypeError, ValueError):
                pass
        report[field] = value
    return report


class App:
    def __init__(self, conversation_creator=None, api_key=None,
                 report_fetcher=None, conversation_ender=None):
        # Inject fakes in tests; defaults hit Tavus for real.
        self.api_key = api_key if api_key is not None else os.environ.get("TAVUS_API_KEY", "")
        self.conversation_creator = conversation_creator or self._default_creator
        self.report_fetcher = report_fetcher or self._default_fetcher
        self.conversation_ender = conversation_ender or self._default_ender
        self.reports = {}  # conversation_id -> report dict

    def _default_creator(self, payload):
        return tavus.create_conversation_via_tavus(payload, self.api_key)

    def _default_fetcher(self, conversation_id):
        return tavus.fetch_post_call_report(conversation_id, self.api_key)

    def _default_ender(self, conversation_id):
        return tavus.end_conversation(conversation_id, self.api_key)

    # --- handlers: return (status_code, body_dict) -------------------------

    def handle_start_test(self, body):
        parts = body.get("parts") or [1, 2, 3]
        candidate_name = body.get("candidate_name")
        try:
            payload = tavus.build_conversation_payload(
                parts, candidate_name, callback_url=body.get("callback_url")
            )
        except ValueError as e:
            return 400, {"error": str(e)}

        try:
            result = self.conversation_creator(payload)
        except tavus.TavusError as e:
            return 502, {"error": str(e)}

        conversation_url = result.get("conversation_url")
        conversation_id = result.get("conversation_id")
        if not conversation_url:
            return 502, {"error": "Tavus did not return a conversation_url",
                         "raw": result}
        return 200, {
            "conversation_id": conversation_id,
            "conversation_url": conversation_url,
            "parts": sorted({int(p) for p in parts}),
        }

    def handle_score(self, body):
        """Receiver for Tavus's post-call action. Stores the band report.

        No AI call here — Tavus already did the scoring. A single-active-test
        demo can fall back to a synthetic id if the body omits conversation_id.
        """
        conversation_id = body.get("conversation_id") or "latest"
        report = normalize_report(body)
        if not report:
            return 400, {"error": "no recognised report fields in body"}
        self.reports[conversation_id] = report
        return 200, {"status": "ok", "conversation_id": conversation_id}

    def handle_end_test(self, conversation_id):
        """End the live call so post-call scoring starts immediately."""
        if not conversation_id:
            return 400, {"error": "conversation_id required"}
        try:
            self.conversation_ender(conversation_id)
        except tavus.TavusError as e:
            return 502, {"error": str(e)}
        return 200, {"status": "ended"}

    def handle_report(self, conversation_id):
        # 1. already received (via webhook receiver or a prior poll)?
        report = self.reports.get(conversation_id) or self.reports.get("latest")
        if report is not None:
            return 200, {"status": "ready", "report": report}

        # 2. otherwise poll Tavus directly for the post-call action's output.
        #    (Works without a public webhook URL — key for local demos.)
        if conversation_id and conversation_id != "latest":
            try:
                fetched = self.report_fetcher(conversation_id)
            except tavus.TavusError:
                fetched = None
            if fetched:
                report = normalize_report(fetched)
                self.reports[conversation_id] = report
                return 200, {"status": "ready", "report": report}

        return 200, {"status": "pending"}
