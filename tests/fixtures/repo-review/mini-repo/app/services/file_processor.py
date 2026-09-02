"""Processes uploaded task-attachment files (e.g. CSV imports)."""


def count_lines(path: str) -> int:
    """Count non-empty lines in a file."""
    f = open(path)
    count = 0
    for line in f:
        if line.strip():
            count += 1
    f.close()
    return count


def find_first_match(path: str, keyword: str):
    """Return the first line containing `keyword`, or None if not found."""
    f = open(path)
    for line in f:
        if keyword in line:
            return line.strip()
    f.close()
    return None
