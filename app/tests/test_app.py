"""Tests for the IELTS Speaking demo: run with `python3 -m unittest -v` from app/.

Covers the conversation request shape (incl. the 1-minute-pause safety), the
report receiver/store, and a live HTTP smoke test against the real server in
demo mode (no Tavus credits used).
"""
import json
import os
import sys
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

# import the app modules (parent dir)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DEMO_MODE"] = "1"  # ensure server module never tries a real call

import tavus
from app_core import App, normalize_report, SAMPLE_REPORT, REPORT_FIELDS


def fake_creator(payload):
    return {"conversation_id": "c-test", "conversation_url": "https://tavus.daily.co/c-test"}


def make_app(**kw):
    """App with all external calls stubbed (no network)."""
    kw.setdefault("conversation_creator", fake_creator)
    kw.setdefault("api_key", "")
    kw.setdefault("report_fetcher", lambda cid: None)
    kw.setdefault("conversation_ender", lambda cid: 200)
    return App(**kw)


class ConversationalContextTests(unittest.TestCase):
    def test_default_is_full_three_parts(self):
        ctx = tavus.build_conversational_context(None)
        self.assertIn("Part 1", ctx)
        self.assertIn("Part 2", ctx)
        self.assertIn("Part 3", ctx)
        self.assertIn("continuous", ctx)

    def test_single_part(self):
        ctx = tavus.build_conversational_context([2])
        self.assertIn("only Part 2", ctx)
        self.assertNotIn("Part 1", ctx)

    def test_multiple_parts_are_ordered_and_continuous(self):
        ctx = tavus.build_conversational_context([3, 1])
        self.assertLess(ctx.index("Part 1"), ctx.index("Part 3"))
        self.assertIn("ONE continuous test", ctx)

    def test_candidate_name_included(self):
        ctx = tavus.build_conversational_context([1], "Alex")
        self.assertIn("Alex", ctx)

    def test_part2_includes_pause_driven_prep_instruction(self):
        ctx = tavus.build_conversational_context([2])
        # Pause-driven, not a hard-coded countdown: the candidate begins when ready
        # and the examiner does not interrupt natural pauses.
        self.assertIn("begin speaking whenever they are ready", ctx)
        self.assertIn("do not interrupt natural pauses", ctx)

    def test_no_prep_note_when_part2_absent(self):
        ctx = tavus.build_conversational_context([1, 3])
        self.assertNotIn("begin speaking whenever they are ready", ctx)

    def test_invalid_part_raises(self):
        with self.assertRaises(ValueError):
            tavus.build_conversational_context([4])


class ConversationPayloadTests(unittest.TestCase):
    def test_defaults_use_live_ids(self):
        p = tavus.build_conversation_payload([1, 2, 3])
        self.assertEqual(p["pal_id"], tavus.DEFAULT_PAL_ID)
        self.assertEqual(p["face_id"], tavus.DEFAULT_FACE_ID)

    def test_has_max_call_duration(self):
        p = tavus.build_conversation_payload([2])
        self.assertEqual(p["properties"]["max_call_duration"], tavus.MAX_CALL_DURATION)
        self.assertLessEqual(p["properties"]["max_call_duration"], 3600)

    def test_no_silence_killing_timeout_present(self):
        # The 1-minute pause must be safe: only join/leave timeouts may exist,
        # and none of them end the call while a participant sits silent.
        props = tavus.build_conversation_payload([2])["properties"]
        allowed = {"max_call_duration", "participant_absent_timeout",
                   "participant_left_timeout", "enable_recording",
                   "enable_closed_captions", "language"}
        self.assertTrue(set(props).issubset(allowed),
                        f"unexpected property could end a pause: {set(props) - allowed}")
        # participant_absent_timeout only applies BEFORE anyone joins; once the
        # candidate is in, a silent minute cannot trip it.
        self.assertGreaterEqual(props["participant_absent_timeout"], 60)

    def test_callback_url_optional(self):
        self.assertNotIn("callback_url", tavus.build_conversation_payload([1]))
        p = tavus.build_conversation_payload([1], callback_url="https://x/score")
        self.assertEqual(p["callback_url"], "https://x/score")


