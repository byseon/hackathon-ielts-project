"""Central config from environment variables (see .env.example).

Tavus-centric: one TAVUS_API_KEY covers STT, TTS, the hosted LLM, and the
Knowledge Base (RAG). The judge LLM is OpenAI-compatible and falls back to the
Tavus key so you don't need a second provider.

Reads os.environ; if python-dotenv is installed it also loads a local .env.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:  # optional convenience: auto-load .env if python-dotenv is present
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # pragma: no cover
    pass


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Config:
    # Tavus CVI (conversation + STT + Knowledge Base)
    tavus_api_key: str = _get("TAVUS_API_KEY")
    tavus_pal_id: str = _get("TAVUS_PAL_ID")
    tavus_face_id: str = _get("TAVUS_FACE_ID")
    tavus_stt_engine: str = _get("TAVUS_STT_ENGINE", "tavus-soniox")
    tavus_document_tags: tuple[str, ...] = tuple(
        t.strip() for t in _get("TAVUS_DOCUMENT_TAGS").split(",") if t.strip())

    # Off-call judge LLM (OpenAI-compatible; defaults to Tavus's hosted LLM)
    llm_base_url: str = _get("LLM_BASE_URL")
    _llm_api_key: str = _get("LLM_API_KEY")
    llm_model: str = _get("LLM_MODEL", "llama-3.3-70b")

    # Pronunciation + word-timing backbone (local)
    charsiu_model: str = _get("CHARSIU_MODEL", "charsiu/en_w2v2_fc_10ms")

    # Demo
    port: int = int(_get("PORT", "8000"))

    @property
    def llm_api_key(self) -> str:
        """Fall back to the Tavus key so one credential serves both."""
        return self._llm_api_key or self.tavus_api_key

    def require(self, *names: str) -> None:
        """Raise if any named field is empty — call at the edge that needs them."""
        missing = [n for n in names if not getattr(self, n)]
        if missing:
            raise RuntimeError(
                f"Missing config: {', '.join(missing)}. Copy .env.example -> .env "
                f"and fill them in.")


config = Config()
