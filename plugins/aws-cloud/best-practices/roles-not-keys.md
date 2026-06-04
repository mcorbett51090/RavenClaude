# Prefer roles and federation over long-lived keys

Use IAM roles with short-lived credentials — instance/task roles, IRSA/Pod Identity for EKS, OIDC federation for CI, Identity Center for humans. Long-lived access keys are the most common AWS breach vector: they leak via logs, forks, and laptops and are rarely rotated. There is almost never a good reason to mint one.
