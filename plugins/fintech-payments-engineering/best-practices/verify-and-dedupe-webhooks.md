# Verify and idempotently handle every webhook

Payment webhooks arrive at a public endpoint, at-least-once, and out of order, so verify the provider's signature before trusting any payload and dedupe by event id with idempotent handlers. An unverified webhook is a spoofable instruction to credit an account or mark an invoice paid, and a non-idempotent handler double-applies on the inevitable redelivery. Drive your payment state machine from verified webhooks, not from the synchronous response alone.
