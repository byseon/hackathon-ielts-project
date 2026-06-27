import json

from assessment import Turn, Criterion
from assessment.features import extract_features
from assessment.judges import RubricJudge, build_user_prompt, NullRAG


class FakeLLM:
    """Returns a fixed JSON verdict; lets us test parsing without a network call."""

    def __init__(self, band=6.5):
        self.band = band
        self.last_user = ""

    def complete(self, system, user):
        self.last_user = user
        return json.dumps({
            "criterion": "x", "band": self.band, "confidence": 0.8,
            "evidence": [{"quote": "it was good", "observation": "basic word",
                          "feature": "flagged_basic_overuse=['good']"}],
            "feedback": [{"issue": "repetition", "suggestion": "vary vocabulary"}],
            "comparative_note": "closer to band 6 exemplar",
        })


def _turn():
    words = [{"text": "it", "start": 0.0, "end": 0.2, "confidence": 0.9},
             {"text": "was", "start": 0.2, "end": 0.4, "confidence": 0.9},
             {"text": "good", "start": 0.4, "end": 0.7, "confidence": 0.9}]
    return Turn.from_tavus(1, 1, words, clean_text="It was good.")


def test_build_user_prompt_includes_features_and_schema():
    feats = extract_features(_turn())
    p = build_user_prompt(Criterion.LEXICAL_RESOURCE, feats, "It was good.", NullRAG())
    assert "FEATURES:" in p and "TRANSCRIPT:" in p and "Return JSON" in p


def test_judge_parses_llm_json():
    feats = extract_features(_turn())
    judge = RubricJudge(FakeLLM(band=6.5))
    res = judge.judge(Criterion.LEXICAL_RESOURCE, feats, "It was good.")
    assert res.band == 6.5
    assert res.criterion == Criterion.LEXICAL_RESOURCE
    assert res.evidence and res.evidence[0].quote == "it was good"


def test_judge_all_runs_four_criteria():
    feats = extract_features(_turn())
    results = RubricJudge(FakeLLM()).judge_all(feats, "It was good.")
    assert set(results) == set(Criterion)
