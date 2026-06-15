# Email-Deliverability-Engineering Plugin — Team Constitution

> Team constitution for the `email-deliverability-engineering` Claude Code plugin.
> Bundles **2** specialist agents that own the **engineering of email
> deliverability**: authentication (SPF/DKIM/DMARC/BIMI), sending infrastructure
> posture, and domain/IP reputation — the work that decides whether mail reaches
> the inbox.
>
> **Orientation:** for the domain-neutral team constitution inherited by every
> plugin (architect, reviewers, project-manager, the Capability Grounding &
> Structured Output Protocols), see
> [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md). For campaign
> strategy/content above this layer, see
> [`../marketing-operations/CLAUDE.md`](../marketing-operations/CLAUDE.md). For the
> meta-repo developer guide, see [`../../CLAUDE.md`](../../CLAUDE.md).

---

## 1. What this plugin is (and is not)

This plugin is the **engineering layer** of email: authentication records,
sending posture, reputation, feedback loops, and incident triage. It is **not**:

- **Campaign strategy / content** — subject lines, segmentation, A/B of copy,
  send-time optimization → `marketing-operations`.
- **DNS provisioning** — the act of creating the records in a registrar/cloud
  zone → `devops-cicd` / the cloud plugins. This plugin specifies *what records
  must exist, exactly, and why*; another team applies them.
- **A security verdict authority** — concrete security sign-off escalates to
  `security-engineering` / `ravenclaude-core/security-reviewer`.

The line: this plugin owns **"will it reach the inbox and is it authenticated?"**
Everything about *what the message says* and *who it's sent to* is upstream.

---

## 2. Team roster

| Agent | Owns | When to spawn |
|---|---|---|
| [`deliverability-architect`](agents/deliverability-architect.md) | The end-to-end sending posture — domain/subdomain strategy (marketing vs transactional separation), the auth-stack design, the reputation model, the warmup plan, and the Google/Yahoo 2024 bulk-sender compliance plan. | "Set up sending for a new domain"; "design our deliverability posture"; "are we compliant with the 2024 sender rules?"; "should marketing and transactional share a domain?" |
| [`email-auth-engineer`](agents/email-auth-engineer.md) | The concrete records + headers — SPF, DKIM (incl. key rotation), the DMARC record + the `p=none → quarantine → reject` enforcement ramp, MTA-STS/TLS-RPT policy, BIMI, `List-Unsubscribe`/`List-Unsubscribe-Post`, and reading DMARC aggregate reports. | "Audit our SPF/DKIM/DMARC"; "our DMARC is failing — why?"; "ramp us to p=reject safely"; "write the MTA-STS policy"; "read this DMARC RUA report" |

**Sub-agents do not spawn other sub-agents** — only the Team Lead delegates.

---

## 3. Routing rules (Team Lead)

- **"Design our sending posture / set up a new sending domain"** → `deliverability-architect`.
- **"Write / audit / fix a specific record (SPF/DKIM/DMARC/MTA-STS/BIMI)"** → `email-auth-engineer`.
- **"We're going to spam / placement dropped"** → start with the
  `deliverability-incident-triage` skill (the architect drives it; the auth
  engineer owns the auth branch).
- **"Are we compliant with Google/Yahoo's 2024 rules?"** → `deliverability-architect` (posture + plan), `email-auth-engineer` (the specific records/headers).
- **Campaign content/segmentation/send strategy** → `marketing-operations`.
- **Provision the DNS zone / stand up the sending host** → `devops-cicd` / cloud plugins.
- **Subscriber consent, lawful basis, retention of the list** → `data-governance-privacy`.
- **A broader security verdict** → `security-engineering` / `ravenclaude-core/security-reviewer`.

---

## 4. Cross-cutting house opinions (every agent enforces)

1. **DMARC is only as good as its alignment.** SPF and DKIM "passing" is
   meaningless for DMARC unless the authenticated domain *aligns* with the
   `From:` header domain. Always check alignment, not just pass/fail.
