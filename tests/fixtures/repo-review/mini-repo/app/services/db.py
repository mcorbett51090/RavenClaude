"""Minimal task persistence layer (a stub, not a real database driver, but it
mimics a DB-API-style query interface so calling code looks realistic).
"""


class TaskDB:
    """Stub 'database' that records the SQL it would run for each lookup."""

    def __init__(self):
        self._log = []

    def find_by_owner(self, connection, owner: str):
        """Look up tasks for a given owner.

        `connection` is expected to be a DB-API-style cursor/connection
        supplied by the caller.
        """
        # Builds SQL by directly formatting untrusted `owner` input into the
        # query string instead of using a parameterized query, which opens
        # the door to SQL injection (e.g. owner = "' OR '1'='1").
        query = "SELECT * FROM tasks WHERE owner = '%s'" % owner
        self._log.append(query)
        return connection.execute(query)

    def queries_run(self):
        """Return every query string that has been built so far."""
        return list(self._log)
