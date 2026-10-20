#!/usr/bin/env python3
"""openapi_diff.py - a zero-dependency OpenAPI breaking-change classifier.

Compares two OpenAPI documents (an OLD/baseline and a NEW/candidate) and
classifies every difference as BREAKING, ADDITIVE, or INFO, using the same
rules as knowledge/api-versioning-and-evolution-decision-trees.md. It answers
the one question that actually causes API outages: "is THIS change breaking,
from the strictest consumer's point of view?" -- which a single-spec linter
(Spectral, vacuum) cannot answer, because it needs the BEFORE and AFTER.

What it checks (producer/consumer asymmetry -- judged from a strict client):

  BREAKING
    - a removed path, operation, or response field
    - a removed or newly-REQUIRED request property (tightening input)
    - a removed response status code
    - a removed or newly-required operation parameter
    - a changed type on a request or response property
    - a value REMOVED from a request or response enum (narrowing)
    - a value ADDED to a CLOSED response enum (the misclassified case --
      strict SDKs throw on an unknown variant; suppress with the documented
      x-extensible-enum vendor extension when the enum is genuinely open)

  ADDITIVE (safe -- no version bump)
    - a new path or operation
    - a new OPTIONAL request property
    - a new response field / response status code
    - a value added to a response enum marked x-extensible-enum
    - a new optional parameter

  INFO
    - description / summary / example churn, openapi version field changes

This is a HEURISTIC linter, not a proof: it walks the documents structurally.
Local '#/...' $refs are dereferenced in both documents first (with a cycle
guard), allOf members are flattened, oneOf/anyOf variants are paired by
position, and items / additionalProperties / path-item-level parameters are
walked. An external or unresolvable $ref cannot be diffed, so it is reported as
a BREAKING 'UNSURE: unresolved $ref' finding. Treat a clean run as "no breaking
change DETECTED", not "provably none" -- and treat an UNSURE as breaking (the
cost of a false 'additive' is a production outage).

Input format: JSON OpenAPI documents (3.0 / 3.1 / 3.2). YAML specs are the
common authoring form but stdlib has no YAML parser, so convert first and keep
this tool dependency-free:

    npx --yes js-yaml openapi.yaml > openapi.json     # or: yq -o=json ...

Stdlib only (json, argparse, sys); runs anywhere Python 3.8+ is present.

Examples
--------
  python3 openapi_diff.py old.json new.json
  python3 openapi_diff.py old.json new.json --format json
  python3 openapi_diff.py old.json new.json && echo "no breaking change"
  # exits 1 when any BREAKING change is found -- wire it into CI as a gate.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any
from urllib.parse import unquote

HTTP_METHODS = ("get", "put", "post", "delete", "patch", "options", "head", "trace")
EXTENSIBLE_ENUM_KEY = "x-extensible-enum"


class Finding:
    """One classified difference."""

    BREAKING = "BREAKING"
    ADDITIVE = "ADDITIVE"
    INFO = "INFO"

    def __init__(self, level: str, where: str, message: str) -> None:
        self.level = level
        self.where = where
        self.message = message

    def as_dict(self) -> dict[str, str]:
        return {"level": self.level, "where": self.where, "message": self.message}


def _load(path: str) -> dict[str, Any]:
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"error: file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(
            f"error: {path} is not valid JSON ({exc}).\n"
            "Convert a YAML spec first: npx --yes js-yaml spec.yaml > spec.json"
        )
    if not isinstance(data, dict):
        raise SystemExit(f"error: {path} is not an OpenAPI object")
    return data


_MISSING = object()


def _resolve_pointer(root: Any, ref: str) -> Any:
    """Resolve a local '#/a/b' JSON pointer against root, or return _MISSING."""
    if not ref.startswith("#"):
        return _MISSING  # external document or URL
    pointer = ref[1:]
    if pointer == "":
        return root
    if not pointer.startswith("/"):
        return _MISSING
    node = root
    for part in pointer[1:].split("/"):
        part = unquote(part).replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and part in node:
            node = node[part]
        elif isinstance(node, list) and part.isdigit() and int(part) < len(node):
            node = node[int(part)]
        else:
            return _MISSING
    return node


class _Dereferencer:
    """Inline local $refs, remembering the ones that cannot be followed."""

    def __init__(self, root: Any) -> None:
        self.root = root
        self.stack: list[str] = []  # refs being expanded right now (cycle guard)
        self.memo: dict[str, Any] = {}
        self.cycle_hits = 0
        self.unresolved: dict[str, str] = {}  # ref -> first location seen

    def walk(self, node: Any, where: str) -> Any:
        if isinstance(node, list):
            return [self.walk(item, f"{where}[{i}]") for i, item in enumerate(node)]
        if not isinstance(node, dict):
            return node
        ref = node.get("$ref")
        if isinstance(ref, str):
            target = self.expand(ref, where)
            extra = {k: self.walk(v, f"{where}.{k}") for k, v in node.items() if k != "$ref"}
            return {**target, **extra} if isinstance(target, dict) and extra else target
        return {k: self.walk(v, f"{where}.{k}") for k, v in node.items()}

    def expand(self, ref: str, where: str) -> Any:
        if ref in self.stack:  # recursive schema: keep the stub, do not recurse
            self.cycle_hits += 1
            return {"$ref": ref}
        if ref in self.memo:
            return self.memo[ref]
        target = _resolve_pointer(self.root, ref)
        if target is _MISSING:
            self.unresolved.setdefault(ref, where)
            return {"$ref": ref}
        self.stack.append(ref)
        hits = self.cycle_hits
        resolved = self.walk(target, where)
        self.stack.pop()
        if self.cycle_hits == hits:  # only a cycle-free expansion is context-independent
            self.memo[ref] = resolved
        return resolved


def _dereference(spec: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    """Return (spec with local $refs inlined under 'paths', {unresolved ref: where})."""
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return spec, {}
    deref = _Dereferencer(spec)
    resolved = dict(spec)
    resolved["paths"] = deref.walk(paths, "paths")
    return resolved, deref.unresolved


def _ops(spec: dict[str, Any], path: str) -> dict[str, Any]:
    item = spec.get("paths", {}).get(path, {})
    if not isinstance(item, dict):
        return {}
    shared = item.get("parameters")
    return {
        m: _with_shared_params(item[m], shared)
        for m in HTTP_METHODS
        if isinstance(item.get(m), dict)
    }


def _with_shared_params(op: dict[str, Any], shared: Any) -> dict[str, Any]:
    """Merge path-item-level parameters into an operation (the operation's win)."""
    if not isinstance(shared, list) or not shared:
        return op
    merged = {_param_key(p): p for p in shared if isinstance(p, dict)}
    own = op.get("parameters")
    merged.update({_param_key(p): p for p in own or [] if isinstance(p, dict)})
    return {**op, "parameters": list(merged.values())}


def _enum_values(schema: dict[str, Any]) -> list[Any]:
    values = schema.get("enum")
    return list(values) if isinstance(values, list) else []


def _is_extensible(schema: dict[str, Any]) -> bool:
    return bool(schema.get(EXTENSIBLE_ENUM_KEY))


def _diff_enum(
    old_schema: dict[str, Any],
    new_schema: dict[str, Any],
    where: str,
    direction: str,
    out: list[Finding],
) -> None:
    """direction is 'request' (input) or 'response' (output)."""
    old_vals = _enum_values(old_schema)
    new_vals = _enum_values(new_schema)
    if not old_vals and not new_vals:
        return
    removed = [v for v in old_vals if v not in new_vals]
    added = [v for v in new_vals if v not in old_vals]
    # Removing an accepted value narrows the contract -> breaking either way.
    if removed:
        out.append(
            Finding(
                Finding.BREAKING,
                where,
                f"enum value(s) removed: {removed} (narrowing an accepted value set)",
            )
        )
    if not added:
        return
    if direction == "request":
        # A new ACCEPTED input value is additive (old clients still send old values).
        out.append(
            Finding(Finding.ADDITIVE, where, f"request enum value(s) added: {added}")
        )
    else:
        # Response enum: the misclassified case.
        if _is_extensible(old_schema) or _is_extensible(new_schema):
            out.append(
                Finding(
                    Finding.ADDITIVE,
                    where,
                    f"response enum value(s) added: {added} (enum marked "
                    f"{EXTENSIBLE_ENUM_KEY} -- strict clients have an unknown fallback)",
                )
            )
        else:
            out.append(
                Finding(
                    Finding.BREAKING,
                    where,
                    f"response enum value(s) added to a CLOSED enum: {added} -- "
                    f"strict generated SDKs throw on an unknown variant. Mark the "
                    f"enum {EXTENSIBLE_ENUM_KEY} before extending it, or version.",
                )
            )


def _flatten_all_of(schema: dict[str, Any]) -> dict[str, Any]:
    """Merge allOf members into one schema (the schema's own keys win)."""
    members = schema.get("allOf")
    if not isinstance(members, list) or not members:
        return schema
    props: dict[str, Any] = {}
    required: list[Any] = []
    merged: dict[str, Any] = {}
    own = {k: v for k, v in schema.items() if k != "allOf"}
    for part in [*members, own]:
        if not isinstance(part, dict):
            continue
        part = _flatten_all_of(part)
        if isinstance(part.get("properties"), dict):
            props.update(part["properties"])
        if isinstance(part.get("required"), list):
            required.extend(r for r in part["required"] if r not in required)
        for key in ("type", "enum", EXTENSIBLE_ENUM_KEY, "items", "additionalProperties"):
            if key in part:
                merged[key] = part[key]
        for key in ("oneOf", "anyOf"):
            if key in part:
                merged[key] = part[key]
    if props:
        merged["properties"] = props
    if required:
        merged["required"] = required
    return merged


def _diff_nested(
    old_schema: dict[str, Any],
    new_schema: dict[str, Any],
    where: str,
    direction: str,
    out: list[Finding],
) -> None:
    """Walk array items, additionalProperties and oneOf/anyOf variants."""
    _diff_schema(old_schema.get("items"), new_schema.get("items"), f"{where}[]", direction, out)
    _diff_schema(
        old_schema.get("additionalProperties"),
        new_schema.get("additionalProperties"),
        f"{where}.*",
        direction,
        out,
    )
    for key in ("oneOf", "anyOf"):
        old_variants = old_schema.get(key)
        new_variants = new_schema.get(key)
        if not isinstance(old_variants, list) or not isinstance(new_variants, list):
            continue
        pairs = zip(old_variants, new_variants)
        for index, (old_variant, new_variant) in enumerate(pairs):
            _diff_schema(old_variant, new_variant, f"{where}.{key}[{index}]", direction, out)
        change = f"{len(old_variants)} -> {len(new_variants)}"
        if len(new_variants) < len(old_variants):
            if direction == "request":
                msg = f"{key} variant(s) removed from a request ({change}): narrows accepted input"
                out.append(Finding(Finding.BREAKING, f"{where}.{key}", msg))
            else:
                msg = f"response {key} variant(s) removed ({change})"
                out.append(Finding(Finding.INFO, f"{where}.{key}", msg))
        elif len(new_variants) > len(old_variants):
            if direction == "request":
                msg = f"request {key} variant(s) added ({change})"
                out.append(Finding(Finding.ADDITIVE, f"{where}.{key}", msg))
            else:
                msg = (
                    f"{key} variant(s) added to a response ({change}): strict clients "
                    "may not recognise the new variant"
                )
                out.append(Finding(Finding.BREAKING, f"{where}.{key}", msg))


def _diff_schema(
    old_schema: Any,
    new_schema: Any,
    where: str,
    direction: str,
    out: list[Finding],
) -> None:
    if not isinstance(old_schema, dict) or not isinstance(new_schema, dict):
        return
    old_schema = _flatten_all_of(old_schema)
    new_schema = _flatten_all_of(new_schema)

    old_type = old_schema.get("type")
    new_type = new_schema.get("type")
    if old_type is not None and new_type is not None and old_type != new_type:
        out.append(
            Finding(
                Finding.BREAKING,
                where,
                f"type changed: {old_type!r} -> {new_type!r}",
            )
        )

    _diff_enum(old_schema, new_schema, where, direction, out)
    _diff_nested(old_schema, new_schema, where, direction, out)

    old_props = old_schema.get("properties", {})
    new_props = new_schema.get("properties", {})
    if not isinstance(old_props, dict) or not isinstance(new_props, dict):
        return

    old_required = set(old_schema.get("required", []) or [])
    new_required = set(new_schema.get("required", []) or [])

    for name, old_prop in old_props.items():
        prop_where = f"{where}.{name}"
        if name not in new_props:
            if direction == "response":
                out.append(
                    Finding(
                        Finding.BREAKING,
                        prop_where,
                        "response property removed (a consumer may depend on it)",
                    )
                )
            else:
                out.append(
                    Finding(
                        Finding.BREAKING,
                        prop_where,
                        "request property removed",
                    )
                )
            continue
        _diff_schema(old_prop, new_props[name], prop_where, direction, out)

    for name in new_props:
        prop_where = f"{where}.{name}"
        if name in old_props:
            continue
        if direction == "request":
            if name in new_required:
                out.append(
                    Finding(
                        Finding.BREAKING,
                        prop_where,
                        "new REQUIRED request property (tightens input -- old "
                        "clients omit it)",
                    )
                )
            else:
                out.append(
                    Finding(Finding.ADDITIVE, prop_where, "new optional request property")
                )
        else:
            out.append(Finding(Finding.ADDITIVE, prop_where, "new response property"))

    # An existing optional request property becoming required is breaking.
    for name in old_props:
        if name in new_props and name not in old_required and name in new_required:
            out.append(
                Finding(
                    Finding.BREAKING,
                    f"{where}.{name}",
                    "request property became REQUIRED (was optional)",
                )
            )


def _request_schema(operation: dict[str, Any]) -> dict[str, Any]:
    body = operation.get("requestBody", {})
    if not isinstance(body, dict):
        return {}
    content = body.get("content", {})
    if not isinstance(content, dict):
        return {}
    for media in content.values():
        if isinstance(media, dict) and isinstance(media.get("schema"), dict):
            return media["schema"]
    return {}


def _response_schema(response: dict[str, Any]) -> dict[str, Any]:
    content = response.get("content", {})
    if not isinstance(content, dict):
        return {}
    for media in content.values():
        if isinstance(media, dict) and isinstance(media.get("schema"), dict):
            return media["schema"]
    return {}


def _param_key(param: dict[str, Any]) -> tuple[str, str]:
    return (str(param.get("name", "")), str(param.get("in", "")))


def _diff_parameters(
    old_op: dict[str, Any], new_op: dict[str, Any], where: str, out: list[Finding]
) -> None:
    old_params = {
        _param_key(p): p for p in old_op.get("parameters", []) if isinstance(p, dict)
    }
    new_params = {
        _param_key(p): p for p in new_op.get("parameters", []) if isinstance(p, dict)
    }
    for key, old_param in old_params.items():
        name, loc = key
        if key not in new_params:
            out.append(
                Finding(
                    Finding.BREAKING,
                    f"{where} param {name} ({loc})",
                    "parameter removed",
                )
            )
            continue
        if not old_param.get("required") and new_params[key].get("required"):
            out.append(
                Finding(
                    Finding.BREAKING,
                    f"{where} param {name} ({loc})",
                    "parameter became required (was optional)",
                )
            )
    for key, new_param in new_params.items():
        name, loc = key
        if key in old_params:
            continue
        if new_param.get("required"):
            out.append(
                Finding(
                    Finding.BREAKING,
                    f"{where} param {name} ({loc})",
                    "new REQUIRED parameter (old clients omit it)",
                )
            )
        else:
            out.append(
                Finding(
                    Finding.ADDITIVE, f"{where} param {name} ({loc})", "new optional parameter"
                )
            )


def _diff_operation(
    old_op: dict[str, Any], new_op: dict[str, Any], where: str, out: list[Finding]
) -> None:
    _diff_parameters(old_op, new_op, where, out)
    _diff_schema(
        _request_schema(old_op), _request_schema(new_op), f"{where} request", "request", out
    )
    old_resp = old_op.get("responses", {}) if isinstance(old_op.get("responses"), dict) else {}
    new_resp = new_op.get("responses", {}) if isinstance(new_op.get("responses"), dict) else {}
    for code, old_r in old_resp.items():
        if code not in new_resp:
            out.append(
                Finding(
                    Finding.BREAKING,
                    f"{where} response {code}",
                    "response status code removed",
                )
            )
            continue
        if isinstance(old_r, dict) and isinstance(new_resp[code], dict):
            _diff_schema(
                _response_schema(old_r),
                _response_schema(new_resp[code]),
                f"{where} response {code}",
                "response",
                out,
            )
    for code in new_resp:
        if code not in old_resp:
            out.append(
                Finding(
                    Finding.ADDITIVE, f"{where} response {code}", "new response status code"
                )
            )


def diff(old: dict[str, Any], new: dict[str, Any]) -> list[Finding]:
    out: list[Finding] = []

    old, old_unresolved = _dereference(old)
    new, new_unresolved = _dereference(new)
    for side, unresolved in (("old", old_unresolved), ("new", new_unresolved)):
        for ref, where in unresolved.items():
            out.append(
                Finding(
                    Finding.BREAKING,
                    f"{side} {where}",
                    f"UNSURE: unresolved $ref {ref} (external or missing target; not "
                    "diffed -- treat as breaking until checked)",
                )
            )

    old_v = str(old.get("openapi", old.get("swagger", "")))
    new_v = str(new.get("openapi", new.get("swagger", "")))
    if old_v != new_v:
        out.append(Finding(Finding.INFO, "openapi", f"spec version: {old_v!r} -> {new_v!r}"))

    old_paths = old.get("paths", {}) if isinstance(old.get("paths"), dict) else {}
    new_paths = new.get("paths", {}) if isinstance(new.get("paths"), dict) else {}

    for path in old_paths:
        if path not in new_paths:
            out.append(Finding(Finding.BREAKING, path, "path removed"))
            continue
        old_ops = _ops(old, path)
        new_ops = _ops(new, path)
        for method, old_op in old_ops.items():
            if method not in new_ops:
                out.append(
                    Finding(Finding.BREAKING, f"{method.upper()} {path}", "operation removed")
                )
                continue
            _diff_operation(old_op, new_ops[method], f"{method.upper()} {path}", out)
        for method in new_ops:
            if method not in old_ops:
                out.append(
                    Finding(Finding.ADDITIVE, f"{method.upper()} {path}", "new operation")
                )

    for path in new_paths:
        if path not in old_paths:
            out.append(Finding(Finding.ADDITIVE, path, "new path"))

    return out


def _render_text(findings: list[Finding]) -> str:
    order = {Finding.BREAKING: 0, Finding.ADDITIVE: 1, Finding.INFO: 2}
    findings = sorted(findings, key=lambda f: (order[f.level], f.where))
    counts = {
        Finding.BREAKING: sum(1 for f in findings if f.level == Finding.BREAKING),
        Finding.ADDITIVE: sum(1 for f in findings if f.level == Finding.ADDITIVE),
        Finding.INFO: sum(1 for f in findings if f.level == Finding.INFO),
    }
    lines = ["OpenAPI change classification", "=" * 30]
    if not findings:
        lines.append("No differences detected.")
        return "\n".join(lines)
    for finding in findings:
        lines.append(f"[{finding.level:<8}] {finding.where}")
        lines.append(f"           {finding.message}")
    lines.append("-" * 30)
    lines.append(
        f"BREAKING: {counts[Finding.BREAKING]}   "
        f"ADDITIVE: {counts[Finding.ADDITIVE]}   "
        f"INFO: {counts[Finding.INFO]}"
    )
    if counts[Finding.BREAKING]:
        lines.append(
            "Verdict: BREAKING change(s) detected -> bump the major version and "
            "run the deprecation clock (Deprecation + Sunset). See "
            "knowledge/api-versioning-and-evolution-decision-trees.md."
        )
    else:
        lines.append("Verdict: no breaking change detected (additive -- no version bump).")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="openapi_diff.py",
        description="Classify the diff between two OpenAPI (JSON) specs as breaking/additive.",
    )
    parser.add_argument("old", help="baseline OpenAPI JSON document")
    parser.add_argument("new", help="candidate OpenAPI JSON document")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="output format (default: text)",
    )
    args = parser.parse_args(argv)

    findings = diff(_load(args.old), _load(args.new))

    if args.format == "json":
        breaking = sum(1 for f in findings if f.level == Finding.BREAKING)
        print(
            json.dumps(
                {
                    "breaking": breaking,
                    "additive": sum(1 for f in findings if f.level == Finding.ADDITIVE),
                    "info": sum(1 for f in findings if f.level == Finding.INFO),
                    "findings": [f.as_dict() for f in findings],
                },
                indent=2,
            )
        )
    else:
        print(_render_text(findings))

    return 1 if any(f.level == Finding.BREAKING for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
