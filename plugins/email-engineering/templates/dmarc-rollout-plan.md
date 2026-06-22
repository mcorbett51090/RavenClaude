# DMARC rollout plan — <domain>

> A staged, evidence-gated path from no-policy to `p=reject`. Never skip a stage. Fill the brackets.

## 0. Pre-flight

- Sending domain: `<domain>` (organizational domain that owns `_dmarc`)
- Known sending sources (ESPs, app servers, third parties): `<list every source — each must align>`
- RUA mailbox for aggregate reports: `dmarc@<domain>` (or a DMARC-analytics vendor)

## 1. Authenticate every source

| Source | SPF include / IP | DKIM selector | Aligns on | Status |
| --- | --- | --- | --- | --- |
| `<ESP 1>` | `<include:...>` | `<selector>` | DKIM / SPF | ☐ |
| `<app server>` | `<ip4:...>` | `<selector>` | DKIM / SPF | ☐ |

> Every legitimate source must align (return-path or `d=` matching `<domain>`) before you enforce. SPF breaks on forwarding — make **DKIM** alignment the durable one.

## 2. Monitor — `p=none`

```
_dmarc.<domain>  TXT  "v=DMARC1; p=none; rua=mailto:dmarc@<domain>; fo=1"
```

- Publish and collect aggregate reports for **~2 weeks**.
- Exit criterion: **every** legitimate source shows `dmarc=pass` (aligned) in the reports; no surprises.

## 3. Quarantine (ramped) — `p=quarantine`

```
_dmarc.<domain>  TXT  "v=DMARC1; p=quarantine; pct=25; rua=mailto:dmarc@<domain>; fo=1"
```

- Ramp `pct`: 25 → 50 → 100 over days, watching reports.
- Exit criterion: no legitimate mail quarantined at `pct=100`.

## 4. Enforce — `p=reject`

```
_dmarc.<domain>  TXT  "v=DMARC1; p=reject; rua=mailto:dmarc@<domain>; fo=1"
```

- Only after stages 2-3 show legitimate streams clean.
- Keep `rua` forever — it's your ongoing spoofing/visibility signal.

## 5. (Optional) BIMI

- Requires `quarantine`/`reject` + an SVG logo, and generally a **VMC/CMC certificate** for Gmail/Apple display. **Verify current requirement** before committing.

## Sign-off

- [ ] All sources aligned (stage 1 table complete)
- [ ] 2 weeks of clean RUA at `p=none`
- [ ] Ramped through `quarantine` with no legitimate mail lost
- [ ] `p=reject` published, `rua` retained
