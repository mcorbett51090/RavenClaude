# Decision Tree: Quota / token exhaustion failover

**When this applies:** A coding agent or surface returns quota, rate-limit, weekly/monthly cap, spend-limit, or tokens-exhausted (Claude Code weekly limit, Codex/ChatGPT caps, Cursor cloud-agent spend limit, Copilot premium-request exhaustion).

**Last verified:** 2026-09-04 (methodology; vendor reset times and prices are `[verify-at-use]`).

**Hard gate:** do not silent-fail; do not blindly retry the exhausted surface; traverse before naming a substitute SKU; then map the leaf through the vendor-neutral tier tree + closed-world lineup.

```mermaid
flowchart TD
    START[Quota or limit error] --> CLASS{Limit type?}
    CLASS -->|Context overflow| CTX[Context-window planning: reshape / smaller window / different window model]
    CLASS -->|Short rate limit| BACKOFF[Backoff once then recheck]
    BACKOFF -->|Repeats| SOFT
    CLASS -->|Soft quota hourly/daily| SOFT[Wait OR failover]
    CLASS -->|Hard weekly/monthly/spend| HARD[Failover required until reset]
    SOFT --> REC
    HARD --> REC
    CTX --> DONE[Deliver failover plan]
    REC[Record surface model error reset-time task-state] --> ORDER{Failover order}
    ORDER --> S1[1 Same vendor different surface]
    S1 --> S2[2 Same tier different vendor closed-world]
    S2 --> S3[3 Lower-cost tier that still fits task leaf]
    S3 --> S4[4 Wait until reset if deadline allows]
    S4 --> S5[5 Escalate CoS/Matthew for plan upgrade only]
    S1 --> DONE
    S2 --> DONE
    S3 --> DONE
    S4 --> DONE
    S5 --> DONE
```

**Rationale:** same-tier alternate vendors usually beat upgrading to a frontier SKU just because one vendor is capped. Surface failover (CLI → cloud agent) often unlocks the same model family under a different meter.

**Tradeoffs:**

| Move | When | Trap avoided |
|---|---|---|
| Same vendor, other surface | CLI weekly-capped but cloud agent available | Abandoning the vendor unnecessarily |
| Same tier, other vendor | Cap is hard and task still needed | Blind prestige upgrade |
| Wait for reset | Soft deadline; quality bar unmet by alternates | Burning money on wrong tier |
| Escalate for plan upgrade | Alternates fail quality bar and deadline is hard | Surprise spend without Matthew |

**Anti-patterns:** identical retries on exhausted surface; hiding the limit; inventing SKUs not in the lineup / live catalog.
