# Rotate credentials on a schedule — don't wait for a compromise

**Status:** Absolute rule
**Domain:** Secrets management
**Applies to:** `security-engineering`

---

## Why this exists

A credential that has never been rotated has an unknown exposure window. If it was leaked silently (logs, a third-party breach, a misconfigured monitoring tool), you won't know until the attacker uses it. Short-lived credentials with automatic rotation reduce the window of opportunity to near zero. Even credentials you believe are safe should be rotated periodically — rotation is the hygiene that limits damage when your belief turns out to be wrong.

## How to apply

Use OIDC federation for cloud authentication (no stored secret at all). For credentials that must be stored, automate rotation via the secrets manager. Define a rotation policy in the vault configuration with a maximum age.

```hcl
# HashiCorp Vault: dynamic credentials with automatic rotation for a database
resource "vault_database_secret_backend_role" "app_role" {
  backend = vault_database_secrets_engine.db.path
  name    = "my-service"
  db_name = vault_database_secret_backend_connection.postgres.name

  creation_statements = [
    "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';",
    "GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO \"{{name}}\";",
  ]

  default_ttl = "1h"     # credentials expire in 1 hour
  max_ttl     = "24h"    # max lifetime before forced rotation
}
```

```yaml
# AWS Secrets Manager: automatic rotation schedule
resource "aws_secretsmanager_secret_rotation" "api_key_rotation" {
  secret_id           = aws_secretsmanager_secret.api_key.id
  rotation_lambda_arn = aws_lambda_function.rotate_secret.arn

  rotation_rules {
    automatically_after_days = 30   # rotate every 30 days
  }
}
```

Rotation policy by credential type:

| Credential type | Rotation cadence | Preferred approach |
|---|---|---|
| Cloud IAM (CI/CD) | N/A (use OIDC) | OIDC federation |
| Database credentials | Hourly/daily | Vault dynamic secrets |
| API keys (external) | 90 days max | Secrets manager + rotation lambda |
| SSH keys | 90 days max | CA-signed short-lived certs |
| TLS certificates | Automated via ACME | Let's Encrypt / cert-manager |

**Do:**
- Prefer OIDC federation or dynamic secrets (Vault) over stored credentials wherever supported.
- Set an expiry on every stored credential, enforced by the vault.
- Test rotation in a non-production environment before enabling in prod — rotation failures cause outages.

**Don't:**
- Rotate manually and call it a policy — automation is the only reliable policy.
- Set rotation intervals above 90 days for any human or service credential.
- Rotate credentials without first ensuring the new credential is deployed to the application (hot-swap pattern).

## Edge cases / when the rule does NOT apply

Long-lived test accounts in isolated dev environments with no access to production data can have longer rotation intervals, but must still have a policy and an expiry.

## See also

- [`../agents/appsec-engineer.md`](../agents/appsec-engineer.md) — owns the secrets management program and CI integration.
- [`./a-committed-secret-is-compromised.md`](./a-committed-secret-is-compromised.md) — if a credential was committed, rotation is the first step of remediation.

## Provenance

Codifies NIST SP 800-63B credential management guidance and HashiCorp Vault dynamic secrets documentation. The rotation policy table draws from CIS Controls v8, Control 4.

---

_Last reviewed: 2026-06-05 by `claude`_
