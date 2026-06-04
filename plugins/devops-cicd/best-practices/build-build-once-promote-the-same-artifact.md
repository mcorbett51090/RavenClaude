# Build once, promote the same artifact

The exact bytes tested in staging must be the bytes that reach production, identified by **digest**. Rebuilding per-environment reintroduces nondeterminism and is why "it worked in staging" lies. Build in CI, store in the registry, and promote that digest through environments.