class GreetingTests(unittest.TestCase):
    def test_part1_greeting_asks_name_and_frames_ielts(self):
        g = tavus.build_custom_greeting([1, 2, 3])
        self.assertIn("IELTS", g)
        self.assertIn("name", g.lower())

    def test_part2_only_greeting_mentions_part2(self):
        g = tavus.build_custom_greeting([2])
        self.assertIn("Part 2", g)
        self.assertIn("cue card", g.lower())

    def test_part3_only_greeting_mentions_discussion(self):
        g = tavus.build_custom_greeting([3])
        self.assertIn("Part 3", g)

    def test_payload_includes_greeting(self):
        p = tavus.build_conversation_payload([1, 2, 3], "Alex")
        self.assertIn("custom_greeting", p)
        self.assertIn("Alex", p["custom_greeting"])


class EventExtractionTests(unittest.TestCase):
    def test_extracts_report_from_string_body(self):
        events = [
            {"event_type": "application.transcription_ready", "properties": {}},
            {"event_type": "application.post_call_action_executed",
             "properties": {"tool_id": tavus.SCORE_TOOL_ID, "status": "error",
                            "request": {"body": json.dumps({"overall_band": 7})}}},
        ]
        report = tavus.extract_report_from_events(events)
        self.assertEqual(report["overall_band"], 7)

    def test_returns_none_when_action_absent(self):
        events = [{"event_type": "application.transcription_ready", "properties": {}}]
        self.assertIsNone(tavus.extract_report_from_events(events))

    def test_ignores_other_tools(self):
        events = [{"event_type": "application.post_call_action_executed",
                   "properties": {"tool_id": "some-other-tool",
                                  "request": {"body": "{\"x\":1}"}}}]
        self.assertIsNone(tavus.extract_report_from_events(events, tool_id=tavus.SCORE_TOOL_ID))


class EndTestTests(unittest.TestCase):
    def test_end_calls_ender(self):
        calls = []
        app = make_app(conversation_ender=lambda cid: calls.append(cid) or 200)
        status, out = app.handle_end_test("c-1")
        self.assertEqual(status, 200)
        self.assertEqual(calls, ["c-1"])

    def test_end_requires_id(self):
        status, out = make_app().handle_end_test(None)
        self.assertEqual(status, 400)

    def test_end_error_502(self):
        def boom(cid):
            raise tavus.TavusError("nope")
        status, out = make_app(conversation_ender=boom).handle_end_test("c-1")
        self.assertEqual(status, 502)


class ReportPollingTests(unittest.TestCase):
    def test_polls_tavus_when_not_stored(self):
        fetched = dict(SAMPLE_REPORT)
        app = make_app(report_fetcher=lambda cid: fetched)
        status, out = app.handle_report("c-9")
        self.assertEqual(out["status"], "ready")
        self.assertEqual(out["report"]["overall_band"], 6.5)
        # cached after first fetch
        self.assertIn("c-9", app.reports)

    def test_pending_when_fetcher_returns_none(self):
        app = make_app(report_fetcher=lambda cid: None)
        status, out = app.handle_report("c-9")
        self.assertEqual(out["status"], "pending")

    def test_pending_when_fetcher_errors(self):
        def boom(cid):
            raise tavus.TavusError("not ready")
        app = make_app(report_fetcher=boom)
        status, out = app.handle_report("c-9")
        self.assertEqual(out["status"], "pending")

    def test_stored_report_short_circuits_fetcher(self):
        def boom(cid):
            raise AssertionError("fetcher should not be called")
        app = make_app(report_fetcher=boom)
        app.handle_score({"conversation_id": "c-9", **SAMPLE_REPORT})
        status, out = app.handle_report("c-9")
        self.assertEqual(out["status"], "ready")


