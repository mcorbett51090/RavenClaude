# Never export service-account key files

Exported SA JSON keys are long-lived credentials that end up on laptops, in CI variables, and in repos. Use Workload Identity Federation for external/CI workloads and Workload Identity for GKE pods so you attach an identity instead of downloading a secret, and disable SA key creation org-wide via org policy so the unsafe path is closed.
