# Building a form builder people can use without help (2026)

> **Retrieved:** 2026-10-26. Product behaviour is quoted from each product's own docs on that date. Anything seen
> only through a search summary is marked `[via snippet]`. Library sizes were **measured** (esbuild 0.25.0
> `--bundle --minify --format=esm`, then `gzip -9`). Recommendations not stated by any source are marked
> `[inference]`. Re-verify versions, prices and limits at use.
>
> **Scope.** This is the *authoring tool*: the builder an owner uses to create a form. The server half of a
> submission (honeypots, double-submit guards, telemetry, the platform-selection axes) is
> [`forms-engineering`](../../forms-engineering/CLAUDE.md)'s and is not restated here. How a builder *looks and
> feels* across forms, contact cards and Wallet passes is [`visual-builder-ux-2026.md`](visual-builder-ux-2026.md).
> The procedure is the [`form-builder`](../skills/form-builder/SKILL.md) skill.

## 0. The short version

1. **Own a typed definition model; compile a JSON Schema from it for type checks only.** JSON Schema validates
   data and cannot express visibility, pages or flow (its `if/then` and `dependentRequired` are data
   constraints). JSON Forms and react-jsonschema-form split a data schema from a UI schema for the same reason.
2. **Draft, then immutable versions.** One autosaved draft per form; publish copies the whole definition into an
   append-only version row; every submission stores `form_version_id` and answers keyed by **stable field ids**
   (Form.io's model: full copies per revision, `_fvid` on each submission, a single replace-on-save draft).
3. **Logic is a typed condition tree, not code.** `{connector: and|or, items: [...]}` with typed operands (field,
   URL param, variable, constant), as in Formbricks' current zod types. Evaluate it with your own small
   allow-listed interpreter, the **same code** on the client (for UX) and the server (for truth).
4. **Validate the logic graph on every save and block publish on errors** — cycles, unreachable pages, dangling
   targets, formula cycles.
5. **A document canvas for owners, a graph and JSON view for power users** — two disclosure levels, no more.
6. **One renderer** for the live preview, the published form and the one-question-at-a-time mode.
7. **Money is computed on the server from the published version**, never taken from the client.

## 1. Schema models compared

| Model | Pages / layout | Conditional rule shape | Calculations | Versioning while submissions exist |
|---|---|---|---|---|
| JSON Forms | Vertical/Horizontal layouts, Group, Categorization (tabs) | `rule: {effect: HIDE\|SHOW\|DISABLE\|ENABLE, condition: {scope, schema}}` — the condition is itself a JSON Schema | none built in | not addressed |
| react-jsonschema-form | ordering only (`ui:order`) | `dependencies`, dynamic `oneOf` | none | not addressed |
| SurveyJS | pages, nestable panels | **string expressions** `"visibleIf": "{age} >= 16"`, `enableIf`, `requiredIf`, triggers | `calculatedValues` | not addressed |
| Form.io | panels, wizard | simple conditions, **JSON Logic, or author JavaScript** (`show = …`) | JavaScript `value = …` | **full-copy revisions, `_fvid` on submissions, one replace-on-save draft** |
| Formbricks (open source) | blocks + endings | typed tree, ~30 named operators, typed operands, `logicFallback` per block | `calculate` actions on declared variables | not studied |
| Tally | blocks; question = title block + input block sharing a group id | "When … Then …" logic blocks in the flow | calculated fields | `PATCH` must resend **all** blocks |
| Typeform | one question at a time; groups | `logic[].actions[]` with `jump/add/subtract/…`, `condition {op, vars}` | `variables {score, price}` | **a `PUT` that omits a field deletes its results** |
| Google Forms API | `pageBreakItem` sections | per-option `goToAction` / `goToSectionId`, radio and dropdown only | quiz grading | opaque `revisionId`; `isPublished` and `isAcceptingResponses` are separate flags |

**What the comparison says** `[inference]`:

- Two lineages. *Data-schema-first* (JSON Forms, RJSF) is strong on validation and weak on flow. *Questionnaire-first*
  (SurveyJS, Typeform, Formbricks, Tally, Google) models pages, flow and variables. A small-business builder with
  steps, logic and payments belongs to the second, with a derived JSON Schema for the server's type check.
- Typed condition trees map one-to-one onto a sentence-builder UI: each leaf is a "[field] [operator] [value]" row,
  and the operator list is filtered by the field's type (Formbricks: single-select gets equals / not equals / one
  of / is submitted; text adds contains / starts with / ends with).
