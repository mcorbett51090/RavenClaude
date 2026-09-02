"""Small text helpers shared across the app."""
import re


def slugify(text: str) -> str:
    """Convert arbitrary text into a URL/filename-safe slug.

    This is the canonical slug implementation for the app; other modules
    should call this instead of reimplementing the same logic.
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def truncate(text: str, max_len: int = 80) -> str:
    """Truncate text to max_len characters, appending an ellipsis if cut."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"
