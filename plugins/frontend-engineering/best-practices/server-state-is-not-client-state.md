# Treat server state as a cache, not client state

Data fetched from an API is a cache of someone else's source of truth, not your application's state. Manage it with a server-cache library (TanStack Query, SWR, or RSC data) that gives you revalidation, deduplication, and loading/error states — never by copying it into a global client store, which is the single most common source of staleness and synchronization bugs in React apps.
