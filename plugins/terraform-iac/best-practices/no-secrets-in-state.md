# Keep secrets out of state — and encrypt it anyway

Terraform stores resource attributes — including many secrets — in state as plaintext. Mark variables/outputs sensitive and source secrets from a manager, but because providers still persist some values, treat the entire state file as sensitive: a remote, encrypted, access-restricted, versioned backend is mandatory.
