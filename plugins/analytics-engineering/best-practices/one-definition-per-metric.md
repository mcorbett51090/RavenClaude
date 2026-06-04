# Define each metric exactly once

Revenue, active user, churn, and every other business metric must have a single governed definition in the semantic/metrics layer, consumed by every dashboard and tool. The moment two reports compute the 'same' metric differently, the business loses trust in all of them and burns hours reconciling. Metric drift is the silent killer of analytics credibility; metrics-as-code with explicit grain and filters is the cure.
