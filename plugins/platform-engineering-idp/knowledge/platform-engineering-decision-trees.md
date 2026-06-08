# Platform Engineering & IDP — Decision Trees + 2026 Capability Map

> Canonical knowledge bank for `platform-engineering-idp`. **Traverse the relevant Mermaid tree
> top-to-bottom before choosing** — the proactive complement to the Capability Grounding Protocol.
> Volatile product/version facts in the capability map carry a retrieval date and a re-verify-at-use
> rider.

---

## Decision Tree: Should you start a platform team / what should it own first

```mermaid
flowchart TD
  A[Developers report recurring friction shipping?] -->|No / one-off| Z[Don't start a platform team yet. A README + a repo template is enough.]
  A -->|Yes, recurring| B{How many stream-aligned teams feel it?}
  B -->|1-2 teams| C[Embed an enabling person; codify a paved-road template. No standing platform team yet.]
  B -->|3+ teams, same friction| D{Is the friction in ONE journey or many?}
  D -->|One dominant journey| E[Thinnest viable platform: pave THAT journey first<br/>e.g. create-a-new-service or get-a-database]
  D -->|Many| F[Still pick ONE to pave first — rank by frequency x pain x number-of-teams]
  E --> G[Name the cognitive load removed; set an adoption goal, not a feature count]
  F --> G
```

**Leaf rule:** below ~3 teams sharing the same friction, a paved-road repo template beats a standing
platform team. The first thing a real platform team owns is the single highest-frequency × highest-
pain developer journey — not a portal.

---

## Decision Tree: Buy-vs-build the IDP / portal

```mermaid
flowchart TD
  A[Do you actually need a portal yet?] -->|No golden path worth surfacing| Z[Not yet. Ship one paved road + a README first.]
  A -->|Yes, multiple things to surface| B{Deep, bespoke customization a real requirement?}
  B -->|No — standard catalog + scorecards + templates| C{Maintenance budget for an OSS platform?}
  C -->|Thin / no dedicated owner| D[Buy a managed portal<br/>Port / Cortex / OpsLevel / Spotify Portal]
  C -->|Have a dedicated platform team| E{Want max control + OSS + plugin ecosystem?}
  B -->|Yes — heavy custom plugins, unusual model| E
  E -->|Yes| F[Build on Backstage<br/>accept the upgrade/maintenance cost]
  E -->|No| D
  D --> G[Catalog still as code; own every entity]
  F --> G
```

**Leaf rule:** buy/adopt before you build; build before you framework. Backstage's power is real and
so is its maintenance cost — choose it for genuine customization + a team to maintain it, not for
prestige. Either way the catalog lives **as code in the repo it describes**.

---

## Decision Tree: Golden-path scoping (what to pave, and the escape hatch)

```mermaid
flowchart TD
  A[Is there a common service/workload shape ~80% of teams use?] -->|No, all bespoke| Z[Don't force a path yet; document patterns, gather the common shape first.]
  A -->|Yes| B[Pave THAT shape: create -> build -> deploy -> run, defaults baked in]
  B --> C{Does doing it the paved way feel easier than rolling your own?}
  C -->|No| D[Not paved yet — remove friction until the supported way is the lazy way]
  C -->|Yes| E[Add the escape hatch: stepping off is allowed + unsupported]
  E --> F{A team keeps taking the same escape?}
  F -->|Yes| G[Fold that escape into a new supported variant]
  F -->|No| H[Leave it; the 20% stays bespoke]
```

**Leaf rule:** pave the 80% path, make the supported way the easiest way, and keep an escape hatch.
A path with no exit becomes a shadow platform. A recurring escape is a signal to pave a new variant.

---

## Decision Tree: The self-service boundary (button vs ticket)

```mermaid
flowchart TD
  A[How often is this provisioning requested?] -->|Rare / one-off| T[Keep it a ticket; automation isn't worth it yet]
  A -->|Frequent / recurring| B{Reversible if wrong?}
  B -->|Hard to reverse| C{Blast radius if misused?}
  B -->|Easily reversible| D[Self-service button with sane defaults]
  C -->|Large blast radius| E[Self-service WITH guardrails: policy + quotas + bounded defaults; no human gate on the happy path]
  C -->|Small| D
  D --> F[Instrument usage as an adoption signal]
  E --> F
```