class StartTestHandlerTests(unittest.TestCase):
    def setUp(self):
        self.app = make_app()

    def test_returns_conversation_url(self):
        status, out = self.app.handle_start_test({"parts": [1, 2, 3]})
        self.assertEqual(status, 200)
        self.assertEqual(out["conversation_url"], "https://tavus.daily.co/c-test")
        self.assertEqual(out["parts"], [1, 2, 3])

    def test_invalid_parts_400(self):
        status, out = self.app.handle_start_test({"parts": [9]})
        self.assertEqual(status, 400)
        self.assertIn("error", out)

    def test_tavus_error_502(self):
        def boom(_payload):
            raise tavus.TavusError("nope")
        app = App(conversation_creator=boom, api_key="")
        status, out = app.handle_start_test({"parts": [1]})
        self.assertEqual(status, 502)

    def test_missing_url_502(self):
        app = App(conversation_creator=lambda p: {"conversation_id": "x"}, api_key="")
        status, out = app.handle_start_test({"parts": [1]})
        self.assertEqual(status, 502)


class ScoreAndReportTests(unittest.TestCase):
    def setUp(self):
        self.app = make_app()

    def test_store_and_retrieve(self):
        body = {"conversation_id": "abc", **SAMPLE_REPORT}
        status, out = self.app.handle_score(body)
        self.assertEqual(status, 200)
        status, out = self.app.handle_report("abc")
        self.assertEqual(status, 200)
        self.assertEqual(out["status"], "ready")
        self.assertEqual(out["report"]["overall_band"], 6.5)

    def test_pending_when_absent(self):
        status, out = self.app.handle_report("missing")
        self.assertEqual(out["status"], "pending")

    def test_latest_fallback(self):
        # Tavus may omit conversation_id; it stores under "latest".
        self.app.handle_score(dict(SAMPLE_REPORT))
        status, out = self.app.handle_report("some-unknown-id")
        self.assertEqual(out["status"], "ready")

    def test_empty_body_400(self):
        status, out = self.app.handle_score({"unrelated": "x"})
        self.assertEqual(status, 400)

    def test_numeric_coercion_and_field_filtering(self):
        report = normalize_report({"overall_band": "7.0", "fc_band": "6",
                                   "summary": "ok", "junk": "drop me"})
        self.assertEqual(report["overall_band"], 7.0)
        self.assertEqual(report["fc_band"], 6.0)
        self.assertNotIn("junk", report)

    def test_sample_report_has_all_fields(self):
        for f in REPORT_FIELDS:
            self.assertIn(f, SAMPLE_REPORT)


class HttpSmokeTest(unittest.TestCase):
    """Boots the real server (demo mode) and exercises it over HTTP."""
    @classmethod
    def setUpClass(cls):
        import server
        server.APP = make_app()
        server.DEMO_MODE = True
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def _post(self, path, obj):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(obj).encode(), method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())

    def _get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}") as r:
            return r.status, r.read()

    def test_full_flow_over_http(self):
        # 1. start-test
        status, out = self._post("/api/start-test", {"parts": [1, 2, 3]})
        self.assertEqual(status, 200)
        self.assertTrue(out["conversation_url"].startswith("https://"))
        cid = out["conversation_id"]

        # 2. report pending before scoring
        status, out = self._get(f"/api/report/{cid}")
        self.assertEqual(json.loads(out)["status"], "pending")

        # 2b. ending the call is accepted
        status, out = self._post("/api/end-test", {"conversation_id": cid})
        self.assertEqual(status, 200)
        self.assertEqual(out["status"], "ended")

        # 3. Tavus posts the band report
        status, out = self._post("/api/score", {"conversation_id": cid, **SAMPLE_REPORT})
        self.assertEqual(status, 200)

        # 4. report now ready
        status, out = self._get(f"/api/report/{cid}")
        body = json.loads(out)
        self.assertEqual(body["status"], "ready")
        self.assertEqual(body["report"]["overall_band"], 6.5)

    def test_static_index_served(self):
        status, body = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"IELTS", body)


if __name__ == "__main__":
    unittest.main()
