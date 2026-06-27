"""Pronunciation features.

A transcript cannot score pronunciation — you need acoustics. Two pluggable
backends behind one `PronunciationAssessor` protocol:

  1. CharsiuGopAssessor  (MIT, local, recommended) — wav2vec2 forced alignment
     (lingjzhu/charsiu, Wav2Vec2-FC) gives frame-level phoneme posteriors, from
     which we compute Goodness-of-Pronunciation (GOP) per phoneme/word. Add an F0
     contour (parselmouth/CREPE) for intonation and aligned vowel duration/energy
     for word stress. Fully open, no vendor lock-in.
  2. ProxyPronunciationAssessor — zero-dependency fallback from STT word
     confidence + timing. Weak (flags likely problems, does not truly score) but
     always runs, so the pipeline is never blocked. `source="proxy"` warns the
     judge not to trust it.

GOP, briefly: align canonical phones to audio, then
  GOP(p) = (1/T) * sum_t [ log P(p | o_t) - log max_q P(q | o_t) ]
averaged over the frames t aligned to phone p. Near 0 = native-like; very
negative = likely mispronounced. (Witt & Young, 2000; modern wav2vec2 variant.)
"""

from __future__ import annotations

from typing import Protocol
from ..schema import Turn, PronunciationFeatures


class PronunciationAssessor(Protocol):
    def assess(self, turn: Turn) -> PronunciationFeatures: ...


# --------------------------------------------------------------------------- #
# Proxy — always available, zero deps                                          #
# --------------------------------------------------------------------------- #


class ProxyPronunciationAssessor:
    """Estimate pronunciation from STT confidence + timing. No audio model.

    Use only to *flag* likely problem spots. Set `source="proxy"` so judges
    down-weight it. Real scoring should use Charsiu GOP on the audio.
    """

    def assess(self, turn: Turn) -> PronunciationFeatures:
        feats = PronunciationFeatures(source="proxy")
        confs = [w.confidence for w in turn.words if w.confidence is not None]
        if confs:
            mean_conf = sum(confs) / len(confs)
            feats.accuracy_score = round(mean_conf * 100, 1)
            feats.intelligibility_estimate = round(mean_conf, 3)
            # words the STT was least sure about == candidate mispronunciations
            low = sorted(
                (w for w in turn.words if w.confidence is not None and w.confidence < 0.6),
                key=lambda w: w.confidence,
            )[:5]
            feats.low_accuracy_phonemes = [w.text for w in low]  # word-level proxy
        # crude fluency-of-speech proxy from phonation density
        if turn.words:
            total = max(1e-6, turn.words[-1].end - turn.words[0].start)
            phon = sum(w.duration for w in turn.words)
            feats.fluency_score = round(min(1.0, phon / total) * 100, 1)
        return feats


# --------------------------------------------------------------------------- #
# Charsiu GOP — MIT, local, recommended                                        #
# --------------------------------------------------------------------------- #


class CharsiuGopAssessor:
    """GOP scoring via Charsiu forced alignment (MIT, wav2vec2).

    Requires: pip install torch transformers + the charsiu repo (lingjzhu/charsiu)
    on PYTHONPATH. Heavy (model download) — kept lazy so importing this module
    never pulls torch. See module docstring for the GOP formula.
    """

    def __init__(self, model: str = "charsiu/en_w2v2_fc_10ms",
                 lang: str = "eng-us"):
        self.model = model
        self.lang = lang
        self._aligner = None

    def _ensure(self):
        if self._aligner is None:
            # Lazy import — only when actually scoring, never at module import.
            from Charsiu import charsiu_forced_aligner  # type: ignore
            self._aligner = charsiu_forced_aligner(aligner=self.model, lang=self.lang)
        return self._aligner

    def assess(self, turn: Turn) -> PronunciationFeatures:
        if not turn.audio_path:
            raise ValueError("CharsiuGopAssessor needs turn.audio_path (per-turn wav)")
        aligner = self._ensure()  # noqa: F841 — used once wired
        feats = PronunciationFeatures(source="gop")
        # Pipeline (depends on charsiu version):
        #   1. G2P the reference (turn.clean_text) -> canonical phones
        #   2. aligner.align(audio, text) -> phone segments + frame posteriors
        #   3. for each phone p over its frames: gop_p = mean(logP(p) - logP(argmax))
        #   4. word_score = mean(gop over its phones); accuracy_score = scaled mean
        #   5. word stress: aligned vowel duration/energy vs expected pattern
        #   6. intonation: F0 contour slope/range over the utterance
        # The installed model produces the numbers; this adapter standardises them
        # into PronunciationFeatures for the judge.
        raise NotImplementedError(
            "Wire charsiu align() + posterior extraction here; returns gop-based "
            "accuracy/word_stress/intonation. Use ProxyPronunciationAssessor until then."
        )


def default_assessor() -> PronunciationAssessor:
    """Use Charsiu GOP if torch is installed, else the zero-dep proxy."""
    try:
        import torch  # noqa: F401
        return CharsiuGopAssessor()
    except Exception:
        return ProxyPronunciationAssessor()
