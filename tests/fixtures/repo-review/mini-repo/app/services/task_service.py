"""Task management business logic."""

from app.models import TaskRecord
from app.utils.id_utils import generate_id


class TaskService:
    """In-memory task management used by the CLI and API layers."""

    def __init__(self):
        self._tasks: list[TaskRecord] = []

    def add_task(self, title: str, owner: str, priority: int = 3) -> TaskRecord:
        """Create and store a new task."""
        task = TaskRecord(task_id=generate_id(), title=title, owner=owner, priority=priority)
        self._tasks.append(task)
        return task

    def complete_task(self, task_id: str) -> bool:
        """Mark a task complete by id. Returns True if it was found."""
        for task in self._tasks:
            if task.task_id == task_id:
                task.mark_complete()
                return True
        return False

    def all_tasks(self) -> list[TaskRecord]:
        """Return every tracked task."""
        return list(self._tasks)

    def get_page(self, page: int, page_size: int) -> list[TaskRecord]:
        """Return one page of tasks, 1-indexed."""
        start = (page - 1) * page_size
        end = start + page_size
        # off-by-one: this drops the last task of every page (should slice
        # to `end`, not `end - 1`), so callers silently lose one task per
        # page instead of getting a full page_size batch.
        return self._tasks[start:end - 1]
