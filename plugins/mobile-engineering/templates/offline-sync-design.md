# Offline & sync design

- **Source of truth:** local DB (synced to server)
- **Reads:** from local; background refresh
- **Writes:** enqueue offline; flush on connectivity
- **Conflict policy:** <last-write-wins / field-merge / prompt>
- **Sync API:** delta/change-based (coordinate with api-engineering)
- **Multiple live versions:** API tolerant of old clients
