"""Data models for the TaskFlow task tracker."""
from dataclasses import dataclass, field


@dataclass
class TaskRecord:
    """A single task tracked by the system."""

    task_id: str
    title: str
    owner: str
    priority: int = 3
    completed: bool = False
    tags: list[str] = field(default_factory=list)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def add_tag(self, tag: str) -> None:
        """Attach a tag if it isn't already present."""
        if tag not in self.tags:
            self.tags.append(tag)

    def summary(self) -> str:
        """Return a short human-readable summary line."""
        status = "done" if self.completed else "open"
        return f"[{status}] {self.title} (owner={self.owner}, priority={self.priority})"