- Stable ids everywhere (Typeform `ref`, Tally `uuid`, Google `itemId`). Labels are never keys — Form.io's docs say
  conditions reference fields "by their Property Name … not their Label".
- i18n converged independently on `{default: "…", <locale>: "…"}` at every string (SurveyJS, Formbricks).
- Separate *published* from *accepting responses* (Google). A closed form, a scheduled close and a response limit
  are not the same as unpublishing.

## 2. A recommended definition shape `[inference]`

```ts
type I18n = { default: string; [locale: string]: string };

interface FormDefinition {
  formatVersion: 1;                          // envelope version; write a migrator per bump
  locales: { default: string; enabled: string[] };
  settings: { display: 'classic' | 'conversational'; progress: 'steps' | 'bar' | 'none';
              reviewStep: boolean; submitLabel: I18n };
  theme: { source: 'site'; overrides?: Record<string, string> };
  pages: Page[];                             // ordered; the unit of navigation and branching
  fields: Field[];                           // flat, stable ids; membership via Page.fieldIds
  params: UrlParam[];                        // allow-listed URL / hidden params (utm_source, ref…)
  variables: Variable[];                     // declarative formulas (score, price, total)
  endings: Ending[];                         // thank-you screens / redirects; can be branch targets
  outputs: { email?: EmailOut[]; webhooks?: WebhookOut[]; crm?: FieldMap; payment?: PaymentCfg };
}
interface Page  { id: string; title?: I18n; fieldIds: string[]; visibleWhen?: Cond;
                  branches?: { id: string; when: Cond; goTo: string }[]; fallback?: string }
interface Field { id: string; key: string; type: FieldType; label: I18n; hint?: I18n;
                  required: boolean; requiredWhen?: Cond; visibleWhen?: Cond; archived?: boolean;
                  options?: { id: string; value: string; label: I18n; exclusive?: boolean }[];
                  props: Record<string, unknown>; validation?: Rule[] }
type Operand = { kind: 'field'; id: string } | { kind: 'param'; name: string }
             | { kind: 'var'; id: string }  | { kind: 'const'; value: string | number | boolean | string[] };
type Cond = { connector: 'and' | 'or'; items: (Leaf | Cond)[] };
type Leaf = { left: Operand; op: Operator; right?: Operand };
```

- **Field-level `visibleWhen` / `requiredWhen`** give the inspector one sentence: "Show this question only
  when…". Separate show *and* hide rules make authors reason about defaults (Tally: "Showing blocks requires
  hiding them first").
- **Page branches with a fallback** are what a flow graph draws.
- **Declarative variable formulas, not imperative add/subtract actions.** A formula's value does not depend on
  which path fired, so the server can recompute it exactly — required for a payment amount.
- **Evaluation order, identical on client and server:** params → answers → variables (topological) → page and
  field visibility → required → routing. On submit the server re-runs all of it, drops answers to hidden fields,
  enforces required only on visible ones, and recomputes every variable.

## 3. Editing a published form

| Edit | Classification | Builder behaviour `[inference]` |
|---|---|---|
| Typo, label, help text, theme | safe | new version silently; old submissions keep theirs |
| Add a field or option | safe | new ids; old submissions simply have no value |
| Reorder fields or options | safe when answers are keyed by id | warn only for position-keyed exports |
| Delete a field or option that has data | **archive** | `archived: true`, hidden from new respondents, still a column in the inbox |
| Change a field's type when it has data | **fork** | new field id; old one archived; confirm: "Existing answers stay under '<label> (old)'" |
| Change an option's stored value | disallowed | labels editable; values immutable once published |
| Change consent or legal text | new version | the submission's version proves which text was shown (ICO: record "the consent statement… and version numbers") |

Typeform's help lists deleting a question or choice, changing a type, and reordering choices as edits that can
affect collected results `[via snippet]`; its developer docs state a `PUT` deletes results for omitted fields.

## 4. Field catalog

Phase **P1** is the first release; **P2/P3** follow. Autocomplete tokens are WHATWG autofill names; `inputmode`
values are MDN's.

