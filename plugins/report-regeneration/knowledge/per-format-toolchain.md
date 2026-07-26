# Per-format toolchain — `report-regeneration`

**Status:** knowledge-bank deliverable (plan §9 — `knowledge/` "per-format toolchain map"). Non-normative *reference*: [`core-architecture-spec.md`](core-architecture-spec.md) owns the taxonomy/harness/schemas, [`powerbi-ingest-contract.md`](powerbi-ingest-contract.md) owns the Power BI route contract, [`threat-model-stride.md`](threat-model-stride.md) owns the security pass. This document does not restate any of the three — it answers one question: **which tool does which job, at which tier, on what evidence.**

**Output formats are HTML and Office ONLY.** Power BI is an **input** source (data + a screenshot), never an output — see [`core-architecture-spec.md`](core-architecture-spec.md) §1. The tables below follow that split.

---

## 1. Why a map, not a single stack

The product is **one Binding Manifest schema + one verification harness across two byte-level output engines + one Power BI ingestion adapter** — not one templating engine (plan §2, RT2-F3: "Do not measure Bet-1 as '≤20% format-specific LOC'... per-format byte-level engines... are expected, not a bet failure"). Each format gets its own parse/emit/render/a11y tools; the harness (V1–V6 + period-coherence) is the one thing that's shared.

---

## 2. HTML / web→PDF

