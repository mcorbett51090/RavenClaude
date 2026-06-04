# Separate deploy from release

Deploying code and releasing a feature are different events. Ship behind a feature flag (deploy dark), then flip the flag to release. A bad release becomes a flag flip instead of a redeploy + rollback.
