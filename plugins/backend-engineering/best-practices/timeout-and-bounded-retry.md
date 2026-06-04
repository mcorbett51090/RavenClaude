# Timeout every call; retry idempotent-only with backoff+jitter

Every outbound network call needs a timeout sized to the dependency, or one slow dependency exhausts the thread/connection pool and cascades into total failure. Retries must be bounded, use exponential backoff with jitter (to avoid synchronized retry storms), and apply only to idempotent operations. Pair with circuit breakers so a failing dependency makes you fail fast rather than pile up.
