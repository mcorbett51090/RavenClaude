# Migration plan — <change>

**Table traffic:** <hot/cold>  **Reversible:** yes

| Step (separate deploy) | DDL/DML | Locks? | Rollback |
|---|---|---|---|
| 1. expand | add nullable column | no | drop column |
| 2. backfill | batched UPDATE (throttled) | row-level | n/a |
| 3. constrain | ADD CONSTRAINT NOT VALID; VALIDATE | brief | drop constraint |
| 4. switch | app reads new | — | flag back |
| 5. contract | drop old | brief | restore from backup |

_Sequence with devops-cicd/release-engineer._
