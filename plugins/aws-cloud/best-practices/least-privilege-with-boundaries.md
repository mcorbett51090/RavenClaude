# Least privilege, capped by boundaries and SCPs

Grant the minimum actions on the minimum resource ARNs, then use IAM Access Analyzer and last-used data to remove what's unused. Layer permission boundaries (per-role ceiling) and SCPs (org-wide ceiling) so even a mis-scoped policy can't exceed the cap. A `*` action or resource is a finding, not a default.
