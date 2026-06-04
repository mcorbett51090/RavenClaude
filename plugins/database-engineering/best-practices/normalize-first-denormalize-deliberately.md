# Normalize first; denormalize only with evidence

Design to 3NF so each fact lives in one place and integrity is structural. Denormalize only when a measured read hot-path justifies it and you explicitly accept the write-amplification and consistency-maintenance cost — and prefer a materialized view or covering index over redundant columns. Premature denormalization is a consistency bug you scheduled for later.
