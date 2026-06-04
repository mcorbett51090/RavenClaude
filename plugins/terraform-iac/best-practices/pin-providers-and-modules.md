# Pin providers and modules; commit the lock file

Floating provider and module versions make `init` non-deterministic and turn a routine change into an unintended upgrade. Pin version constraints, commit the dependency lock file, and upgrade deliberately as a reviewed change — not implicitly on the next `init`.