| Field | Semantics | `autocomplete` | Note | Ph |
|---|---|---|---|---|
| Short / long text | `input type=text` / `textarea` | by purpose | visible label + hint; **never a placeholder as the label** (GOV.UK) | P1 |
| Name | one "Full name" or given + family | `name` / `given-name` / `family-name` | accept every character (GOV.UK names pattern) | P1 |
| Email | `type=email` | `email` | typo-domain **warning**, not a block; no confirm-email field | P1 |
| Phone | `type=tel` | `tel` | accept spaces, brackets, dashes; **no input mask**; normalise to E.164 on the server. libphonenumber-js is 35.8 KB gz (`/min`) to 49.9 KB (`/max`) — lazy-load it or validate server-side | P1 |
| Number | `type=text` + `inputmode=numeric/decimal` | — | **avoid `type=number`** (GOV.UK) | P1 |
| Date (memorable) | day / month / year inputs | `bday-*` for birthdays | GOV.UK date input | P1 |
| Single choice | radios in `fieldset`/`legend` | — | don't pre-select; offer "None / I don't know" | P1 |
| Multiple choice | checkboxes in `fieldset` | — | "Select all that apply"; exclusive "None" after an "or" divider | P1 |
| Dropdown | `select`, combobox for long lists | e.g. `country-name` | a last resort (GOV.UK); simple mode suggests radios at ≤ 7 options `[inference]` | P1 |
| Yes / No | two radios | — | an explicit "No" beats a lone checkbox `[inference]` | P1 |
| Rating / NPS / scale | radio group | — | each radio named ("4 of 5"); label the endpoints | P1 |
| Website | `type=url` | `url` | — | P1 |
| Consent | one **unticked** checkbox per purpose | — | ICO: no pre-ticked boxes; record who, when, what text, which version | P1 |
| Hidden / URL param | not rendered | — | allow-listed lowercase names (Typeform), length cap; **untrusted input** | P1 |
| Statement, heading, image, video, divider | content | — | images need alt text | P1 |
| Page break | step boundary | — | the page title feeds `<title>` (WAI multi-page) | P1 |
| Captcha | challenge widget | — | the builder only toggles it — mechanics are core's ([`cloudflare-who-gets-in.md`](../../ravenclaude-core/knowledge/concepts/cloudflare-who-gets-in.md)) | P1 |
| Scheduling date, time, range | picker **plus** typed entry | — | "Never make a calendar control that depends on JavaScript as the only input option" (GOV.UK) | P2 |
| Currency | text + prefix | — | store minor units; prefixes are not read out, so repeat the currency in the label | P2 |
| Image choice | radios/checkboxes with images | — | alt text required; never derived from the file name (Formbricks) | P2 |
| File upload | `type=file` with `accept`, `multiple` | — | specific errors ("must be smaller than 2MB", "is empty"); handling rules: [core security rules](../../ravenclaude-core/rules/security.md) | P2 |
| Signature | canvas (signature_pad 4.7 KB gz) **plus a typed-name option** | — | WCAG 2.5.1: confirming identity need not be path-based | P2 |
| Address | multi-field + lookup + manual fallback | `address-line1`, `address-level2`, `postal-code`, `country-name` | always a manual route (GOV.UK addresses) | P2 |
| Calculated value | not an input | — | server recomputes | P2 |
| Payment | provider's hosted element or redirect | provider's | §6 | P2 |
| Ranking | list with Up/Down buttons, drag optional | — | APG rearrangeable listbox; Typeform staff called its ranking block a hard barrier `[via snippet]` | P3 |
| Matrix / grid | a radio group per row | — | stack rows on mobile | P3 |
| Repeatable group | "add another" loop | — | one item per loop, summary with Change/Remove, state the maximum (DWP/MoJ patterns) `[via snippet]` | P3 |
| Slider | native `range` + a numeric box | — | add typed entry for precision | P3 |

Fillout lists 51 types and tells API consumers to "discard fields with unknown types"; scope the first release
to about fifteen.

## 5. Logic

### 5.1 Capabilities