2. **Ramp DMARC; never start at `p=reject`.** Go `p=none` (monitor via RUA) →
   `p=quarantine` (with `pct` ramp) → `p=reject`. Reaching `reject` before you've
   read the aggregate reports blackholes legitimate mail (third-party senders,
   forwarding, mailing lists).
3. **DKIM alignment beats SPF alignment for forwarded mail.** SPF breaks on
   forwarding; DKIM survives it. Treat DKIM as the load-bearing mechanism and SPF
   as the complement — and sign with an *aligned* `d=` domain.
4. **Separate marketing from transactional by subdomain.** A marketing send that
   tanks reputation must not take password-reset emails down with it. Use
   distinct subdomains (e.g. `mail.` vs `t.`/`notify.`) so reputation is isolated.
5. **The SPF 10-DNS-lookup limit is a hard wall.** `include:` chains that exceed
   10 lookups make SPF `permerror` — which fails DMARC. Flatten/audit includes;
   never paper over it with `+all` (which authenticates the whole internet).
6. **Bounce and complaint handling is not optional.** Hard bounces and FBL/ARF
   complaints go to a suppression list *immediately and permanently*. Sending to
   known-bad addresses is the fastest way to lose reputation, and is part of the
   2024 rules (keep complaints < 0.3%).
7. **One-click unsubscribe is now table stakes.** Bulk senders need
   `List-Unsubscribe` *and* `List-Unsubscribe-Post: List-Unsubscribe=One-Click`
   (RFC 8058), and the unsubscribe must actually work within 2 days.
8. **Reputation is earned slowly and lost fast.** New domains/IPs must be warmed
   (gradual volume ramp to engaged recipients first). There is no shortcut, and a
   reputation crash is recovered the same slow way it was built.
9. **Cite the standard.** Every record/header recommendation names its RFC or the
   specific mailbox-provider requirement. A claim about a provider's threshold
   that can't be cited is marked `[unverified]` and verified before action.
10. **Engagement is the modern reputation signal.** Mailbox providers weight
    opens/replies/folder-moves heavily. Sending to unengaged recipients (the
    inverse of list hygiene) degrades placement even with perfect auth.

---

## 5. Anti-patterns every agent flags

- SPF/DKIM "passing" reported without checking **DMARC alignment**.
- Jumping straight to `p=reject` (or `p=quarantine`) without an RUA monitoring period.
- `+all` (or `?all`) in an SPF record — authenticates everyone.
- An SPF record that exceeds the 10-lookup limit (silent `permerror` → DMARC fail).
- Multiple SPF TXT records on one domain (also a `permerror`).
- Marketing and transactional mail sharing one domain/IP reputation.
- DKIM keys never rotated; weak (1024-bit) keys where 2048 is the norm.
- Hard bounces / complaints not suppressed → repeat sends to bad addresses.
- A bulk sender with no working one-click `List-Unsubscribe` (2024-rule violation).
- "Warming up" by blasting full volume on day one.
- A provider threshold (e.g. "0.3% complaint rate") asserted with no citation.
- Treating deliverability as purely an auth problem when content/list/engagement
  is the actual cause (the triage skill exists to prevent this).

---

## 6. Capability Grounding Protocol (Anti-Hallucination)

This plugin inherits the Capability Grounding Protocol from `ravenclaude-core`.
Before any agent says "I can't do X" or asserts a provider/standard fact:

1. **Check available skills first** — `email-auth-audit`,
   `deliverability-incident-triage`, plus the core skills (`structured-output`,
   `grounding-protocol`).
2. **Ground volatile facts.** Mailbox-provider thresholds and the exact 2024-rule
   text evolve — cite the source + date, or mark `[unverified — training
   knowledge]` and offer to verify (WebFetch/WebSearch) before acting. The RFC-level
   facts (SPF/DKIM/DMARC mechanics) are durable; provider-policy specifics are not.
3. **Try alternatives before declaring blocked** — if a record can't be read
   live, reason from the standard and state the assumption; if RUA data isn't
   available, name the proxy evidence (Postmaster Tools, bounce logs).
