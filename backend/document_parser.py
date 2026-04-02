"""
Reducto PDF parser.

Uploads a local PDF to the Reducto API and returns the extracted
Markdown text, which is then passed to the AI engine for transaction
extraction.

Reducto SDK response structure (for reference):
  upload_resp.upload_id           → str
  parse_resp.result.markdown      → str  (full document markdown)
  parse_resp.result.chunks        → list (page-level chunks, optional use)
"""

import os

from dotenv import load_dotenv

load_dotenv()

REDUCTO_API_KEY: str = os.getenv("REDUCTO_API_KEY", "")


def parse_pdf_to_markdown(file_path: str) -> str:
    """
    Upload *file_path* to Reducto, parse it, and return the full
    extracted Markdown string.

    Raises:
        EnvironmentError  – REDUCTO_API_KEY is not configured.
        FileNotFoundError – The file does not exist.
        RuntimeError      – Any Reducto API or network error.
    """
    if not REDUCTO_API_KEY:
        raise EnvironmentError(
            "REDUCTO_API_KEY is not set. Add it to your .env file."
        )

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"PDF not found at path: {file_path}")

    # Import here so a missing SDK surfaces a clear message.
    try:
        from reducto import Reducto  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "The 'reducto' package is not installed. Run: pip install reducto"
        ) from exc

    client = Reducto(api_key=REDUCTO_API_KEY)
    file_name = os.path.basename(file_path)

    # ── Step 1: Upload the PDF ────────────────────────────────────────────────
    try:
        with open(file_path, "rb") as pdf_file:
            upload_resp = client.upload.upload(
                file=(file_name, pdf_file, "application/pdf")
            )
    except Exception as exc:
        raise RuntimeError(f"Reducto upload failed: {exc}") from exc

    upload_id: str = upload_resp.upload_id
    if not upload_id:
        raise RuntimeError("Reducto returned an empty upload_id.")

    # ── Step 2: Parse the uploaded document ──────────────────────────────────
    try:
        parse_resp = client.parse.parse_url(
            document_url=f"reducto://{upload_id}"
        )
    except Exception as exc:
        raise RuntimeError(f"Reducto parse failed: {exc}") from exc

    # ── Step 3: Extract Markdown text ────────────────────────────────────────
    try:
        markdown_text: str = parse_resp.result.markdown
    except AttributeError as exc:
        raise RuntimeError(
            "Unexpected Reducto response structure. "
            f"Could not access .result.markdown — raw response: {parse_resp}"
        ) from exc

    if not markdown_text or not markdown_text.strip():
        raise RuntimeError(
            "Reducto returned an empty document. "
            "Ensure the PDF contains selectable text (not a scanned image)."
        )

    return markdown_text
