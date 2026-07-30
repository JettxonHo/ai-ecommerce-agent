"""VIOLATION: application loads .env and reads environment variables."""

import os

from dotenv import load_dotenv


def read_timeout() -> str:
    """Both dotenv loading and getenv are forbidden in core layers."""
    load_dotenv()
    return os.getenv("BRIEF_TIMEOUT", "30")