| Stage | Tool | Tier | Note |
|---|---|---|---|
| **Structural parse — floor** | stdlib `html.parser` | Tier-A (always available) | `rebind-manifest`'s taint-dictionary + earned-frozen detector run on this today, stdlib-only, no pip, no network (verified in `skills/rebind-manifest/SKILL.md`: "Stdlib only (`argparse`/`html.parser`/`re`/`json`/`pathlib`)"). `doctor.py`'s `TIER_A_STDLIB` list names `html.parser` explicitly as one of the tools "the load-bearing checks never depend on a pip install" for. |
| **Structural parse — accel** | selectolax (lexbor backend) or lxml | Tier-B (doctor-gated) | selectolax is **5–30× faster than BeautifulSoup**, read-only + CSS-selectors only, tree held in C memory; lxml is comparably fast and adds XPath. BeautifulSoup only if the tree must be *mutated* — not our read-time case (claims-table claim 12). Absent → `doctor.py` degrade: "fall back to stdlib html.parser (lower fidelity on malformed HTML)." |
| **Regenerate (templating)** | Jinja2 | Tier-B, **required** for the HTML lane | The mature Python templating engine; docxtpl (Office) wraps it (claim 13). `doctor.py`: absence **blocks the v0.1.0 lane** — the only tool on the list marked non-optional. |
| **Render — fidelity copy** | Playwright / headless Chromium | Tier-B | Highest layout fidelity (real Chrome, modern CSS/JS), fastest (~13 ms warm). **wkhtmltopdf is deprecated — do not use** (archived Jan 2023, last release 2020, unpatched SSRF CVSS 9.8) (claim 9). Also the auto-capture fallback route for the Power BI screenshot (§4). |
| **Render — accessible copy** | WeasyPrint, `pdf_variant="pdf/ua-1"` | Tier-B | Pure-Python, implements CSS Paged Media, cleaner pagination, but slower (~600 ms) and weaker on advanced layout (claim 9). Emits PDF/UA but the docs state output is **"not guaranteed to be valid"** (claim 10) — **never trusted on faith**, always gated by veraPDF (§5). |
| **Why two render outputs, not one** | — | — | Headless-Chromium print does **not** reliably produce a *tagged* PDF — its strength is visual fidelity, not the tag tree (claim 11, `[unverified — needs a direct Chromium-print-to-tagged-PDF spike]`; the plan's Phase-1 pre-build gate names exactly this spike — "veraPDF-on-a-Chromium-print run... settles C11" — **not yet run this session**; see `BUILD-STATE.md`). Until that spike lands, the architectural split (Playwright = fidelity copy, WeasyPrint `pdf/ua-1` = accessible copy) is the working assumption, not a confirmed fact. |
| **a11y gate** | axe-core + veraPDF | Tier-B | See [`wcag-floor.md`](wcag-floor.md) for the honest coverage story. |

---

## 3. Office (docx → PDF)

| Stage | Tool | Tier | Note |
|---|---|---|---|
| **Structural parse — floor** | stdlib `zipfile` + `xml.etree.ElementTree` | Tier-A (always available) | `.docx` is an OPC/zip container of XML parts — the same container shape V4's egress scan unzips (`core-architecture-spec.md` §6: "unzip every OPC container... `word/embeddings/*.xlsx`, `word/charts/*.xml`, `docProps/*`..."). `doctor.py`'s `TIER_A_STDLIB` list names both `zipfile` and `xml.etree.ElementTree` as always-available. |
| **Structural parse — accel** | python-docx + a manual `document.element.body` walk | Tier-B | python-docx reads/writes paragraphs/tables/sections/styles, but **does not iterate paragraphs and tables in document order out of the box** (long-standing issue #276) — true ¶+table order needs the manual body-XML walk (claim 14). Absent → `doctor.py` degrade: "Office lane (v0.2.0) unavailable." |
| **Regenerate (templating)** | docxtpl | Tier-B | Wraps python-docx + Jinja2 so a Word file itself is the template (claim 13). Absent → degrade: "use python-docx direct manipulation (more code)." |
| **Render — PDF + accessible copy** | LibreOffice `--headless` PDF export | Tier-B | The "Universal Accessibility (PDF/UA)" export option **auto-enables tagged PDF and cannot be disabled** — a scriptable, local, no-cloud docx→accessible-PDF path (claim 15). Also the V5 render referee for Office: render → screenshot capture. Absent → degrade: "Office PDF export unavailable; emit .docx only." |
| **a11y gate** | veraPDF | Tier-B | Same validator as the HTML→PDF path — see [`wcag-floor.md`](wcag-floor.md). |

---

## 4. Power BI (input source ONLY — never an output)

| Stage | Tool / route | Tier | Note |
|---|---|---|---|
| **Data — confirmed tenant route** | XMLA endpoint (DAX) | Tier-B | Requires Premium / PPU / Fabric capacity (claim 7). **No macOS-runnable native XMLA client exists today** — `pyadomd` is Windows/.NET-Framework-only (COM-registered); `doctor.py` labels it "EXPECTED-ABSENT on macOS." See [`powerbi-ingest-contract.md`](powerbi-ingest-contract.md) §2 for the full gap analysis. |
| **Data — macOS fallback** | REST `executeQueries` (DAX, JSON) | Tier-B | Plain JSON over HTTPS, stdlib-parseable, works on Pro/PPU/Premium/Fabric. **Do not conflate with `executeDaxQueries` (Arrow)** — the claims-table's claim 7 does exactly that; the correction (two distinct endpoints, different limits/auth/response shape) lives in `powerbi-ingest-contract.md` §1 and is authoritative over claim 7's original text. `scripts/powerbi_probe.py`'s `data` subcommand implements this route (verified this session — `POST .../datasets/{id}/executeQueries`). |
| **Screenshot — primary route (current implementation)** | Power BI REST `ExportToFile` (server-side render, service-principal auth, no browser) | Tier-B | **This is the current adopted primary route** — confirmed this session directly in `scripts/powerbi_probe.py` (`probe_shot()`: "PRIMARY: ExportToFile"), and in `scope.md` rev. 2 / `BUILD-STATE.md`. It postdates `powerbi-ingest-contract.md`'s original framing (Playwright named as "target route" — written slightly earlier in the same session, before the maintainer's ExportToFile decision). Readers of `powerbi-ingest-contract.md` should treat its §5 decision diagram as the *fallback-ordering rationale* (still correct) but read "primary route = ExportToFile" as the current fact, sourced here and in the code, not there. |
| **Screenshot — fallback** | Playwright vs the published-report Service UI (injected auth header) | Tier-B | Used only if ExportToFile fails/unavailable (`powerbi_probe.py`: "fallback route — primary ExportToFile failed or was unavailable"). |
| **Screenshot — always-available fallback** | user-provided image | none (no tooling dependency) | The last resort, and the only route requiring no auth/tenant capability at all (`powerbi-ingest-contract.md` §5). |
| **Never** | PBIR / .pbix parsing or emission | — | Removed by the rev.-2 scope decision (`scope.md`) — Power BI contributes data + a screenshot, nothing is round-tripped as a Power BI artifact (`core-architecture-spec.md` §1). |

Both the PBI-sourced data value and the PBI screenshot are `regenerate`/verified assets, never transplanted — see `core-architecture-spec.md` §4 (construction rule) and [`inference-failure-modes.md`](inference-failure-modes.md) for how a stale or wrong PBI figure is caught.

---

## 5. The two-tier gate split (plan §8, binding)

The stack is heavy (Docling, Playwright+Chromium, WeasyPrint's native pango/gobject deps, veraPDF's JRE, LibreOffice ~10 GB, axe/Node, an XMLA/REST client) — a sharp break from the reused skills' stdlib-only convention. Two tiers, not one gate:

| Tier | What lives here | Enforcement | Degrade behavior |
|---|---|---|---|
| **Tier-A** | schema validation, the taint scan, AST/DOM/body-XML diffs (V2), the manifest-completeness/coverage leg (V6), period-coherence — everything deterministic and stdlib-only | CI-enforced, every PR | These are the ML-free legs that carry the dominant-failure-mode load (§ `inference-failure-modes.md`) — they never depend on a pip install. |
| **Tier-B** | V5 render referee, axe/veraPDF, LibreOffice PDF export, the XMLA/REST data-read + Service screenshot capture, VLM labeling | doctor-gated (`doctor.py`), LOUD-skip in CI, enforced locally at release time | Modeled on the repo's Gate-10 pinned-binary precedent: **"A SKIP IS NOT A PASS."** An unrunnable Tier-B gate is a loud skip locally and a hard failure in CI where provisioned — never a silent pass. |

**Fail-closed, binding (RT2-F4):** a consumer missing LibreOffice/veraPDF, or with no reachable XMLA/REST route, gets `overall_gate: PARTIAL` (missing legs enumerated), **never** `PASS`. This is enforced at the schema level — `fidelity-receipt.schema.json`'s `overall_gate` `allOf` clause forbids `PASS` when any leg reads `fail` / `not_captured` / `PARTIAL` / `PROBE_ERROR`. Every current `doctor.py` tool row carries an explicit degrade mode (e.g. `verapdf` absent → "PDF a11y leg → not_captured (PARTIAL, never PASS)"; `weasyprint` absent → "PDF/UA emit unavailable; ship HTML only + flag manual PDF step") — verified this session directly against `scripts/doctor.py`'s `TOOLS` table.

---

## 6. Cross-references

- Taxonomy, RSG/manifest schemas, the six-leg harness: [`core-architecture-spec.md`](core-architecture-spec.md).
- Full Power BI route contract (XMLA vs REST, auth, capacity tiers, period-coherence gating): [`powerbi-ingest-contract.md`](powerbi-ingest-contract.md).
- STRIDE / prompt-injection pass over every trust boundary: [`threat-model-stride.md`](threat-model-stride.md).
- The 85–95% classifier ceiling and how the tools above interact with it: [`inference-failure-modes.md`](inference-failure-modes.md).
- The accessibility floor these gates actually prove: [`wcag-floor.md`](wcag-floor.md).
- Manifest versioning/reuse mechanics: [`manifest-reuse-contract.md`](manifest-reuse-contract.md).
