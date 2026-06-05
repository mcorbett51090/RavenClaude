# Bind IAM to the pod identity, not the node role

**Status:** Absolute rule
**Domain:** AWS IAM / EKS
**Applies to:** `aws-cloud`

---

## Why this exists

When workloads on EKS use the EC2 node's IAM role for AWS API calls, every pod on that node inherits the same permissions — whether it's your payment service or a compromised open-source dependency. The node role must be broad enough for every workload on it, which consistently over-provisions. IAM Roles for Service Accounts (IRSA) and the newer EKS Pod Identity (v1.24+) let you bind a distinct IAM role to each Kubernetes ServiceAccount, so the permissions travel with the pod identity, not the hardware it happens to run on.

## How to apply

**IRSA (works on all EKS versions):**

```hcl
resource "aws_iam_role" "my_service" {
  name = "my-service-irsa"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.eks.arn }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "${aws_iam_openid_connect_provider.eks.url}:sub" = "system:serviceaccount:my-ns:my-sa"
          "${aws_iam_openid_connect_provider.eks.url}:aud" = "sts.amazonaws.com"
        }
      }
    }]
  })
}
```

In the pod spec annotate the ServiceAccount:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-sa
  namespace: my-ns
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::<account>:role/my-service-irsa
```

**EKS Pod Identity (EKS add-on, v1.24+):**
```bash
aws eks create-pod-identity-association \
  --cluster-name my-cluster \
  --namespace my-ns \
  --service-account my-sa \
  --role-arn arn:aws:iam::<account>:role/my-service-pod-identity
```

**Do:**
- One IAM role per Kubernetes ServiceAccount, scoped to the minimum S3/DynamoDB/Secrets Manager calls that service needs.
- Remove all AWS permissions from the EC2 node role except those the kubelet/CNI genuinely require (e.g., `ec2:DescribeInstances` for node registration, ECR pull).
- Prefer EKS Pod Identity for new clusters (no OIDC thumbprint management, no condition string to get wrong).

**Don't:**
- Grant `s3:*` or `dynamodb:*` to the node role because "every service needs S3."
- Skip the `StringEquals` condition on the IRSA trust policy — without the namespace/service-account constraint, any pod in the cluster can assume the role.
- Use EC2 instance profiles or environment variable `AWS_ACCESS_KEY_ID` on pods.

## Edge cases / when the rule does NOT apply

DaemonSets that must interact with EC2 APIs at the node level (CNI plugins, node-termination handlers) legitimately need node-role permissions. Keep those permissions narrow and separate from application roles.

## See also

- [`../agents/aws-iam-identity-engineer.md`](../agents/aws-iam-identity-engineer.md) — writes the trust policy and the least-privilege inline policy
- [`./roles-not-keys.md`](./roles-not-keys.md) — the broader principle (roles over keys) of which IRSA is the EKS expression

## Provenance

Codifies AWS Well-Architected Security Pillar SEC05-BP01 (use temporary credentials) and the AWS EKS Best Practices Guide §IAM. EKS Pod Identity is the newer AWS-native option, GA since EKS 1.24.

---

_Last reviewed: 2026-06-05 by `claude`_
