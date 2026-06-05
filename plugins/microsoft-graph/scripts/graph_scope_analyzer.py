#!/usr/bin/env python3
"""Microsoft Graph scope analyzer — least-privilege triage for a permission list.

A *calculator/linter*, not a data source and not a security authority: you supply the
scopes (or a JWT access token to read its `scp`/`roles` claims) and it flags the
over-privilege anti-patterns from the `permission-least-privilege-review` skill and
CLAUDE.md §3 #1 / §4, suggesting a narrower alternative where one is well known.

It calls no network and contacts no tenant — it only parses text you give it. Output is
decision-support for a human + `ravenclaude-core/security-reviewer`, never a sign-off.

Usage:
    # Analyze an explicit scope list
    python3 graph_scope_analyzer.py --scopes "User.Read.All,Mail.ReadWrite,Directory.ReadWrite.All"

    # Decode a JWT access token and analyze its scp (delegated) + roles (application) claims
    python3 graph_scope_analyzer.py --token "<jwt>"

    # JSON output (for piping into a report)
    python3 graph_scope_analyzer.py --scopes "Sites.ReadWrite.All" --json

The JWT path performs NO signature verification — it is for inspecting claims only, never
for trusting a token. All findings are heuristic and version-volatile; confirm permission
names against https://learn.microsoft.com/graph/permissions-reference at use.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import sys
from dataclasses import dataclass, field

# Known narrower alternatives for broad scopes (heuristic; verify-at-use).
# Maps a broad permission -> (suggested alternative, rationale).
NARROWER_ALTERNATIVES: dict[str, tuple[str, str]] = {
    "Files.ReadWrite.All": (
        "Files.ReadWrite (delegated) or Sites.Selected (application, per-site)",
        "tenant-wide file write is rarely needed; scope to the user or named sites",
    ),
    "Sites.ReadWrite.All": (
        "Sites.Selected (application, site-specific consent)",
        "Sites.Selected is the least-privilege choice for SharePoint service apps",
    ),
    "Sites.Read.All": (
        "Sites.Selected (application, site-specific consent)",
        "scope to named sites instead of every site in the tenant",
    ),
    "Group.ReadWrite.All": (
        "Group.Read.All + GroupMember.ReadWrite.All",
        "split read from membership-write so neither is broader than needed",
    ),
    "User.ReadWrite.All": (
        "User.Read.All, or delegated User.Read for the signed-in user",
        "tenant-wide user write is high-blast; confirm write is truly required",
    ),
    "Mail.ReadWrite": (
        "Mail.Read (if no write) and/or an application access policy to scope mailboxes",
        "drop write if unused; scope app-only mail to specific mailboxes",
    ),
    "Directory.ReadWrite.All": (
        "a resource-scoped permission (User.*, Group.*) — almost never Directory.*.All",
        "Directory.ReadWrite.All is effectively Tier 0 / tenant admin",
    ),
}

# Permissions that always escalate to security-reviewer when present as APPLICATION scopes
# or when they grant tenant-wide data access (heuristic substrings).
TENANT_WIDE_MARKERS = (".All",)
TIER0_SCOPES = {"Directory.ReadWrite.All", "RoleManagement.ReadWrite.Directory"}


@dataclass
class Finding:
    scope: str
    severity: str  # "escalate" | "narrow" | "info"
    message: str
    suggestion: str | None = None


@dataclass
class Report:
    delegated: list[str] = field(default_factory=list)
    application: list[str] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)

    @property
    def must_escalate(self) -> bool:
        return any(f.severity == "escalate" for f in self.findings)


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def decode_jwt_claims(token: str) -> dict[str, object]:
    """Decode a JWT payload WITHOUT verifying the signature (claims inspection only)."""
    parts = token.strip().split(".")
    if len(parts) < 2:
        raise ValueError("not a JWT: expected at least header.payload.signature")
    try:
        payload = _b64url_decode(parts[1])
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"could not base64url-decode the JWT payload: {exc}") from exc
    try:
        claims = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JWT payload is not valid JSON: {exc}") from exc
    if not isinstance(claims, dict):
        raise ValueError("JWT payload did not decode to a JSON object")
    return claims


def _split_scopes(raw: str) -> list[str]:
    # scp is space-delimited in tokens; CLI input may be comma-delimited.
    items = raw.replace(",", " ").split()
    return [s.strip() for s in items if s.strip()]


def analyze(delegated: list[str], application: list[str]) -> Report:
    report = Report(delegated=sorted(set(delegated)), application=sorted(set(application)))

    for scope in report.application:
        if scope in TIER0_SCOPES:
            report.findings.append(
                Finding(
                    scope,
                    "escalate",
                    "Tier 0 / tenant-admin-equivalent application scope.",
                    NARROWER_ALTERNATIVES.get(scope, (None, ""))[0],
                )
            )
        elif any(m in scope for m in TENANT_WIDE_MARKERS):
            alt = NARROWER_ALTERNATIVES.get(scope)
            report.findings.append(
                Finding(
                    scope,
                    "escalate",
                    "Tenant-wide application permission (grants access to ALL users' data).",
                    alt[0] if alt else None,
                )
            )

    for scope in report.delegated:
        if scope in TIER0_SCOPES:
            report.findings.append(
                Finding(scope, "escalate", "Tier 0 / tenant-admin-equivalent scope.", None)
            )

    # Narrowing suggestions across both lists.
    for scope in report.delegated + report.application:
        alt = NARROWER_ALTERNATIVES.get(scope)
        if alt and not any(f.scope == scope and f.severity == "escalate" for f in report.findings):
            report.findings.append(
                Finding(scope, "narrow", f"Consider narrowing: {alt[1]}.", alt[0])
            )

    if not report.findings:
        report.findings.append(
            Finding("(all)", "info", "No known over-privilege markers in this scope list.", None)
        )
    return report


def render_text(report: Report) -> str:
    lines: list[str] = []
    lines.append("Microsoft Graph scope analysis (heuristic — verify names at use)")
    lines.append("=" * 64)
    lines.append(f"Delegated scopes (scp):   {', '.join(report.delegated) or '(none)'}")
    lines.append(f"Application roles (roles):{' ' + ', '.join(report.application) if report.application else ' (none)'}")
    lines.append("")
    order = {"escalate": 0, "narrow": 1, "info": 2}
    label = {"escalate": "ESCALATE", "narrow": "NARROW  ", "info": "INFO    "}
    for f in sorted(report.findings, key=lambda x: order[x.severity]):
        lines.append(f"[{label[f.severity]}] {f.scope}")
        lines.append(f"           {f.message}")
        if f.suggestion:
            lines.append(f"           -> alternative: {f.suggestion}")
    lines.append("")
    if report.must_escalate:
        lines.append(
            "VERDICT: at least one scope must be escalated to ravenclaude-core/security-reviewer."
        )
    else:
        lines.append("VERDICT: no mandatory escalation flagged (still a human/security-reviewer call).")
    lines.append("This is decision-support, not a security sign-off.")
    return "\n".join(lines)


def render_json(report: Report) -> str:
    return json.dumps(
        {
            "delegated": report.delegated,
            "application": report.application,
            "must_escalate": report.must_escalate,
            "findings": [
                {
                    "scope": f.scope,
                    "severity": f.severity,
                    "message": f.message,
                    "suggestion": f.suggestion,
                }
                for f in report.findings
            ],
            "disclaimer": "Heuristic + version-volatile; verify permission names at use. Not a security sign-off.",
        },
        indent=2,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Least-privilege triage for a Microsoft Graph permission/scope list.",
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument(
        "--scopes",
        help="Comma/space-delimited scope list (delegated by default; use --application for app roles).",
    )
    src.add_argument(
        "--token",
        help="A JWT access token; reads scp (delegated) + roles (application) claims. No signature verification.",
    )
    parser.add_argument(
        "--application",
        help="Comma/space-delimited APPLICATION (app-role) scopes, when using --scopes for delegated.",
        default="",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    delegated: list[str] = []
    application: list[str] = []

    if args.token:
        try:
            claims = decode_jwt_claims(args.token)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        scp = claims.get("scp", "")
        roles = claims.get("roles", [])
        delegated = _split_scopes(scp) if isinstance(scp, str) else []
        if isinstance(roles, list):
            application = [str(r) for r in roles]
        elif isinstance(roles, str):
            application = _split_scopes(roles)
    else:
        delegated = _split_scopes(args.scopes or "")
        application = _split_scopes(args.application or "")

    report = analyze(delegated, application)
    print(render_json(report) if args.json else render_text(report))
    # Exit 1 when an escalation is mandatory, so the script is CI/pipeline-usable.
    return 1 if report.must_escalate else 0


if __name__ == "__main__":
    raise SystemExit(main())
