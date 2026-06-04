# Federate with OIDC, don't paste static keys

CI should authenticate to the cloud with short-lived OIDC-federated tokens, not a long-lived access key stored as a CI secret. Static keys leak via logs, forks, and screen-shares and rarely get rotated.
