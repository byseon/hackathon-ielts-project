"""Configure the Tavus Examiner PAL + Knowledge Base from the CLI.

    uv run python scripts/setup_tavus.py faces            # list face ids (for the random pool)
    uv run python scripts/setup_tavus.py upload docs/knowledge/rubric.pdf --tags ielts-rubric
    uv run python scripts/setup_tavus.py pal --pal pece42dab07f --prompt prompts/examiner-pal-system-prompt.md

Reads TAVUS_API_KEY from .env (see .env.example). DRY-RUN by default — prints the
request it would send; pass --execute to actually call the API. Stdlib only.

NOTE: Tavus API request bodies evolve; fields marked VERIFY against current docs
(https://docs.tavus.io/api-reference/overview). The UI (your PAL editor) can do all
of this too — this script just automates the tedious parts (bulk doc upload, faces).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from assessment.config import config  # noqa: E402

BASE = "https://tavusapi.com/v2"


def _call(method: str, path: str, body: dict | None, execute: bool) -> dict | None:
    url = f"{BASE}{path}"
    if not execute:
        print(f"[dry-run] {method} {url}")
        if body is not None:
            print(json.dumps(body, indent=2)[:2000])
        print("  (pass --execute to send)\n")
        return None
    config.require("tavus_api_key")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Content-Type": "application/json", "x-api-key": config.tavus_api_key})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read() or b"{}")


def cmd_faces(args) -> None:
    """List available faces so you can build the random-examiner pool."""
    out = _call("GET", "/faces", None, args.execute)
    if out:
        faces = out.get("data", out if isinstance(out, list) else [])
        for f in faces:
            print(f"{f.get('face_id', f.get('replica_id', '?'))}  {f.get('face_name', f.get('replica_name', ''))}")


def cmd_upload(args) -> None:
    """Upload a Knowledge Base document under one or more tags (RAG)."""
    path = Path(args.file)
    # VERIFY: Tavus may accept a document_url instead of/in addition to file upload.
    body = {
        "document_name": path.name,
        "tags": args.tags,
        # "document_url": "https://...",  # if hosting the file; else use multipart upload
    }
    print(f"Uploading {path} with tags={args.tags}")
    out = _call("POST", "/documents", body, args.execute)
    if out:
        print("document_id:", out.get("document_id"))


def _first_code_block(text: str) -> str:
    """Extract the first ```fenced``` block (the Base system prompt) from markdown."""
    parts = text.split("```")
    if len(parts) >= 3:
        block = parts[1]
        # drop an optional language tag on the opening fence line
        return block.split("\n", 1)[1] if "\n" in block else block
    return text


def cmd_pal(args) -> None:
    """Patch the Examiner PAL with the system prompt + STT engine."""
    raw = Path(args.prompt).read_text() if args.prompt else ""
    # If given the markdown doc, send only the Base system prompt code block.
    prompt = _first_code_block(raw) if args.prompt and args.prompt.endswith(".md") else raw
    body = {  # VERIFY field names against the current /v2/pals schema
        "system_prompt": prompt,
        "layers": {"stt": {"stt_engine": config.tavus_stt_engine}},
    }
    if args.greeting:
        body["custom_greeting"] = args.greeting
    _call("PATCH", f"/pals/{args.pal}", body, args.execute)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--execute", action="store_true", help="actually call the API")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("faces").set_defaults(func=cmd_faces)

    up = sub.add_parser("upload")
    up.add_argument("file")
    up.add_argument("--tags", nargs="+", default=["ielts-rubric"])
    up.set_defaults(func=cmd_upload)

    pal = sub.add_parser("pal")
    pal.add_argument("--pal", default=config.tavus_pal_id, help="PAL id (e.g. pece42dab07f)")
    pal.add_argument("--prompt", help="path to the system-prompt file")
    pal.add_argument("--greeting", help="custom greeting text")
    pal.set_defaults(func=cmd_pal)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
