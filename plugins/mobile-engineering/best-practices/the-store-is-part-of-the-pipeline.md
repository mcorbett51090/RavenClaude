# Treat the app store as part of the pipeline

Code signing, provisioning, review guidelines, phased rollout, and the reality that users do not update instantly are engineering concerns, not afterthoughts. Design the app and its API to tolerate multiple live client versions simultaneously, automate signing and submission in CI/CD, and plan for review latency. An app that breaks when the backend changes because old clients are still live is a versioning failure.
