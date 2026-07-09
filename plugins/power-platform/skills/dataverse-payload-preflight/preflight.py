#!/usr/bin/env python3
"""dataverse-payload-preflight — validate a Dataverse create/update payload against LIVE
entity metadata in ONE pass, so you never fix-one-field-and-retrigger.

Born from the Contoso assumption-rework retro (2026-06-24): create payloads failed one field at
a time across many human re-fires (empty lookup bind -> invalid option-set value -> undeclared
columns -> "Owner was not provided"). A single metadata-vs-payload sweep finds them all at once.

Two layers:
  * validate(payload, metadata) -> [violations]  — PURE, deterministic, fully unit-tested
    (no network). This is the value; feed it metadata from anywhere.
  * fetch_metadata(org, entity, token)           — best-effort live fetch from the Dataverse
    Web API EntityDefinitions (version-sensitive cast syntax — see SKILL [verify-at-use]).

CLI:
  DATAVERSE_TOKEN=... preflight.py --org https://x.crm.dynamics.com --entity contoso_balancesheet \\
                                   --payload payload.json
  # offline / testing: pass --metadata metadata.json instead of --org
Exit 0 = no ERROR-severity violations (warnings allowed); 3 = one or more errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# ── The pure validator (no network — this is what the gate tests) ────────────────
# `metadata` shape (assembled by fetch_metadata, or hand-authored for tests):
# {
#   "logical_name": "contoso_balancesheet", "entity_set": "contoso_balancesheets",
#   "primary_id": "contoso_balancesheetid", "ownership": "UserOwned",
#   "attributes": {
#     "<logical>": {"type": "String|Picklist|Lookup|...", "required": "None|ApplicationRequired|
#                    SystemRequired|Recommended", "valid_for_create": true,
#                    "options": [int,...],            # Picklist only
#                    "targets": ["account","contact"] # Lookup only (logical entity names)
#                  }, ...
#   }
# }

_BIND_RE = re.compile(r"^/(?P<set>[A-Za-z0-9_]+)\((?P<id>.*)\)$")
_REQUIRED = {"ApplicationRequired", "SystemRequired"}


def _strip_annotation(key: str) -> tuple[str, str | None]:
    """'contoso_AccountId@odata.bind' -> ('contoso_AccountId', 'odata.bind'); plain key -> (key, None)."""
    if "@" in key:
        base, ann = key.split("@", 1)
        return base, ann
    return key, None


def validate(payload: dict, metadata: dict) -> list[dict]:
    """Return ALL field-level violations of `payload` against `metadata`. One pass, no network.

    Each violation: {field, kind, severity ('error'|'warning'), detail, fix}.
    kinds: nonexistent-column, missing-required, invalid-option-set, malformed-lookup-bind,
           unknown-lookup-target, lookup-needs-bind, owner-not-provided.
    """
    v: list[dict] = []
    attrs: dict = metadata.get("attributes", {}) or {}
    # case-insensitive lookup of attribute logical names (payload casing varies)
    by_lower = {k.lower(): k for k in attrs}
    # entity-set -> logical, for validating @odata.bind targets we know about.
    # We only hold the logical target name here, and Dataverse EntitySetName
    # pluralization is irregular, so accept several forms to avoid a false
    # "unknown-lookup-target" warning: the raw/exact name (the "also accept exact"
    # the old comment promised but never added), the naive "+s", and the
    # consonant-"y" -> "-ies" rule (activity -> activities, company -> companies).
    # This is a warning-only check, so widening the accepted set only ever
    # suppresses false positives — it never blocks a genuinely-valid payload.
    known_target_sets: set[str] = set()
    for a in attrs.values():
        for t in a.get("targets", []) or []:
            tl = str(t).lower()
            known_target_sets.add(tl)          # raw / exact
            known_target_sets.add(tl + "s")    # naive plural
            if len(tl) > 1 and tl.endswith("y") and tl[-2] not in "aeiou":
                known_target_sets.add(tl[:-1] + "ies")

    present_logicals: set[str] = set()

    for key, value in payload.items():
        base, ann = _strip_annotation(key)
        low = base.lower()

        # 1. @odata.bind — a lookup set-by-reference
        if ann and ann.startswith("odata.bind"):
            m = _BIND_RE.match(str(value).strip()) if value is not None else None
            if not m or not m.group("id").strip():
                v.append({"field": key, "kind": "malformed-lookup-bind", "severity": "error",
                          "detail": f"bind value {value!r} is empty or not '/entityset(id)'",
                          "fix": "set '/<entityset>(<record-guid-or-alternate-key>)' with a non-empty id"})
                continue
            tset = m.group("set").lower()
            # mark the underlying lookup logical (best-effort: nav name often != logical; warn-only)
            if low in by_lower:
                present_logicals.add(by_lower[low])
            if known_target_sets and tset not in known_target_sets:
                v.append({"field": key, "kind": "unknown-lookup-target", "severity": "warning",
                          "detail": f"entity-set '/{m.group('set')}' is not a known target of this entity's lookups {sorted(known_target_sets)}",
                          "fix": "bind to a valid target entity-set, or verify the navigation-property name"})
            continue

        # other annotations (@odata.type, @odata.id…) are not data fields
        if ann:
            continue

        # 2. nonexistent column
        if low not in by_lower:
            # a raw value to a NAME that IS a lookup logical -> needs a bind, not a raw value
            v.append({"field": key, "kind": "nonexistent-column", "severity": "error",
                      "detail": f"'{base}' is not an attribute of {metadata.get('logical_name','?')}",
                      "fix": "remove it, or correct the logical name (verify against EntityDefinitions/Attributes)"})
            continue

        logical = by_lower[low]
        meta = attrs[logical]
        present_logicals.add(logical)

        # 3. a Lookup attribute given a RAW value instead of <nav>@odata.bind
        if meta.get("type") == "Lookup":
            v.append({"field": key, "kind": "lookup-needs-bind", "severity": "error",
                      "detail": f"'{logical}' is a Lookup; a raw value won't bind it",
                      "fix": f"use '<NavigationProperty>@odata.bind': '/<entityset>(<id>)' instead of '{base}': <value>"})
            continue

        # 4. invalid option-set value
        if meta.get("type") == "Picklist" and "options" in meta and value is not None:
            try:
                ival = int(value)
            except (TypeError, ValueError):
                ival = None
            if ival is None or ival not in meta["options"]:
                v.append({"field": key, "kind": "invalid-option-set", "severity": "error",
                          "detail": f"value {value!r} is not in {logical}'s option set {meta['options']}",
                          "fix": "use a declared option value (query the attribute's OptionSet)"})

    # 5. missing required (create context)
    for logical, meta in attrs.items():
        if meta.get("required") in _REQUIRED and meta.get("valid_for_create", True):
            if logical == metadata.get("primary_id"):
                continue  # the id is server-assigned on create
            if logical not in present_logicals:
                v.append({"field": logical, "kind": "missing-required", "severity": "error",
                          "detail": f"required attribute '{logical}' (RequiredLevel={meta.get('required')}) is absent",
                          "fix": "add it to the payload (or its <nav>@odata.bind for a required lookup)"})

    # 6. owner-not-provided on a user/team-owned entity (the SPN-create trap)
    if metadata.get("ownership") in ("UserOwned", "TeamOwned"):
        has_owner = any(_strip_annotation(k)[0].lower() == "ownerid" for k in payload)
        if not has_owner:
            v.append({"field": "ownerid", "kind": "owner-not-provided", "severity": "warning",
                      "detail": f"{metadata.get('logical_name','?')} is {metadata['ownership']}; an application-user (SPN) create often needs an explicit owner",
                      "fix": "set 'ownerid@odata.bind': '/systemusers(<id>)' (or /teams(<id>)) — verify the SPN holds prvAssign/read on the target"})
    return v


# ── Best-effort live metadata fetch (version-sensitive — verify at use) ───────────
def fetch_metadata(org: str, entity: str, token: str) -> dict:
    """Assemble the metadata dict from the Dataverse Web API. Best-effort + fail-safe: a failed
    sub-query degrades that check class (with a note on stderr) rather than crashing.

    NOTE [verify-at-use]: the metadata cast syntax (…/Attributes/Microsoft.Dynamics.CRM.<Type>
    AttributeMetadata, OptionSet expand) is version-sensitive — confirm against your org's
    $metadata if a query 400s. This function is intentionally NOT exercised by the gate (no live
    org); the gate tests validate() against fixtures.
    """
    import urllib.request

    base = org.rstrip("/") + "/api/data/v9.2"
    hdr = {"Authorization": f"Bearer {token}", "Accept": "application/json",
           "OData-MaxVersion": "4.0", "OData-Version": "4.0"}

    def get(url):
        req = urllib.request.Request(url, headers=hdr)
        with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (trusted org URL + bearer)
            return json.loads(r.read().decode("utf-8"))

    md: dict = {"logical_name": entity, "attributes": {}}
    try:
        ent = get(f"{base}/EntityDefinitions(LogicalName='{entity}')?$select=LogicalName,EntitySetName,PrimaryIdAttribute,OwnershipType")
        md["entity_set"] = ent.get("EntitySetName")
        md["primary_id"] = ent.get("PrimaryIdAttribute")
        md["ownership"] = ent.get("OwnershipType")
    except Exception as e:  # noqa: BLE001
        print(f"[preflight] entity metadata fetch failed ({e}); ownership/primary-id checks skipped", file=sys.stderr)

    try:
        for a in get(f"{base}/EntityDefinitions(LogicalName='{entity}')/Attributes?$select=LogicalName,RequiredLevel,AttributeType,IsValidForCreate").get("value", []):
            req = a.get("RequiredLevel", {})
            md["attributes"][a["LogicalName"]] = {
                "type": a.get("AttributeType"),
                "required": req.get("Value") if isinstance(req, dict) else req,
                "valid_for_create": a.get("IsValidForCreate", True),
            }
    except Exception as e:  # noqa: BLE001
        print(f"[preflight] attribute fetch failed ({e}); column/required checks degraded", file=sys.stderr)

    # Picklist options + Lookup targets — version-sensitive casts; degrade quietly.
    try:
        for a in get(f"{base}/EntityDefinitions(LogicalName='{entity}')/Attributes/Microsoft.Dynamics.CRM.PicklistAttributeMetadata?$select=LogicalName&$expand=OptionSet($select=Options)").get("value", []):
            opts = (a.get("OptionSet") or {}).get("Options", [])
            md["attributes"].setdefault(a["LogicalName"], {})["options"] = [o.get("Value") for o in opts if o.get("Value") is not None]
    except Exception as e:  # noqa: BLE001
        print(f"[preflight] option-set fetch failed ({e}); invalid-option-set check skipped", file=sys.stderr)
    try:
        for a in get(f"{base}/EntityDefinitions(LogicalName='{entity}')/Attributes/Microsoft.Dynamics.CRM.LookupAttributeMetadata?$select=LogicalName,Targets").get("value", []):
            md["attributes"].setdefault(a["LogicalName"], {})["targets"] = a.get("Targets", [])
    except Exception as e:  # noqa: BLE001
        print(f"[preflight] lookup-target fetch failed ({e}); unknown-target check skipped", file=sys.stderr)
    return md


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--entity", required=True, help="target entity logical name (e.g. contoso_balancesheet)")
    ap.add_argument("--payload", required=True, help="payload JSON file, or '-' for stdin")
    ap.add_argument("--org", help="Dataverse org URL (live metadata fetch); needs DATAVERSE_TOKEN env")
    ap.add_argument("--metadata", help="metadata JSON file (offline; skips the live fetch)")
    a = ap.parse_args()

    payload = json.load(sys.stdin if a.payload == "-" else open(a.payload, encoding="utf-8"))
    if a.metadata:
        metadata = json.load(open(a.metadata, encoding="utf-8"))
    elif a.org:
        import os
        tok = os.environ.get("DATAVERSE_TOKEN")
        if not tok:
            print("[preflight] --org given but DATAVERSE_TOKEN env is unset", file=sys.stderr)
            return 2
        metadata = fetch_metadata(a.org, a.entity, tok)
    else:
        print("[preflight] provide --metadata <file> or --org <url>", file=sys.stderr)
        return 2
    metadata.setdefault("logical_name", a.entity)

    violations = validate(payload, metadata)
    errors = [x for x in violations if x["severity"] == "error"]
    print(json.dumps({"entity": a.entity, "ok": not errors,
                      "error_count": len(errors), "warning_count": len(violations) - len(errors),
                      "violations": violations}, indent=2))
    if violations:
        print(f"\n[preflight] {len(errors)} error(s), {len(violations)-len(errors)} warning(s) — fix all in one pass:", file=sys.stderr)
        for x in violations:
            print(f"  [{x['severity']}] {x['field']}: {x['detail']} -> {x['fix']}", file=sys.stderr)
    else:
        print("[preflight] clean — payload matches live metadata.", file=sys.stderr)
    return 3 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
