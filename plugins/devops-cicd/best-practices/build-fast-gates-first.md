# Order CI gates cheapest-first

Run format/lint/typecheck (seconds) before unit (minutes) before integration/e2e (tens of minutes), and fail fast. A developer should learn about a formatting error in 15 seconds, not after a 20-minute integration run.