**Leaf rule:** make it self-service when it's frequent; guardrail (policy/quotas/defaults) rather than
human-gate when blast radius is large. A "self-service" form that opens a ticket for the common case
is a service desk in disguise. Choose the mechanism — Crossplane composition vs Score spec vs portal-
fronted Terraform module — by who owns the control plane and how k8s-native the estate is.

---

## Decision Tree: Which DevEx metric framework

```mermaid
flowchart TD
  A[What question are you answering?] --> B{Delivery throughput & stability?}
  B -->|Yes| C[DORA: deploy freq, lead time, change-fail rate, MTTR]
  A --> D{The whole multidimensional picture?}
  D -->|Yes| E[SPACE: satisfaction, performance, activity, communication, efficiency]
  A --> F{Felt friction / cognitive load / flow?}
  F -->|Yes| G[DevEx/DXI lens + a developer survey]
  C --> H[Balance the set: 1 delivery + 1 perception + 1 adoption metric]
  E --> H
  G --> H
  H --> I[Never measure individuals; attach a decision to every metric]
```

**Leaf rule:** use DORA for delivery, SPACE for breadth, DevEx/DXI for felt friction — and always
ship a *balanced* set (a delivery metric + a perception metric + an adoption metric) so no single
proxy gets gamed. Measure the system, never the individual; every metric must inform a decision.

---

## Platform maturity staging (the ladder)

| Stage | What it looks like | Move to the next stage by… |
|---|---|---|
| **1. Ad-hoc** | Every team builds + deploys its own way; tribal knowledge; tickets for infra. | Documenting the common shape; shipping one paved-road template. |
| **2. Paved road** | A supported template exists; some teams use it; still manual infra. | Making the supported way the *easiest* way; adding the escape hatch. |
| **3. Self-service** | Common infra is a button with guardrails; no ticket for the common case. | Surfacing it in a portal/catalog; instrumenting adoption. |
| **4. Platform-as-product** | Portal + catalog + golden paths; adoption measured; platform has a roadmap & users. | Continuous DevEx measurement; retiring features nobody adopts. |

---

## 2026 capability map — IDP / portal landscape (dated, re-verify at use)

_Retrieved 2026-06-08. Product positioning and pricing are volatile — re-confirm at use; this is
orientation, not a procurement recommendation._

| Category | Options (2026) | Notes |
|---|---|---|
| **OSS portal framework** | **Backstage** (CNCF, Spotify-origin) — dominant (~89% IDP-portal share, 270+ public adopters). | Maximum control + plugin ecosystem; real upgrade/maintenance cost. Needs a team to own it. |
| **Managed portals** | **Port**, **Cortex**, **OpsLevel**, **Spotify Portal** (managed Backstage), **Roadie** (managed Backstage). | Faster time-to-value, less bespoke; good when customization is standard and maintenance budget is thin. |
| **Self-service infra control plane** | **Crossplane** (k8s-native control plane, compositions), **Score** (workload spec decoupled from platform), **Terraform/OpenTofu modules** fronted by a portal/template, **Kratix** (promises). | Choose by how k8s-native the estate is and who owns the control plane. |
| **Policy / guardrails** | **OPA/Gatekeeper**, **Kyverno**, **Conftest**. | Make self-service buttons safe without a human gate on the happy path. |
| **DevEx measurement** | **DORA** (Google/DORA), **SPACE** framework, **DevEx/DXI** (DX, GetDX), homegrown survey + telemetry. | Pair system metrics with a survey; never measure individuals. |
| **Team model** | **Team Topologies** (platform group, enabling teams, stream-aligned teams). | The platform team's job is reducing others' cognitive load. |

> Provenance: CNCF/Backstage adoption + Gartner platform-team forecast and the DORA/SPACE/DevEx
> literature, retrieved 2026-06-08; see `docs/research/2026-06-08-twenty-candidate-plugins/sources.md`.
> Shares, adopter counts, and product names are volatile — re-verify at use. No invented products.

---

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — team constitution & seams.
- [`../best-practices/README.md`](../best-practices/README.md) — the named, citable rules.
- Neighbour decision trees: `devops-cicd`, `cloud-native-kubernetes`, `terraform-iac`,
  `observability-sre`.

_Last reviewed: 2026-06-08 by `claude`._
