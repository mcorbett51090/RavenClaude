#!/usr/bin/env python3
"""sec_risk.py — a zero-dependency security risk-triage calculator.

Removes guesswork (and CVSS-only theater) from two recurring AppSec decisions a
security engineer / triager runs constantly. It implements the team's house
doctrine that **CVSS is a property of the flaw in the abstract; risk is a
property of the flaw in YOUR deployment** — see
../knowledge/vulnerability-severity-vs-risk-decision-tree.md.

  risk-band       Turn a CVSS base score + deployment context (reachability,
                  internet exposure, authentication-to-trigger, KEV/known-
                  exploited, optional EPSS probability) into a RISK BAND
                  (emergency / critical / high / medium / low) and a proposed
                  remediation SLA. Mirrors the severity-vs-risk decision tree's
                  leaves exactly; the SLA day-counts are defaults to tune to the
                  org's risk appetite, not a standard-mandated number.

  cvss-temporal   A transparent, *approximate* re-weighting of a CVSS base score
                  by exploit-maturity and remediation-level multipliers, to rank
                  WITHIN a band where KEV is silent. This is a teaching/ranking
                  aid that shows its arithmetic — it is NOT the official CVSS
                  Threat/Temporal calculator (use FIRST's calculator for an
                  authoritative vector). Use it to break ties, never to override
                  the KEV/reachability gate.

This is a CALCULATOR, not a data source — it does not fetch CVEs, the KEV
catalog, or EPSS scores. The user supplies every input; the tool does the
banding/arithmetic and shows the rule it applied. Stdlib only (argparse); runs
anywhere Python 3.9+ is present.

IMPORTANT: outputs are decision-support, not a verdict. The ship/no-ship /
accept-the-risk call routes to ravenclaude-core/security-reviewer (see
../CLAUDE.md §2). Validate the band and SLA against the org's own policy
(and any regulatory window, e.g. CISA BOD 22-01 for federal) before acting.

Examples
--------
  # A reachable, internet-facing, unauthenticated flaw — base 7.5, not on KEV
  python3 sec_risk.py risk-band --cvss 7.5 --reachable yes \\
      --internet-exposed yes --auth-required no --kev no

  # A 9.8 in an unreachable build-time path — base score is high, risk is low
  python3 sec_risk.py risk-band --cvss 9.8 --reachable no \\
      --internet-exposed no --auth-required no --kev no

  # Tie-break within a band: base 8.1, functional exploit exists, no fix yet
  python3 sec_risk.py cvss-temporal --cvss 8.1 \\
      --exploit-maturity functional --remediation-level none
"""

from __future__ import annotations

import argparse
import sys

# --- risk-band: the leaves of the severity-vs-risk decision tree ------------
# Default SLA day-counts. These are a DEFENSIBLE DEFAULT to tune to the org's
# risk appetite (and any policy/regulatory window) — not a standard mandate.
_BANDS = {
    "emergency": {
        "sla": "patch or mitigate NOW (emergency change)",
        "gate": "security-reviewer verdict",
        "why": "KEV-listed or public working exploit / active exploitation",
    },
    "critical": {
        "sla": "stop-and-fix (target <= 72h)",
        "gate": "security-reviewer verdict",
        "why": "reachable + internet-exposed + unauthenticated to trigger",
    },
    "high": {
        "sla": "this sprint (target <= 7 days)",
        "gate": "sprint planning",
        "why": "reachable + internet-exposed, authentication required",
    },
    "medium": {
        "sla": "normal sprint, prioritized",
        "gate": "sprint planning",
        "why": "reachable, internal-only, CVSS base >= 7.0",
    },
    "low": {
        "sla": "normal dependency-update cadence",
        "gate": "PR review",
        "why": "unreachable, OR internal-only with CVSS base < 7.0",
    },
}


def _yn(s: str) -> bool:
    """Parse a yes/no/true/false flag. 'unknown' is treated as yes (fail-safe)."""
    v = s.strip().lower()
    if v in {"yes", "y", "true", "t", "1"}:
        return True
    if v in {"no", "n", "false", "f", "0"}:
        return False
    if v in {"unknown", "u", "?"}:
        # Fail safe toward higher urgency when reachability/exposure is unknown.
        return True
    raise argparse.ArgumentTypeError(f"expected yes/no/unknown, got {s!r}")


def _band(cvss: float, reachable: bool, internet: bool, auth: bool, kev: bool) -> str:
    """Resolve the risk band by traversing the decision tree top-to-bottom."""
    if kev:
        return "emergency"
    if not reachable:
        return "low"
    # reachable (or unknown) from here
    if not internet:
        return "medium" if cvss >= 7.0 else "low"
    # reachable + internet-exposed
    return "high" if auth else "critical"


