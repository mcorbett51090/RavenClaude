#!/usr/bin/env python3
"""pii_risk_score.py — a zero-dependency data-governance scoring helper.

Removes guesswork from three recurring governance dispositioning decisions by
turning the signals a steward already observes into a transparent, repeatable
score. It does NOT fetch data, scan a warehouse, or read a regulation — the
user supplies every signal; the tool does the arithmetic and shows the formula
and the threshold it crossed.

  classify        Map a data asset to a sensitivity TIER (public / internal /
                  confidential / restricted) from observable signals: does it
                  contain PII, is any of it special-category, how many people,
                  how identifiable, how harmful if disclosed. Pairs with the
                  "Classify this data" tree (knowledge/data-governance-privacy-
                  decision-trees.md). Classification drives controls.

  dpia-threshold  Score whether a processing activity likely WARRANTS a Data
                  Protection Impact Assessment, from the high-risk indicators a
                  GDPR Art. 35 / EDPB-style screen looks at (large-scale,
                  special-category, systematic monitoring, vulnerable subjects,
                  new tech, automated decisions, matching/combining, etc.).
                  Output is a SCREENING signal, not a legal determination.

  reident         Score the re-identification risk of a "de-identified" dataset
                  from observable signals (smallest equivalence-class size k,
                  number of quasi-identifiers, whether a re-linking key exists,
                  whether it's released publicly). Pairs with the "Is this
                  anonymized or pseudonymized?" tree. A held key => pseudonymized
                  => STILL personal data, regardless of the rest.

This is a SCORING HELPER, not legal advice and not a data source (see
../CLAUDE.md §2 #6 — governance engineering, not legal advice). The thresholds
are transparent heuristics for triage/prioritization; a DPIA-warranted signal
means "engage your DPO/legal," a classification tier means "apply these
controls" — neither is a regulatory determination. Validate every input and
route every legal interpretation to legal / regulatory-compliance.

Stdlib only (argparse); runs anywhere Python 3.8+ is present.

Examples
--------
  # Classify: contains PII, no special-category, ~50k people, directly
  # identifiable, moderate harm if disclosed
  python3 pii_risk_score.py classify --pii yes --special-category no \\
      --subjects 50000 --identifiability direct --harm moderate

  # DPIA screen: large-scale special-category processing with systematic
  # monitoring and an automated decision affecting people
  python3 pii_risk_score.py dpia-threshold --large-scale --special-category \\
      --systematic-monitoring --automated-decision

  # Re-identification: k=2 smallest group, 6 quasi-identifiers, no re-linking
  # key held, released publicly
  python3 pii_risk_score.py reident --k 2 --quasi-identifiers 6 \\
      --key-held no --public-release yes
"""

from __future__ import annotations

import argparse
import sys

# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------

_IDENTIFIABILITY = {"none": 0, "indirect": 1, "direct": 2}
_HARM = {"low": 0, "moderate": 1, "high": 2}


def cmd_classify(args: argparse.Namespace) -> int:
    if args.subjects < 0:
        print("error: --subjects must be >= 0", file=sys.stderr)
        return 2

    pii = args.pii == "yes"
    special = args.special_category == "yes"
    ident = _IDENTIFIABILITY[args.identifiability]
    harm = _HARM[args.harm]
    large = args.subjects >= 10000

    print("Data-asset sensitivity classification")
    print(f"  contains PII            : {args.pii}")
    print(f"  special-category        : {args.special_category}")
    print(f"  subjects                : {args.subjects:,} ({'large-scale' if large else 'limited'})")
    print(f"  identifiability         : {args.identifiability}")
    print(f"  harm if disclosed       : {args.harm}")

    # Tier logic — strongest-signal-wins, transparent and ordered.
    if pii and special:
        tier = "RESTRICTED"
        why = "special-category PII => strongest controls + lawful basis required"
    elif pii and (ident == 2 or large or harm == 2):
        tier = "RESTRICTED" if (large and harm == 2) else "CONFIDENTIAL"
        why = ("directly-identifiable / large-scale / high-harm PII"
               if tier == "RESTRICTED"
               else "PII present => access-controlled, retention + DSR scope")
    elif pii:
        tier = "CONFIDENTIAL"
        why = "PII present => access-controlled, retention + DSR scope"
    elif harm == 2:
        tier = "CONFIDENTIAL"
        why = "no PII but high harm if disclosed"
    elif harm == 1:
        tier = "INTERNAL"
        why = "no PII, some harm if disclosed => internal-only"
    else:
        tier = "PUBLIC or INTERNAL"
        why = "no PII, low harm => Public if intended for release, else Internal"

    print()
    print(f"  -> suggested tier       : {tier}")
    print(f"     basis                : {why}")
    print("  next: classification drives controls — map the tier to enforceable")
    print("        access/masking/retention rules (-> data-platform/security). The")
    print("        tier is a triage signal, not a legal determination (CLAUDE.md §2).")
    return 0