| Capability | Prior art | Model |
|---|---|---|
| Show / hide a field | SurveyJS `visibleIf`, JSON Forms `rule`, Tally show/hide | `field.visibleWhen` |
| Skip / branch to a page | Formbricks jump + `logicFallback`, Typeform `jump`, Google `goToSectionId` | `page.branches[]` + `fallback`, evaluated on Next |
| Required-if | SurveyJS `requiredIf`, Formbricks `requireAnswer` | `field.requiredWhen` |
| Score / price / total | Typeform variables, Formbricks `calculate`, SurveyJS `calculatedValues`, Fillout `calculations` | declarative `variables[].formula` |
| Piping ("Hi {name}") | SurveyJS `{firstName}`, Tally and Typeform `@` | `{{field_id}}` tokens in strings, shown as chips, rendered as escaped text |
| Prefill from URL | Typeform URL parameters, Tally hidden fields | `params[]` allow-list |
| End early / redirect | SurveyJS `complete`, Tally redirect | branch targets can be `endings[]` |

### 5.2 Presenting logic to non-technical owners

- **Sentence builder** (Tally, Formbricks): "When [all/any] … Then [show / hide / jump to / require]", with a
  fallback line "All other answers continue to…". Rules are checked top to bottom; first match wins.
- **Flow graph** (Fillout page logic, Typeform Logic Map `[via snippet]`): drag from a page to its target, then
  set the condition. Draw it from the same data; never make it the only way to edit.
- **The scaling trap:** a Tally user noted jump logic over 22 checkbox options would need about 4.5 million
  combinations `[via snippet]`. Offer set operators (`includesOneOf`, `includesAllOf`) and page-level visibility
  instead of forcing jumps.
- Simple mode puts one sentence in the field inspector ("Show this question when…") and one in page settings
  ("After this page, go to…"). Advanced mode adds nested groups and the graph. `[inference]`

### 5.3 Checks on every save (block publish on errors)

Formbricks ships, in source: cycle detection (DFS with a recursion stack over jump and fallback edges), "jump
destination no longer exists", "cannot jump to the current block", "multiple jump actions are not allowed", and
a fallback without logic. Add `[inference]`: unreachable pages (BFS from the first page), variable dependency
cycles (topological sort), forward references (a condition reading a field later on the path is always empty),
dangling operands after an archive, and a required-but-hidden hint.

### 5.4 Evaluation safety (multi-tenant)

"Rules as data" is not automatically safe. json-logic-js had prototype pollution leading to remote code
execution before 2.0.0 (GHSA-m9hw-7xfv-wqg7) and command injection fixed in 2.0.1 (CVE-2021-4329); expr-eval's
CVE-2025-12735 (CVSS 9.8) affects every version through 2.0.2 (OSV, 2026-10-26). Form.io runs author JavaScript,
which is unacceptable for tenant-authored forms. `[inference]`: write a ~200-line interpreter over a closed
operator allow-list (comparison, set, string, date, arithmetic, `if`, `round`, `min`, `max`); read values only
from a frozen `Object.create(null)` context; no property access by name, no method calls; cap depth and node
count at save; fuzz it with `__proto__` and `constructor` keys; run the identical module on client and server.

## 6. Outputs and payments

