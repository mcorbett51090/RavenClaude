# Separate accounts by blast radius

Put prod, non-prod, security/log-archive, and shared-services in separate accounts under Organizations. A single account means one blast radius for a mistake, no clean billing attribution, and IAM that has to distinguish environments by convention. Account boundaries are the strongest isolation AWS offers — use them.