def cmd_risk_band(a: argparse.Namespace) -> int:
    if not 0.0 <= a.cvss <= 10.0:
        print("error: --cvss must be between 0.0 and 10.0", file=sys.stderr)
        return 2
    reachable = _yn(a.reachable)
    internet = _yn(a.internet_exposed)
    auth = _yn(a.auth_required)
    kev = _yn(a.kev)
    band = _band(a.cvss, reachable, internet, auth, kev)
    info = _BANDS[band]

    print("Security risk triage — band + proposed SLA")
    print("-" * 52)
    print(f"  CVSS base score    : {a.cvss}")
    print(f"  Reachable in usage : {'yes' if reachable else 'no'}")
    print(f"  Internet-exposed   : {'yes' if internet else 'no'}")
    print(f"  Auth to trigger    : {'yes' if auth else 'no'}")
    print(f"  KEV / known-exploited: {'yes' if kev else 'no'}")
    if a.epss is not None:
        print(f"  EPSS probability   : {a.epss:.2%} (tie-breaker within a band)")
    print("-" * 52)
    print(f"  RISK BAND          : {band.upper()}")
    print(f"  Why                : {info['why']}")
    print(f"  Proposed SLA       : {info['sla']}")
    print(f"  Approval gate      : {info['gate']}")
    print("-" * 52)
    print("  Note: the SLA day-counts are a default to tune to the org's risk")
    print("  appetite (+ any regulatory window, e.g. CISA BOD 22-01). The")
    print("  ship/no-ship / accept-the-risk verdict routes to security-reviewer.")
    return 0


# --- cvss-temporal: transparent, approximate within-band re-weighting -------
# Multipliers below are illustrative ranking weights (loosely modeled on the
# CVSS v3.1 Temporal metric direction) — NOT the official CVSS Threat/Temporal
# equation. Use FIRST's calculator for an authoritative vector.
_EXPLOIT_MATURITY = {
    "not-defined": 1.00,
    "unproven": 0.91,
    "poc": 0.94,
    "functional": 0.97,
    "high": 1.00,
}
_REMEDIATION_LEVEL = {
    "not-defined": 1.00,
    "official-fix": 0.95,
    "temporary-fix": 0.96,
    "workaround": 0.97,
    "none": 1.00,
}


def cmd_cvss_temporal(a: argparse.Namespace) -> int:
    if not 0.0 <= a.cvss <= 10.0:
        print("error: --cvss must be between 0.0 and 10.0", file=sys.stderr)
        return 2
    em = _EXPLOIT_MATURITY[a.exploit_maturity]
    rl = _REMEDIATION_LEVEL[a.remediation_level]
    adjusted = round(min(a.cvss * em * rl, 10.0), 1)

    print("CVSS within-band re-weighting (APPROXIMATE — ranking aid only)")
    print("-" * 62)
    print(f"  CVSS base score        : {a.cvss}")
    print(f"  Exploit maturity       : {a.exploit_maturity} (x{em:.2f})")
    print(f"  Remediation level      : {a.remediation_level} (x{rl:.2f})")
    print("-" * 62)
    print(f"  Adjusted ranking score : {adjusted}  (= base x maturity x remediation)")
    print("-" * 62)
    print("  This is a transparent tie-breaker WITHIN a risk band, not the")
    print("  official CVSS Threat/Temporal score. For an authoritative vector")
    print("  use FIRST's calculator (https://www.first.org/cvss/calculator/).")
    print("  It never overrides the KEV/reachability gate in `risk-band`.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sec_risk.py",
        description="Security risk-triage calculator (decision-support, not a verdict).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command", required=True)

    rb = sub.add_parser("risk-band", help="CVSS + context -> risk band + proposed SLA")
    rb.add_argument("--cvss", type=float, required=True, help="CVSS base score 0.0-10.0")
    rb.add_argument("--reachable", default="unknown", help="vulnerable path reachable? yes/no/unknown")
    rb.add_argument("--internet-exposed", default="unknown", help="exposed to untrusted/internet input? yes/no/unknown")
    rb.add_argument("--auth-required", default="yes", help="authentication required to trigger? yes/no/unknown")
    rb.add_argument("--kev", default="no", help="on CISA KEV / known-exploited / public PoC? yes/no")
    rb.add_argument("--epss", type=float, default=None, help="optional EPSS probability 0.0-1.0 (tie-breaker)")
    rb.set_defaults(func=cmd_risk_band)

    ct = sub.add_parser("cvss-temporal", help="approximate within-band CVSS re-weighting (ranking aid)")
    ct.add_argument("--cvss", type=float, required=True, help="CVSS base score 0.0-10.0")
    ct.add_argument(
        "--exploit-maturity",
        choices=sorted(_EXPLOIT_MATURITY),
        default="not-defined",
        help="exploit code maturity",
    )
    ct.add_argument(
        "--remediation-level",
        choices=sorted(_REMEDIATION_LEVEL),
        default="not-defined",
        help="remediation availability",
    )
    ct.set_defaults(func=cmd_cvss_temporal)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
