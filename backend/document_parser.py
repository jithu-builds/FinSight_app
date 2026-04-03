"""
Reducto PDF parser.

Uses the Reducto REST API directly via `requests` — no SDK required.

Correct API details:
  Base URL  : https://platform.reducto.ai
  Upload    : POST /upload  → { "file_id": "reducto://..." }
  Parse     : POST /parse   → { "result": { "chunks": [{ "content": "..." }] } }
  Auth      : Authorization: Bearer <REDUCTO_API_KEY>
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

REDUCTO_API_KEY: str = os.getenv("REDUCTO_API_KEY", "")
REDUCTO_BASE_URL = "https://platform.reducto.ai"


def parse_pdf_to_markdown(file_path: str) -> str:
    """
    Upload *file_path* to Reducto and return the full extracted Markdown string.

    Raises:
        EnvironmentError  – REDUCTO_API_KEY is not configured.
        FileNotFoundError – The file does not exist.
        RuntimeError      – Any Reducto API / network error.
    """
    if not REDUCTO_API_KEY:
        raise EnvironmentError(
            "REDUCTO_API_KEY is not set. Add it to your .env file."
        )
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"PDF not found at path: {file_path}")

    headers = {"Authorization": f"Bearer {REDUCTO_API_KEY}"}
    file_name = os.path.basename(file_path)

    # ── Step 1: Upload ────────────────────────────────────────────────────────
    try:
        with open(file_path, "rb") as pdf_file:
            upload_resp = requests.post(
                f"{REDUCTO_BASE_URL}/upload",
                headers=headers,
                files={"file": (file_name, pdf_file, "application/pdf")},
                timeout=60,
            )
        upload_resp.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Reducto upload failed [{exc.response.status_code}]: "
            f"{exc.response.text[:400]}"
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Reducto upload network error: {exc}") from exc

    upload_data = upload_resp.json()
    # Response: { "file_id": "reducto://..." }
    file_id: str = upload_data.get("file_id", "")
    if not file_id:
        raise RuntimeError(
            f"Reducto upload returned unexpected response: {upload_data}"
        )

    # ── Step 2: Parse ─────────────────────────────────────────────────────────
    try:
        parse_resp = requests.post(
            f"{REDUCTO_BASE_URL}/parse",
            headers={**headers, "Content-Type": "application/json"},
            json={"input": file_id},
            timeout=120,
        )
        parse_resp.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"Reducto parse failed [{exc.response.status_code}]: "
            f"{exc.response.text[:400]}"
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(f"Reducto parse network error: {exc}") from exc

    # ── Step 3: Extract markdown from chunks ─────────────────────────────────
    parse_data = parse_resp.json()
    chunks: list = parse_data.get("result", {}).get("chunks", [])

    if not chunks:
        raise RuntimeError(
            "Reducto returned no content chunks. "
            "Ensure the PDF contains selectable text (not a scanned image).\n"
            f"Raw response keys: {list(parse_data.keys())}"
        )

    # Join all chunk content into a single markdown document
    markdown_text = "\n\n".join(
        chunk.get("content", "") for chunk in chunks if chunk.get("content")
    ).strip()

    if not markdown_text:
        raise RuntimeError("Reducto parsed the document but all chunks were empty.")

    return markdown_text
