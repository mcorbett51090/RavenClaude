# Control metric cardinality

Never put unbounded-value identifiers (user-id, request-id, full URL with ids) on metric labels — each combination is a new time series and the cost is multiplicative. Put high-cardinality data on traces and logs, which are built to search it. Uncontrolled cardinality is how monitoring itself goes down.
