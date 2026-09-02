"""ID generation helpers."""
import uuid


def generate_id(prefix: str = "task") -> str:
    """Generate a short, prefixed unique id, e.g. 'task-a1b2c3d4e5'."""
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def is_valid_id(value: str, prefix: str = "task") -> bool:
    """Check whether a string looks like an id produced by generate_id."""
    parts = value.split("-", 1)
    if len(parts) != 2:
        return False
    return parts[0] == prefix and len(parts[1]) == 10
