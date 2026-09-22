"""Application configuration, loaded from environment variables."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Runtime configuration for the TaskFlow service."""

    db_path: str
    report_dir: str
    max_tasks_per_page: int = 25

    @classmethod
    def from_env(cls) -> "Config":
        """Build a Config from environment variables, with sane defaults."""
        return cls(
            db_path=os.environ.get("TASKFLOW_DB_PATH", "taskflow.db"),
            report_dir=os.environ.get("TASKFLOW_REPORT_DIR", "reports"),
            max_tasks_per_page=int(os.environ.get("TASKFLOW_PAGE_SIZE", "25")),
        )