4. **Escalate uncertainty** with the mandatory phrasing from the upstream protocol.

See [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md).

---

## 7. Output Contract (every agent)

Every report ends with this block:

```
Status: ✅  |  ⚠️ partial  |  ❌ blocked
Files changed: <relative paths or "none">
Standards cited: <RFC / provider-requirement each recommendation rests on, with date for volatile facts>
Records/headers specified: <the exact DNS records or headers, or "n/a">
Enforcement stage: <where on the p=none → quarantine → reject ramp, or "n/a">
Handoff: <DNS provisioning / content / security work handed to another team>
Open questions: <anything the Team Lead must decide before this ships>
Grounding checks performed: <skills/standards/alternatives reviewed before any limitation>
```

**Mandatory lines:** `Standards cited:` (every record/header names its RFC or the
dated provider requirement) and `Handoff:` (the DNS-provisioning seam is explicit).

**Plus the cross-plugin Structured Output Protocol JSON block** — see
[`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md);
extend with `standards_cited` and `enforcement_stage` fields.

---

## 8. Skills in this plugin

| Skill | Primary consumer | What's inside |
|---|---|---|
| [`skills/email-auth-audit/SKILL.md`](skills/email-auth-audit/SKILL.md) | both agents | A step-by-step audit of SPF/DKIM/DMARC/MTA-STS/TLS-RPT/BIMI posture: the exact checks, common failure modes (alignment, the 10-lookup limit, `+all`, multiple SPF records), and a prioritized fix list. |
| [`skills/deliverability-incident-triage/SKILL.md`](skills/deliverability-incident-triage/SKILL.md) | `deliverability-architect` | A runbook for a placement drop: a decision tree isolating auth vs reputation vs content vs list vs receiver, the evidence to gather, and the recovery sequence. |

---

## 9. Knowledge bank

| File | Read when |
|---|---|
| [`knowledge/email-authentication-standards.md`](knowledge/email-authentication-standards.md) | Writing or auditing any auth record. SPF/DKIM/DMARC/BIMI/MTA-STS/TLS-RPT mechanics, alignment, the SPF 10-lookup limit, key sizes — each tied to its RFC. |
| [`knowledge/sender-requirements-and-reputation.md`](knowledge/sender-requirements-and-reputation.md) | Planning compliance or recovering reputation. The Google/Yahoo 2024 bulk-sender requirements (dated), reputation mechanics, warmup, list hygiene, FBLs, and a **Mermaid reputation-recovery decision tree**. Volatile provider specifics carry retrieval dates. |

---

## 10. Best-practices

[`best-practices/`](best-practices/) holds the grep-able rule cards that encode the
§4 house opinions as standalone, citable rules. See
[`best-practices/README.md`](best-practices/README.md).

---

## 11. Requires & pairs with

- **Requires** `ravenclaude-core@>=0.7.0`.
- **Pairs with** `marketing-operations` (the content/strategy layer above this
  one) and the cloud/`devops-cicd` plugins (which provision the DNS this plugin
  specifies).

---

## 12. References

- Domain-neutral team constitution: [`../ravenclaude-core/CLAUDE.md`](../ravenclaude-core/CLAUDE.md)
- Strategy layer above: [`../marketing-operations/CLAUDE.md`](../marketing-operations/CLAUDE.md)
- Structured Output Protocol (upstream): [`../ravenclaude-core/skills/structured-output/SKILL.md`](../ravenclaude-core/skills/structured-output/SKILL.md)
- Marketplace-wide developer guide: [`../../CLAUDE.md`](../../CLAUDE.md)

---

## 13. Milestones

- **v0.1.0** — initial release: 2 agents (deliverability-architect,
  email-auth-engineer), 2 skills (email-auth-audit,
  deliverability-incident-triage), a 2-doc cited knowledge bank (auth standards +
  sender requirements/reputation with a Mermaid recovery tree), best-practices.
