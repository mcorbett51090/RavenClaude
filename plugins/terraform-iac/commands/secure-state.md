---
description: "Design safe remote state: locking, encryption, versioning, blast-radius isolation, and no secrets."
argument-hint: "[backend + environments]"
---

You are running `/terraform-iac:secure-state`. Use `iac-policy-and-state-engineer` + the `terraform-state-safety` skill.

## Steps
1. Specify a remote backend with locking + encryption + versioning.
2. Isolate state by blast radius/environment.
3. Keep secrets out; treat the whole file as sensitive (encrypt + restrict).
4. Add scheduled drift detection.
5. Emit the backend design (from `templates/remote-state-backend.md`) + Structured Output block.
