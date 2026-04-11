"""
Google Gemini AI engine — gemini-2.5-flash (google.genai SDK)
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime, date

import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- Explicitly load .env for AWS environments ---
def _load_env_on_aws():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(base_dir, '.env')
    load_dotenv(env_path, override=True)

_load_env_on_aws()

def _secret(key: str) -> str:
    """Read from st.secrets (Streamlit Cloud) or fall back to os.getenv."""
    try:
        return st.secrets.get(key) or os.getenv(key, "")
    except Exception:
        return os.getenv(key, "")

GEMINI_API_KEY: str = _secret("GEMINI_API_KEY")
_MODEL_NAME = "gemini-2.5-flash"

VALID_CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Entertainment",
    "Utilities", "Rent & Housing", "Healthcare", "Income",
    "Transfer", "Subscriptions", "Other",
]

@st.cache_resource
def _get_client():
    """Persistent client instance for Streamlit sessions."""
    if not GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY is not set. Check your .env file.")
    return genai.Client(api_key=GEMINI_API_KEY)

def _generate(prompt: str, temperature: float = 0.3) -> str:
    client = _get_client()
    response = client.models.generate_content(
        model=_MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    return response.text

def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^
http://googleusercontent.com/immersive_entry_chip/0
4.  **Wait 30 seconds**: Give the API a clean start. 

If you still see the **503 error**, simply wait one minute; the `@st.cache_resource` fix ensures your next successful call will "stick" and you won't have to keep fighting the server.