# ---------------------------------------------------------------------------
# dpia-threshold
# ---------------------------------------------------------------------------

# The high-risk indicators a GDPR Art. 35 / EDPB WP248-style screen weighs.
# Each is a binary the steward observes. Two-or-more high-risk criteria is the
# commonly-cited screening signal for "a DPIA is likely warranted" — but this is
# a SCREEN, not a determination; the DPO/legal makes the call.
_DPIA_CRITERIA = [
    ("evaluation_scoring", "evaluation / scoring / profiling"),
    ("automated_decision", "automated decision with legal/significant effect"),
    ("systematic_monitoring", "systematic monitoring (incl. public spaces)"),
    ("special_category", "special-category or highly personal data"),
    ("large_scale", "processing on a large scale"),
    ("matching_combining", "matching or combining datasets"),
    ("vulnerable_subjects", "data on vulnerable subjects (children, employees, patients)"),
    ("new_technology", "innovative use or new technology"),
    ("prevents_right_contract", "processing that prevents a right / blocks a service or contract"),
]


def cmd_dpia_threshold(args: argparse.Namespace) -> int:
    flags = [(label, getattr(args, attr)) for attr, label in _DPIA_CRITERIA]
    met = [label for label, present in flags if present]
    count = len(met)

    print("DPIA screening — GDPR Art. 35 high-risk indicators")
    print("  (a SCREEN for prioritization, NOT a legal determination)")
    for label, present in flags:
        print(f"    [{'x' if present else ' '}] {label}")
    print()
    print(f"  high-risk indicators met : {count} of {len(_DPIA_CRITERIA)}")

    if count >= 2:
        verdict = "DPIA LIKELY WARRANTED"
        detail = ("two or more high-risk indicators present — engage your DPO/legal "
                  "and run a DPIA before processing")
    elif count == 1:
        verdict = "DPIA POSSIBLY WARRANTED"
        detail = ("one high-risk indicator — borderline; document the screen and "
                  "consult the DPO/legal on whether a DPIA is required")
    else:
        verdict = "NO HIGH-RISK INDICATOR FROM THIS SCREEN"
        detail = ("none of the screened indicators present — record the screen; "
                  "re-screen if the processing changes")

    print(f"  -> {verdict}")
    print(f"     {detail}")
    print("  note: this is decision-support, not legal advice (CLAUDE.md §2 #6).")
    print("        The DPO / legal makes the DPIA-required determination; jurisdictional")
    print("        DPA lists of mandatory-DPIA processing override this generic screen.")
    return 0


# ---------------------------------------------------------------------------
# reident
# ---------------------------------------------------------------------------