- **Inbox:** one table per form across versions, columns keyed by field id (archived fields stay as greyed
  columns), a version badge per row, and a detail view that renders a submission **in its captured version**
  (Form.io's "original revision" mode).
- **CSV export:** neutralise cells starting with `=`, `+`, `-`, `@`, tab or CR and quote every cell (OWASP CSV
  injection); page the export rather than loading every row.
- **Webhooks: implement the Standard Webhooks spec.** Headers `webhook-id` (the idempotency key, constant across
  retries), `webhook-timestamp`, `webhook-signature`; sign `msg_id.timestamp.payload` with HMAC-SHA256 (`v1,`);
  space-separated signatures allow key rotation; `2xx` is success and `3xx` is failure; disable the endpoint on
  `410`; retry for about three days with backoff; a delivery log with manual replay. The consumer picks the URL,
  so guard against SSRF: `https:` only, no IP literals or private, loopback or link-local hosts, no redirects,
  capped response reads `[inference]`. Verifying *inbound* webhooks is
  [`web-commerce`'s webhook-hardening](../../web-commerce/skills/webhook-hardening/SKILL.md).
- **Email:** the owner notification goes to a verified address; respondent confirmation is opt-in and needs an
  email field; never set Reply-To from respondent input without validating it `[inference]`.
- **CRM mapping:** map by field `key`, never by label, so relabelling never breaks the integration; the mapping
  belongs to the published version `[inference]`.
- **Payments.** Card data collected inside the provider's hosted iframe (hosted checkout or a payment element)
  keeps the merchant at PCI **SAQ A**; a direct API integration is SAQ D (Stripe security guide). Since
  2025-03-31 SAQ A drops requirements 6.4.3, 11.6.1 and 12.3.1 but adds an eligibility criterion that the site
  "is not susceptible to attacks from scripts" (PCI SSC). Who attests that criterion when a platform hosts the
  page for a tenant is `[unverified — ask a QSA]`. The amount: the payment field points at a money variable; on
  submit the server loads the **published version**, re-evaluates variables from the posted answers, rejects a
  mismatched client amount, and fulfils from the provider's webhook, not the client callback. Stripe warns that
  putting its Payment Element inside another iframe breaks redirect-based methods, so an iframe-embedded form
  falls back to hosted checkout. Platform shape: Stripe Connect direct charges ("works best for platforms that
  provide software as a service").
- **Uploads:** route the bytes through the upload rules in
  [`ravenclaude-core/rules/security.md`](../../ravenclaude-core/rules/security.md). On object storage with
  presigned PUTs, upload to a quarantine prefix, then verify size and magic bytes from a storage event before
  promoting the file `[inference]`.

## 7. The published form, as it drives builder defaults

- **One thing per page** suits low-confidence users and mobile, and handles errors, branches and saved progress
  better; the costs are page loads and losing sight of all the questions (GDS, 2015). Default conversational
  forms to one question per page and classic forms to grouped pages, with a per-page override `[inference]`.
- **Error summary** at the top of `main`, focused, `Error:` prefixed to the `<title>`, each entry linking to its
  field, wording matching the inline message (GOV.UK). So every validation rule needs an owner-editable,
  field-specific message with a good default.
- **Conditional reveal** inline only for one simple follow-up; anything bigger goes on the next page (GOV.UK
  radios and checkboxes guidance).
- **Progress:** "Step 2 of 4: …" in `<title>`, an ordered list step indicator, data kept when going back (WAI);
  with branching, omit the total or update it.
- **Check your answers** before submit for small and medium forms (GOV.UK).
- **Conversational mode:** auto-advance only on single-choice questions and never past an error; a visible Back;
  a "Show all questions" switch on the first screen (SurveyMonkey has a Screen Reader Mode toggle; Typeform
  community threads report screen-reader failures `[via snippet]`).
- **Payload:** the base renderer is vanilla; the logic interpreter (about 2 KB) always ships; phone validation,
  signature, address lookup and the payment script load only when the form contains them.

## Sources (retrieved 2026-10-26)

JSON Forms rules and layouts — jsonforms.io/docs/uischema · RJSF uiSchema and dependencies —
rjsf-team.github.io/react-jsonschema-form · JSON Schema conditionals —
json-schema.org/understanding-json-schema/reference/conditionals · SurveyJS conditional logic, localization,
Creator overview — surveyjs.io · Form.io logic and form revisions — help.form.io, form.io/features/form-revisions
· JSON Logic — jsonlogic.com · Formbricks `packages/types/surveys/{logic,types,blocks-validation,elements}.ts`
(GitHub, main) and conditional-logic docs · Tally help (conditional logic, keyboard shortcuts, create a form,
hidden fields) and developer docs · Typeform create/update form and theme API references; help articles
`[via snippet]` · Fillout question types, page logic, form metadata API · Jotform cards vs classic `[via snippet]`
· Google Forms API `v1/forms` · SurveyMonkey one-question-at-a-time · GOV.UK Design System (question pages,
addresses, dates, telephone numbers, email addresses, names, check answers, error summary, radios, checkboxes,
select, text input, file upload) · GDS "One thing per page" (2015) · WAI forms tutorials (multi-page, grouping) ·
WCAG 2.2 Understanding 1.4.3, 1.4.11, 2.5.1, 2.5.7 · WAI-ARIA APG rearrangeable listbox · WHATWG autofill · MDN
`inputmode` · Nielsen Norman Group, progressive disclosure · ICO consent guidance · OSV advisories
GHSA-jc85-fpwf-qm7x, GHSA-67j4-2mh6-8627, GHSA-m9hw-7xfv-wqg7 · Stripe security guide, online payments, Connect
charges, deferred-intent payment, webhooks, Address Element · PCI SSC SAQ A update blog · Standard Webhooks spec
(GitHub) · Cloudflare Queues retries, R2 presigned URLs and event notifications, WAF malicious uploads, Workers
limits, Email Service, D1 limits · OWASP CSV injection.
