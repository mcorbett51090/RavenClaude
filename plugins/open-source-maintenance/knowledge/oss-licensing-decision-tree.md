# Knowledge — Open-source license selection

> **Last reviewed:** 2026-06-23 · **Confidence:** High (SPDX + choosealicense.com consensus; copyleft reach is settled law/practice). **Not legal advice** — flag commercial/patent stakes for a lawyer.
> The `oss-maintainer-strategist` traverses this tree **before** naming a license. The governing constraint is upstream, not downstream: the strongest copyleft in your dependency graph constrains the whole work.

The discipline: **name the license from this tree, then verify dependency compatibility, then emit the LICENSE/NOTICE files** — never the reverse.

---

## Decision Tree: choosing an open-source license

```mermaid
flowchart TD
  Start([New project / first public release]) --> DEP{Any copyleft<br/>dependencies?}
  DEP -->|GPL in graph| GPLDEP[Distribution makes your work effectively GPL.<br/>Use GPL-3.0 or rework the dependency.]
  DEP -->|AGPL in graph| AGPLDEP[Even hosted/SaaS use triggers source-sharing.<br/>Use AGPL-3.0 or replace the dependency.]
  DEP -->|LGPL/MPL only| WEAK[Weak copyleft is file/library-scoped —<br/>you may pick a permissive license for YOUR code,<br/>but keep the dependency's files under its license.]
  DEP -->|Permissive / none| INTENT{Your intent?}

  WEAK --> INTENT
  INTENT -->|Maximize adoption, embeddable anywhere| PATENT{Patent risk or<br/>corporate contributors?}
  INTENT -->|Derivatives must stay open| NETWORK{Does network/SaaS<br/>use count?}

  PATENT -->|Yes| APACHE[Apache-2.0<br/>permissive + explicit patent grant]
  PATENT -->|No| MIT[MIT<br/>shortest, most permissive]

  NETWORK -->|Yes — close the SaaS gap| AGPL[AGPL-3.0]
  NETWORK -->|No — distribution only| LIBQ{Is it a library<br/>meant to be linked?}
  LIBQ -->|Yes| LGPL[LGPL-3.0 or MPL-2.0<br/>copyleft on the library, linkable from closed code]
  LIBQ -->|No — an application| GPL[GPL-3.0]
```

## Contribution agreement (orthogonal to the license)

```mermaid
flowchart TD
  C([Accepting outside contributions?]) --> NEED{Do you need aggregated<br/>rights / relicensing optionality<br/>/ a dual-license business?}
  NEED -->|No| DCO[Use the DCO<br/>Signed-off-by line; inbound=outbound.<br/>Lowest friction — the default.]
  NEED -->|Yes| CLA[Use a CLA<br/>but accept the contributor friction;<br/>prefer a well-known CLA, not a bespoke one.]
```

## Reference table

| License | Type | Use it when | Watch out for |
|---|---|---|---|
| MIT | permissive | maximum adoption, simplest terms | no explicit patent grant |
| Apache-2.0 | permissive | adoption + patent protection | NOTICE file obligations |
| BSD-2/3-Clause | permissive | MIT-like, BSD ecosystem norms | 3-Clause's no-endorsement term |
| MPL-2.0 | weak copyleft | file-scope reciprocity, linkable | per-file boundary |
| LGPL-3.0 | weak copyleft | library copyleft, closed-code linking | relinking obligation |
| GPL-3.0 | strong copyleft | applications, derivatives stay open | constrains the whole distributed work |
| AGPL-3.0 | strong copyleft (network) | close the hosted-SaaS loophole | scares some corporate adopters |

## Provenance
- SPDX License List (canonical identifiers + verbatim text), choosealicense.com (GitHub/OSI guidance), OSI approved-licenses list. Copyleft reach (GPL "distribution", AGPL "network use") per the respective license texts. Last reviewed 2026-06-23.
- See also [`community-health-and-governance.md`](community-health-and-governance.md) for CLA/DCO operational mechanics and [`../best-practices/license-before-first-public-commit.md`](../best-practices/license-before-first-public-commit.md).
