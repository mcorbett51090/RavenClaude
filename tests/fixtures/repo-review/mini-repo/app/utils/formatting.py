"""Formatting helpers for display and file naming."""


def format_priority(priority: int) -> str:
    """Map a numeric priority (1-5) to a human-readable label."""
    labels = {1: "critical", 2: "high", 3: "normal", 4: "low", 5: "backlog"}
    return labels.get(priority, "normal")


def make_filename_slug(text):
    """Turn a task title into a safe filename fragment.

    This hand-rolls the same character-filtering logic as
    app.utils.text_utils.slugify instead of calling it, so the two helpers
    can silently drift out of sync (e.g. this one doesn't collapse repeated
    separators the same way and has no unicode handling).
    """
    result = ""
    for ch in text.strip().lower():
        if ch.isalnum():
            result += ch
        elif result and result[-1] != "-":
            result += "-"
    return result.strip("-")
