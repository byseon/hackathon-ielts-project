"""Layer B — LLM rubric judges (one per IELTS criterion).

Each judge receives the transcript span + the Layer-A features for its criterion +
retrieved band descriptors and exemplars (RAG), and returns a structured JudgeResult
with an evidence-cited band. The full prompts live in
`prompts/assessor-rubric-judges.md`; condensed instruction stubs are here.

LLM-agnostic: pass any object implementing `LLMClient.complete(system, user) -> str`.
Import-safe (no anthropic import at module load). Use a low-hallucination model at
low temperature (e.g. Claude Haiku/Sonnet).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Protocol, Optional

from ..schema import (TurnFeatures, Criterion, JudgeResult, Evidence, FeedbackItem)


class LLMClient(Protocol):
    def complete(self, system: str, user: str) -> str: ...


class RAGStore(Protocol):
    def descriptors(self, criterion: Criterion) -> str: ...
    def exemplars(self, criterion: Criterion, transcript: str, band_hint: float) -> str: ...


class NullRAG:
    """No-op store so judges run before the exemplar corpus exists."""

    def descriptors(self, criterion: Criterion) -> str:
        return "(band descriptors not loaded)"

    def exemplars(self, criterion: Criterion, transcript: str, band_hint: float) -> str:
        return "(no exemplars loaded)"


# Condensed per-criterion instructions (full text in prompts/assessor-rubric-judges.md).
JUDGE_INSTRUCTIONS = {
    Criterion.FLUENCY_COHERENCE:
        "Assess Fluency & Coherence: speech rate, continuity (false starts, "
        "repetition, word-search pauses), logical sequencing, and cohesive devices. "
        "Natural discourse-marking fillers are fine; penalise breakdown only.",
    Criterion.LEXICAL_RESOURCE:
        "Assess Lexical Resource: variety, appropriacy (referential meaning, style, "
        "collocation, attitude), and the ability to paraphrase. Reward paraphrase; "
        "penalise repetition of basic words and register/collocation errors.",
    Criterion.GRAMMATICAL_RANGE_ACCURACY:
        "Assess Grammatical Range & Accuracy: sentence length, subordination, verb-"
        "phrase and phrase complexity, structure variety (range) vs error density and "
        "error gravity (accuracy). Balance the two; list concrete corrections.",
    Criterion.PRONUNCIATION:
        "Assess Pronunciation from the pronunciation-model outputs (not spelling): "
        "chunking, rhythm/stress/linking, intonation, phoneme/word-stress accuracy, "
        "and overall intelligibility. Accent itself is not penalised.",
}

SYSTEM = (
    "You are a calibrated IELTS Speaking examiner judging ONE criterion. Score in "
    "half-bands (0-9). You MUST cite evidence (a quote or a feature) for the band; "
    "anchor by comparison to the provided exemplars. Reserve 8-9 for near-native "
    "performance. Respond ONLY with a JSON object matching the given schema."
)

SCHEMA_HINT = (
    '{"criterion": "...", "band": 6.5, "confidence": 0.0, '
    '"evidence": [{"quote": "...", "observation": "...", "feature": "..."}], '
    '"feedback": [{"issue": "...", "example_from_candidate": "...", '
    '"suggestion": "...", "upgraded_example": "..."}], "comparative_note": "..."}'
)


def build_user_prompt(criterion: Criterion, feats: TurnFeatures, transcript: str,
                      rag: RAGStore, band_hint: float = 6.0) -> str:
    crit_feats = {
        Criterion.FLUENCY_COHERENCE: feats.fluency,
        Criterion.LEXICAL_RESOURCE: feats.lexical,
        Criterion.GRAMMATICAL_RANGE_ACCURACY: feats.grammar,
        Criterion.PRONUNCIATION: feats.pronunciation,
    }[criterion]
    return (
        f"{JUDGE_INSTRUCTIONS[criterion]}\n\n"
        f"FEATURES:\n{json.dumps(asdict(crit_feats), indent=2)}\n\n"
        f"TRANSCRIPT:\n{transcript}\n\n"
        f"BAND DESCRIPTORS:\n{rag.descriptors(criterion)}\n\n"
        f"EXEMPLARS near candidate band:\n{rag.exemplars(criterion, transcript, band_hint)}\n\n"
        f"Return JSON exactly like: {SCHEMA_HINT}"
    )


def _parse(criterion: Criterion, text: str) -> JudgeResult:
    """Tolerant JSON extraction -> JudgeResult."""
    start, end = text.find("{"), text.rfind("}")
    data = json.loads(text[start:end + 1]) if start >= 0 else {}
    return JudgeResult(
        criterion=criterion,
        band=float(data.get("band", 0.0)),
        confidence=float(data.get("confidence", 0.0)),
        evidence=[Evidence(e.get("quote", ""), e.get("observation", ""),
                           e.get("feature", "")) for e in data.get("evidence", [])],
        feedback=[FeedbackItem(f.get("issue", ""), f.get("example_from_candidate", ""),
                               f.get("suggestion", ""), f.get("upgraded_example", ""))
                  for f in data.get("feedback", [])],
        comparative_note=data.get("comparative_note", ""),
    )


class RubricJudge:
    def __init__(self, llm: LLMClient, rag: Optional[RAGStore] = None):
        self.llm = llm
        self.rag = rag or NullRAG()

    def judge(self, criterion: Criterion, feats: TurnFeatures, transcript: str,
              band_hint: float = 6.0) -> JudgeResult:
        user = build_user_prompt(criterion, feats, transcript, self.rag, band_hint)
        return _parse(criterion, self.llm.complete(SYSTEM, user))

    def judge_all(self, feats: TurnFeatures, transcript: str,
                  band_hint: float = 6.0) -> dict[Criterion, JudgeResult]:
        return {c: self.judge(c, feats, transcript, band_hint) for c in Criterion}


class AnthropicClient:
    """LLMClient backed by Claude. Lazy import; needs ANTHROPIC_API_KEY."""

    def __init__(self, model: str = "claude-haiku-4-5-20251001", temperature: float = 0.2):
        self.model, self.temperature = model, temperature

    def complete(self, system: str, user: str) -> str:
        import anthropic  # lazy
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=self.model, max_tokens=1024, temperature=self.temperature,
            system=system, messages=[{"role": "user", "content": user}])
        return msg.content[0].text


__all__ = ["LLMClient", "RAGStore", "NullRAG", "RubricJudge", "AnthropicClient",
           "build_user_prompt", "JUDGE_INSTRUCTIONS"]
