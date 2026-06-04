# Remote state backend (pattern — fill per cloud)

- Remote backend (S3+lock / GCS / azurerm / TFC)
- **Locking** enabled (non-negotiable)
- **Encryption** at rest
- **Versioning** for recovery
- Access **restricted** (it contains secrets)
- **One state per blast-radius/environment** (no monolith)

_Resource-specific backend config -> the cloud plugin._
