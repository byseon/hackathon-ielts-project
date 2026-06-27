"""Central config from environment variables (see .env.example).

Reads os.environ; if python-dotenv is installed it also loads a local .env. No
secret ever lives in code — only names live here, so the rest of the codebase
asks `config.tavus_api_key` instead of reaching into os.environ everywhere.
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
    # Tavus CVI
    tavus_api_key: str = _get("TAVUS_API_KEY")
    tavus_pal_id: str = _get("TAVUS_PAL_ID")
    tavus_face_id: str = _get("TAVUS_FACE_ID")
    tavus_stt_engine: str = _get("TAVUS_STT_ENGINE", "tavus-soniox")
    # Assessment STT
    soniox_api_key: str = _get("SONIOX_API_KEY")
    # LLM judges
    anthropic_api_key: str = _get("ANTHROPIC_API_KEY")
    judge_model: str = _get("JUDGE_MODEL", "claude-haiku-4-5-20251001")
    # Pronunciation
    charsiu_model: str = _get("CHARSIU_MODEL", "charsiu/en_w2v2_fc_10ms")
    # RAG
    database_url: str = _get("DATABASE_URL")
    # Demo
    port: int = int(_get("PORT", "8000"))

    def require(self, *names: str) -> None:
        """Raise if any named field is empty — call at the edge that needs them."""
        missing = [n for n in names if not getattr(self, n)]
        if missing:
            raise RuntimeError(
                f"Missing config: {', '.join(missing)}. Copy .env.example -> .env "
                f"and fill them in.")


config = Config()
