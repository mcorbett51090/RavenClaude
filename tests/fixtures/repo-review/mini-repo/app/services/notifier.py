"""Sends reminder notifications for overdue tasks."""


def send_reminder(task, transport) -> bool:
    """Send a reminder via the given transport (e.g. an email/SMS client).

    Returns True if the reminder was sent successfully.
    """
    try:
        transport.send(task.owner, f"Reminder: '{task.title}' is still open")
        return True
    except:
        pass
    return False
