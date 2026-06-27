"""Assessment-grade transcription (decoupled from the in-call CVI STT).

Why decoupled: the in-call STT (e.g. `tavus-soniox`) drives turn-taking, but the
`conversation.utterance` events it emits carry text only — not word-level timings
or confidence. Every fluency feature needs those. So for assessment we re-transcribe
the *isolated per-turn audio* with disfluencies KEPT, word timestamps, and confidence.

Soniox is a good fit: opt-in disfluency filtering (off by default keeps um/uh/false
starts), ms-level token timestamps, and 0-1 confidence. Whisper-family ASR normalises
fillers away and must NOT be used as the assessment STT.

`Transcriber` is the contract; populate `Turn.words` from whichever backend you run.
"""

from __future__ import annotations

from typing import Protocol, Any
from .schema import Word


class Transcriber(Protocol):
    def transcribe(self, audio_path: str) -> list[Word]: ...


class SonioxTranscriber:
    """Direct Soniox async transcription -> verbatim Words with timing + confidence.

    Keep disfluencies ON (do not enable the filter) so fillers survive for the
    fluency layer. Lazy HTTP so importing this module needs no extra deps.
    """

    def __init__(self, api_key: str, model: str = "stt-async-preview"):
        self.api_key = api_key
        self.model = model

    def transcribe(self, audio_path: str) -> list[Word]:
        # Implement against https://soniox.com/docs (upload -> transcribe -> poll).
        # Map each returned token -> Word(text, start_ms/1000, end_ms/1000, confidence),
        # WITHOUT enabling disfluency removal. Returns [] until wired.
        raise NotImplementedError(
            "Call Soniox async API (disfluencies kept) and map tokens to Word(...).")


def words_from_tavus_tokens(tokens: list[dict[str, Any]]) -> list[Word]:
    """If a Tavus STT/recording export ever exposes word tokens, adapt them here.

    Expected token shape: {text|word, start|start_ms, end|end_ms, confidence?}.
    """
    out: list[Word] = []
    for t in tokens:
        start = t.get("start", t.get("start_ms", 0))
        end = t.get("end", t.get("end_ms", 0))
        # normalise ms -> s if values look like milliseconds
        if start > 1000 or end > 1000:
            start, end = start / 1000.0, end / 1000.0
        out.append(Word(t.get("text", t.get("word", "")), float(start), float(end),
                        t.get("confidence")))
    return out