def cmd_reident(args: argparse.Namespace) -> int:
    if args.k < 1:
        print("error: --k (smallest equivalence-class size) must be >= 1", file=sys.stderr)
        return 2
    if args.quasi_identifiers < 0:
        print("error: --quasi-identifiers must be >= 0", file=sys.stderr)
        return 2

    key_held = args.key_held == "yes"
    public = args.public_release == "yes"

    print("Re-identification risk screen for a 'de-identified' dataset")
    print(f"  smallest group size k   : {args.k}")
    print(f"  quasi-identifiers       : {args.quasi_identifiers}")
    print(f"  re-linking key held     : {args.key_held}")
    print(f"  released publicly        : {args.public_release}")
    print()

    # The dispositive rule first: a held key means it can be re-linked.
    if key_held:
        print("  -> PSEUDONYMIZED — STILL PERSONAL DATA")
        print("     a re-linking key exists, so individuals can be re-identified with it.")
        print("     Full privacy scope applies (lawful basis, DSR, retention) regardless")
        print("     of k or quasi-identifier count. Dropping the name column is not")
        print("     anonymization (CLAUDE.md §2 #5).")
        return 0

    # No key held — score residual risk from k, quasi-IDs, and release surface.
    risk = 0
    reasons = []
    if args.k < 5:
        risk += 2
        reasons.append(f"k={args.k} below the common k=5 floor (singling-out risk)")
    elif args.k < 10:
        risk += 1
        reasons.append(f"k={args.k} is modest; verify it survives a linkage attack")
    if args.quasi_identifiers >= 5:
        risk += 2
        reasons.append(f"{args.quasi_identifiers} quasi-identifiers enable linkage/inference")
    elif args.quasi_identifiers >= 3:
        risk += 1
        reasons.append(f"{args.quasi_identifiers} quasi-identifiers — moderate linkage surface")
    if public:
        risk += 1
        reasons.append("public release removes the access boundary; assume an adversary")

    if risk >= 3:
        band = "HIGH re-identification risk"
        verdict = ("likely STILL personal data — treat as pseudonymized and apply full "
                   "controls, or strengthen the technique (generalize to higher k, "
                   "reduce quasi-IDs, differential privacy) and re-assess")
    elif risk >= 1:
        band = "MODERATE re-identification risk"
        verdict = ("borderline — run a formal re-identification risk assessment before "
                   "treating it as anonymized")
    else:
        band = "LOW residual re-identification risk from this screen"
        verdict = ("plausibly anonymized — but confirm with a documented re-identification "
                   "risk assessment (verified technique, not just columns dropped)")

    print(f"  residual-risk score      : {risk}")
    for r in reasons:
        print(f"    - {r}")
    print(f"  -> {band}")
    print(f"     {verdict}")
    print("  note: this screen does not replace a formal re-identification risk")
    print("        assessment; anonymization is a high bar (CLAUDE.md §2 #5).")
    return 0


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pii_risk_score.py",
        description="Data-governance scoring helper (stdlib only). Decision-support "
        "for triage/prioritization, NOT legal advice — validate every input and route "
        "legal interpretation to legal/regulatory-compliance (CLAUDE.md §2 #6).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    cl = sub.add_parser("classify", help="Map a data asset to a sensitivity tier")
    cl.add_argument("--pii", choices=["yes", "no"], required=True,
                    help="does the asset contain personal data / PII?")
    cl.add_argument("--special-category", choices=["yes", "no"], default="no",
                    help="any special-category data (health, biometric, etc.)? default no")
    cl.add_argument("--subjects", type=int, default=0,
                    help="approximate number of distinct people (>=10000 => large-scale)")
    cl.add_argument("--identifiability", choices=["none", "indirect", "direct"],
                    default="none", help="how directly does it identify a person? default none")
    cl.add_argument("--harm", choices=["low", "moderate", "high"], default="low",
                    help="harm to subjects if disclosed. default low")
    cl.set_defaults(func=cmd_classify)

    dp = sub.add_parser("dpia-threshold", help="Screen whether a DPIA is likely warranted")
    for attr, label in _DPIA_CRITERIA:
        dp.add_argument(f"--{attr.replace('_', '-')}", dest=attr, action="store_true",
                        help=label)
    dp.set_defaults(func=cmd_dpia_threshold)

    ri = sub.add_parser("reident", help="Screen re-identification risk of a de-identified dataset")
    ri.add_argument("--k", type=int, required=True,
                    help="smallest equivalence-class size (k in k-anonymity)")
    ri.add_argument("--quasi-identifiers", type=int, required=True,
                    help="number of quasi-identifier columns (age, ZIP, gender, ...)")
    ri.add_argument("--key-held", choices=["yes", "no"], required=True,
                    help="does anyone hold a key/mapping that re-links to individuals?")
    ri.add_argument("--public-release", choices=["yes", "no"], default="no",
                    help="is the dataset released publicly? default no")
    ri.set_defaults(func=cmd_reident)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
