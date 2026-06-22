# ITIL 4 — Practices Reference

_The ITIL 4 service value system, the guiding principles, and the practice catalog with when-to-reach-for-each. Adopt lightly — practices serve value, not the reverse. Principle-stable; last reviewed: 2026-06-19. `[unverified — training knowledge]` for any specific framework wording; the structure below is the durable shape, not a quotation._

## The service value system (SVS)
ITIL 4 frames service management as a system: **guiding principles** → **governance** → the **service value chain** (plan, improve, engage, design & transition, obtain/build, deliver & support) → **practices** → **continual improvement**. Practices feed the value chain; nothing is adopted that doesn't trace to value.

## The seven guiding principles
1. **Focus on value** — every activity must trace to value for a stakeholder.
2. **Start where you are** — assess what exists before replacing it; don't rip-and-replace reflexively.
3. **Progress iteratively with feedback** — improve in increments, measure, adjust.
4. **Collaborate and promote visibility** — work across silos; hidden work breeds distrust.
5. **Think and work holistically** — the service is an end-to-end system, not isolated parts.
6. **Keep it simple and practical** — remove anything that doesn't contribute to value (the anti-bureaucracy principle).
7. **Optimize and automate** — optimize first, then automate the optimized.

## The common-core practices (adopt first, lightly)
| Practice | What it does | Reach for it when |
|---|---|---|
| **Incident management** | Restore normal service operation as fast as possible | Something is broken now |
| **Problem management** | Find and remove the causes of incidents (reactive + proactive) | An incident recurs, or you want to prevent one |
| **Change enablement** | Maximize successful changes by assessing and authorizing them | Anything alters a service/CI |
| **Service request management** | Fulfill standard, pre-approved user requests from a catalog | A routine ask (access, equipment, how-to) |
| **Service desk** | The single point of contact; capture, resolve, route, communicate | The user-facing front door of IT |
| **Service configuration management** | Maintain CIs + relationships (the CMDB) for the other practices | You need a configuration source of truth for impact/change/incident |

## Add-on practices (adopt on demonstrated need)
- **Service level management** — define and track SLAs/OLAs/UCs end-to-end.
- **Availability / capacity & performance / continuity** — when reliability, scale, or disaster recovery becomes a named concern.
- **Release management / deployment management** — coordinate what ships when and how it lands (deployment automation → `devops-cicd`).
- **Knowledge management** — shift-left deflection via articles + self-service.
- **Monitoring & event management** — engineering telemetry overlaps `observability-sre`; coordinate.
- **Continual improvement** — the standing practice that keeps the system getting better.

## The anti-pattern this reference guards against
Adopting practices because the framework lists them — a full CAB for trivial changes, an SLA with no OLA behind it, a CMDB nobody maintains. ITIL 4's own guiding principles (#6 keep it simple, #1 focus on value) say to cut these. Right-size, don't maximize.
