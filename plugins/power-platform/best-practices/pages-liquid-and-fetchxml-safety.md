# Never concatenate request input into FetchXML/Liquid, and treat hiding as cosmetic

**Status:** Absolute rule — string-built FetchXML from `request` parameters is an injection vector on a public site.

**Domain:** Power Pages / Liquid / security

**Applies to:** `power-platform`

---

## Why this exists

Liquid is the Power Pages templating layer, and `{% fetchxml %}` runs queries against Dataverse from the page. Two patterns turn it dangerous. First, building a FetchXML string by **concatenating `request.params`** lets a visitor inject filter conditions, broaden a query, or read rows the page never intended to expose — the public-site equivalent of SQL injection. Second, makers use Liquid `{% if %}` or CSS to "hide" sensitive content, but the content inside a passed `{% if %}` is still **rendered into the page source** the browser receives — hiding is cosmetic, not security. The `power-pages-engineer` agent flags "Liquid with raw FetchXML strings concatenated from query parameters" as an explicit anti-pattern, and the permissions skill states "hiding ≠ securing." Data protection must live at the **table-permission** layer; Liquid only narrows what an already-authorized user *sees*.

## How to apply

Bind request input through Liquid objects and filter server-side via table permissions — don't string-build the query. Use the `editable`/`entitylist` objects and parameterized FetchXML rather than concatenation:

```liquid
{# DON'T — request input concatenated straight into FetchXML (injection): #}
{% fetchxml q %}
  <fetch><entity name="mc_order">
    <filter><condition attribute="mc_status" operator="eq"
      value="{{ request.params.status }}" /></filter>   {# attacker controls this #}
  </entity></fetch>
{% endfetchxml %}

{# DO — sanitize/whitelist the input, and rely on table permissions for row scope: #}
{% assign status = request.params.status | default: 'active' %}
{% if status != 'active' and status != 'closed' %}{% assign status = 'active' %}{% endif %}
{% fetchxml q %}
  <fetch><entity name="mc_order">
    <filter><condition attribute="mc_status" operator="eq" value="{{ status }}" /></filter>
  </entity></fetch>
{% endfetchxml %}
{# Table permission (Contact scope) already restricts mc_order to the signed-in contact's rows. #}
```

**Do:**
- Whitelist/validate any `request.params` value before it reaches FetchXML; coerce to a known set.
- Let **table permissions** (Contact/Account/Self scope) enforce *which rows* — Liquid filters are UX, not a security boundary.
- Use `{% include %}` web templates for reuse instead of copy-pasting Liquid across pages.
- Minimize custom JS on a public site — every line is an attack surface; security-relevant logic must be server-side.

**Don't:**
- Concatenate `request.params`, route values, or cookies directly into a FetchXML `value=`.
- Treat `{% if user.roles contains ... %}` as protecting the markup inside it — it's in the source for everyone who passes the check.
- Hard-code contact/account GUIDs in Liquid (§3 #11) — look up by the current `user`/`contact` object.

## Edge cases / when the rule does NOT apply

- **Trusted server-side values** already scoped by the platform (`{{ user.id }}`, `{{ request.path }}`) are safe to bind — the risk is *attacker-controlled* input.
- **`entitylist` / `entityform`** components handle their own parameterization and view-based filtering — prefer them over hand-written FetchXML where they fit.
- Liquid `{% if %}` is the **correct** tool for genuine UX variation (showing a premium banner) — just never as the only thing standing between a user and sensitive *data*.

## See also

- [`pages-table-permissions-before-publish.md`](./pages-table-permissions-before-publish.md) — the data-layer security that Liquid filtering must not substitute for
- [`../knowledge/bi-pages-copilot-decision-trees.md`](../knowledge/bi-pages-copilot-decision-trees.md) — `## Decision Tree: Power Pages — Granting a portal user access to a row`
- [`../skills/power-pages-permissions/SKILL.md`](../skills/power-pages-permissions/SKILL.md) — §9 "Liquid permission-aware rendering" ("Liquid hides UI; it does not secure data")
- [`../knowledge/power-pages-2026.md`](../knowledge/power-pages-2026.md) — Liquid + Web API surface, React SPA option
- [`../agents/power-pages-engineer.md`](../agents/power-pages-engineer.md) — owner

## Provenance

Grounded in [Liquid in Power Pages](https://learn.microsoft.com/power-pages/configure/liquid/liquid-overview), [fetchxml Liquid tag](https://learn.microsoft.com/power-pages/configure/liquid/liquid-tags), and the `power-pages-engineer` agent anti-pattern list ("raw FetchXML strings concatenated from query parameters — injection risk") (retrieved 2026-05-30).

---

_Last reviewed: 2026-05-30 by `claude`_
