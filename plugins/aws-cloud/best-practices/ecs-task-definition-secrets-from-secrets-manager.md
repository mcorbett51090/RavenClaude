# Pull ECS task secrets from Secrets Manager, not environment variables

**Status:** Absolute rule
**Domain:** AWS ECS / secrets management
**Applies to:** `aws-cloud`

---

## Why this exists

Hard-coding secrets as literal environment variables in an ECS task definition embeds them in the task definition JSON, CloudFormation/Terraform state, and the ECS console — readable by anyone with `ecs:DescribeTaskDefinition`. They also cannot be rotated without a new task definition revision. Secrets Manager (or Parameter Store SecureString) keeps the secret value out of the definition and rotates it independently. The task retrieves the current value at launch time via the `secrets` block, which references only the ARN.

## How to apply

Use the `secrets` block in the task definition container definition — not `environment` — for any sensitive value.

```json
{
  "containerDefinitions": [
    {
      "name": "app",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/app:1.2.3",
      "environment": [
        { "name": "APP_ENV", "value": "prod" }
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:app/db-password-abc123"
        },
        {
          "name": "API_KEY",
          "valueFrom": "arn:aws:ssm:us-east-1:123456789012:parameter/app/prod/api-key"
        }
      ]
    }
  ]
}
```

The task execution role must have:
```json
{
  "Effect": "Allow",
  "Action": [
    "secretsmanager:GetSecretValue",
    "kms:Decrypt"
  ],
  "Resource": [
    "arn:aws:secretsmanager:us-east-1:123456789012:secret:app/*"
  ]
}
```

**Do:**
- Reference secrets by ARN (not by name) for deterministic resolution.
- Grant the task execution role the minimum `secretsmanager:GetSecretValue` + `kms:Decrypt` scoped to specific secret ARNs.
- Enable automatic rotation in Secrets Manager for credentials that support it.
- Store all secret values in Secrets Manager or Parameter Store SecureString before writing the task definition.

**Don't:**
- Pass secret values as `environment` literals in the task definition.
- Use the same secret ARN across environments — namespace secrets per environment (`app/prod/db-password`, `app/dev/db-password`).
- Embed the secret value in the Terraform `aws_secretsmanager_secret_version` resource — write the value out-of-band via the console or a one-time script.

## Edge cases / when the rule does NOT apply

- **Non-sensitive config** (log level, feature flags, AWS region): plain `environment` is fine.
- **Lambda functions**: use `AWS_LAMBDA_FUNCTION_*` env vars for non-sensitive config; for secrets, use the same Secrets Manager approach via the function's execution role and a direct API call or the Lambda Powertools `SecretsProvider`.

## See also

- [`../agents/aws-iam-identity-engineer.md`](../agents/aws-iam-identity-engineer.md) — owns the execution role policy scoping.
- [`./roles-not-keys.md`](./roles-not-keys.md) — the parent rule: prefer roles; this rule covers the remaining secrets that must exist.

## Provenance

Codifies a concrete application of the `aws-cloud` house opinion #1 ("Roles, not keys") and #4 ("Private by default") to ECS workloads. AWS ECS documentation on sensitive data in containers (`amazon-ecs-agent/docs/secrets.md`). Standard secret-hygiene guidance in the AWS Security Best Practices whitepaper.

---

_Last reviewed: 2026-06-05 by `claude`_
