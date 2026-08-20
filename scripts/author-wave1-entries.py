#!/usr/bin/env python3
"""author-wave1-entries.py — P9. Emits the wave-1 mechanism entries.

⛔ THE UNIT IS THE MECHANISM, NOT THE FILE.

The owner worked example — "hooks can send a message two ways and only one
reaches the model" — is a mechanism fact true of ALL 47 hooks at once. Writing it
into 47 entries writes the same fact 47 times. The honest shape of this corpus is
~15-25 genuine mechanism facts that generalise across many artifacts, plus a long
tail whose only honest per-file statement is a summary. Per-artifact binding
survives intact: a mechanism entry lists many paths in covers[] and coverage still
computes PER ARTIFACT.

⛔ EVERY NUANCE HERE WAS MEASURED IN THIS SESSION, and each carries the control
that would have come out differently had the claim been false. They are the same
twelve facts frozen into tests/fixtures/inventory-nuance-golden.json, so the floor
that gates them is calibrated on the very set it grades.

⛔ WHY A GENERATOR RATHER THAN 12 HAND-WRITTEN FILES. Consistency of the
control:-above-the-claim layout, which S1 measured as load-bearing: the premise
guard reads a +/-6-line window, so a control line placed below a 4-line nuance can
fall outside it. A generator cannot forget. See
docs/best-practices/inventory-authoring.md.

Run: python3 scripts/author-wave1-entries.py && scripts/regen-inventory.sh
"""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CDIR = ROOT / "plugins/ravenclaude-core/knowledge/concepts"
CATEGORY = "Inventory — measured mechanisms"
TODAY = datetime.date.today().isoformat()
PLACEHOLDER_DIGEST = "sha256:" + "0" * 64


def _hooks() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "plugins/ravenclaude-core/hooks/*.sh"],
        capture_output=True, text=True, timeout=60,
    ).stdout.split()
    return sorted(p for p in out if "/tests/" not in p)


def _scripts(*names: str) -> list[str]:
    return [f"scripts/{n}" for n in names]


GOLDEN = json.loads((ROOT / "tests/fixtures/inventory-nuance-golden.json").read_text(encoding="utf-8"))
BY_ID = {p["id"]: p for p in GOLDEN["positives"]}

# (concept id, golden id, covers, verify, nuance_source, summary)
ENTRIES = [
    ("hook-message-channels", "pos-two-channel", None,
     {"tier": "effect", "strength": "executed", "class": "hook-advisory",
      "probe": "plugins/ravenclaude-core/hooks/tests/lib/assert-delivered-channel.sh",
      "teeth_exit": 1},
     "plugins/ravenclaude-core/hooks/_advise.sh:1-40",
     "A hook can write to the terminal or to the model, and only one of those reaches the model."),

    ("hook-emitter-collision", "pos-concat-vs-replace",
     ["plugins/ravenclaude-core/hooks/hooks.json", ".claude/settings.json"],
     {"tier": "none", "rationale":
      "Two live emitters on one event cannot be staged offline; the observable needs a real "
      "host session, which places it in the T2 sampled tier gated on claim 15."},
     "plugins/ravenclaude-core/hooks/hooks.json:1-40",
     "What happens when two hooks emit on the same event: one channel adds, the other overwrites."),

    ("plugin-cache-is-version-keyed", "pos-version-keyed-cache",
     ["plugins/ravenclaude-core/.claude-plugin/plugin.json", "scripts/sync-plugin-versions.py",
      "scripts/generate-copilot-plugin.py"],
     {"tier": "reachability", "strength": "static", "class": "static-resolution",
      "probe": "scripts/sync-plugin-versions.py", "teeth_exit": 2},
     "plugins/ravenclaude-core/.claude-plugin/plugin.json:1-10",
     "Why a merged fix does not reach an installed session until the version field moves."),

    ("must-fail-conventions-diverge", "pos-divergent-teeth",
     _scripts("audit-gates.sh", "check-covers-completeness.py", "check-inventory-evidence.py",
              "check-artifact-budgets.py", "check-nuance-floor.py", "inventory-census.py",
              "inventory-sweep.py", "check-inception-coverage.py", "check-ratchet-freshness.py",
              "spike-selfheal-contract.sh", "audit-prose-rendering-path.py",
              "check-changed-concept-renders.py", "inventory-coverage.py",
              "inventory-nuance-judge.py"),
     {"tier": "effect", "strength": "executed", "class": "script-selftest",
      "probe": "scripts/audit-gates.sh", "teeth_exit": 1},
     "scripts/audit-gates.sh:1-40",
     "Every self-testing tool declares its own teeth-bit exit, because no single number fits all."),

    ("bash-tool-response-has-no-exit-code", "pos-no-exit-code-field",
     ["plugins/ravenclaude-core/hooks/triage-outcome.sh",
      "plugins/ravenclaude-core/hooks/cause-triage.sh"],
     {"tier": "none", "rationale":
      "The payload shape is supplied by the host and cannot be synthesised faithfully offline; "
      "a synthetic fixture would assert the shape this entry says is absent."},
     "plugins/ravenclaude-core/hooks/triage-outcome.sh:1-40",
     "What a post-failure hook can and cannot read after a Bash call fails."),

    ("tprose-screens-edits-too", "pos-tprose-edits",
     ["plugins/ravenclaude-core/hooks/guard-premise.sh",
      "docs/best-practices/inventory-authoring.md"],
     {"tier": "effect", "strength": "executed", "class": "hook-decision",
      "probe": "scripts/spike-tprose-canary.sh", "teeth_exit": 1},
     "plugins/ravenclaude-core/hooks/guard-premise.sh:320-462",
     "The premise guard prose screen is not limited to newly created files."),

    ("frontmatter-date-is-a-certainty-stamp", "pos-frontmatter-stamp",
     ["plugins/ravenclaude-core/hooks/guard-premise.sh", "scripts/spike-tprose-canary.sh"],
     {"tier": "effect", "strength": "executed", "class": "hook-decision",
      "probe": "scripts/spike-tprose-canary.sh", "teeth_exit": 1},
     "plugins/ravenclaude-core/hooks/guard-premise.sh:393-400",
     "Metadata you did not write as a claim can still arm the guard certainty trigger."),

    ("selfheal-greps-a-sentence", "pos-selfheal-grep",
     [".github/workflows/regenerate-artifacts.yml", "scripts/concepts.py",
      "scripts/spike-selfheal-contract.sh"],
     {"tier": "effect", "strength": "executed", "class": "script-selftest",
      "probe": "scripts/spike-selfheal-contract.sh", "teeth_exit": 0},
     ".github/workflows/regenerate-artifacts.yml:193-206",
     "How a failing registry check decides whether the post-merge self-heal survives."),

    ("staleness-double-exemption", "pos-double-exemption",
     ["scripts/concepts.py", "scripts/check-covers-completeness.py"],
     {"tier": "effect", "strength": "executed", "class": "script-selftest",
      "probe": "plugins/ravenclaude-core/hooks/tests/test-gate237-inventory-staleness.sh",
      "teeth_exit": 1},
     "scripts/concepts.py:271-330",
     "Which concepts the staleness gate actually covered, and the two ways one escaped it."),

    ("census-must-be-independent", "pos-census-independence",
     _scripts("inventory-census.py", "inventory-sweep.py", "inventory-coverage.py"),
     {"tier": "effect", "strength": "executed", "class": "script-selftest",
      "probe": "scripts/inventory-census.py", "teeth_exit": 1},
     "scripts/inventory-census.py:1-60",
     "Why the coverage denominator is read from git rather than from the registry it measures."),

    ("islanded-panel-costs-two", "pos-islanded-panel",
     _scripts("check-dom-budget.py", "check-artifact-budgets.py", "generate-dashboards.py",
              "generate-index-dashboard.py") + ["scripts/artifact-budgets.seed.json"],
     {"tier": "effect", "strength": "executed", "class": "script-selftest",
      "probe": "scripts/check-artifact-budgets.py", "teeth_exit": 1},
     "scripts/check-dom-budget.py:95-135",
     "What the DOM budget measures, and the far larger number it does not."),

    ("probing-a-script-runs-it", "pos-probe-side-effects",
     _scripts("inventory-sweep.py", "audit-prose-rendering-path.py"),
     {"tier": "effect", "strength": "executed", "class": "script-selftest",
      "probe": "scripts/inventory-sweep.py", "teeth_exit": 1},
     "scripts/inventory-sweep.py:1-60",
     "Asking a script a question is not free: one that ignores arguments simply runs."),
]


def render(cid: str, golden_id: str, covers: list[str], verify: dict,
           source: str, summary: str, order: int) -> str:
    g = BY_ID[golden_id]
    ev = g["nuance_evidence"]
    # ⛔ EVERY FREE-TEXT SCALAR IS JSON-QUOTED. A bare YAML scalar containing ": "
    # is a parse error, and a summary like "…on the same event: one channel adds"
    # is exactly that shape. Quoting is not style here; it is the difference
    # between a registry that builds and one that does not.
    lines = ["---", f"id: {cid}", f"title: {json.dumps(g['title'])}",
             f"category: {json.dumps(CATEGORY)}",
             "kind: ravenclaude-built", "entry_class: inventory", f"order: {order}",
             f"summary: {json.dumps(summary)}", f"last_verified: {TODAY}", "covers:"]
    lines += [f"  - {p}" for p in covers]
    lines.append(f'covers_digest: "{PLACEHOLDER_DIGEST}"')
    lines.append(f"nuance: {json.dumps(g['nuance'])}")
    lines += ["nuance_evidence:", f"  measured: {ev['measured']}",
              f"  control: {json.dumps(ev['control'])}",
              f"  falsifier: {json.dumps(ev['falsifier'])}",
              f"  probe: {json.dumps(ev['probe'])}",
              f"nuance_source: {json.dumps(source)}", "verify:"]
    for k in ("tier", "strength", "class", "probe", "teeth_exit", "rationale"):
        if k in verify:
            v = verify[k]
            lines.append(f"  {k}: {v if isinstance(v, int) else json.dumps(v)}")
    lines += ["sources:",
              "  - label: measured in the FORGE product-inventory run",
              "    url: https://github.com/mcorbett51090/RavenClaude/pull/997",
              "---", "",
              "## What a reader would have assumed instead", "",
              f"{g['nuance_evidence']['control']}", "",
              "## The discriminator", "",
              f"control: {g['nuance_evidence']['control']}",
              f"Measured {ev['measured']}: {g['nuance']}", "",
              "## Why it matters", "",
              f"Falsifier: {g['nuance_evidence']['falsifier']}", "",
              f"Probe: `{ev['probe']}`", ""]
    return "\n".join(lines)


def main() -> int:
    CDIR.mkdir(parents=True, exist_ok=True)
    written = []
    for i, (cid, gid, covers, verify, source, summary) in enumerate(ENTRIES, start=1):
        cov = covers if covers is not None else _hooks()
        missing = [p for p in cov if not (ROOT / p).exists()]
        if missing:
            print(f"  ⚠ {cid}: skipping {len(missing)} covers path(s) that do not exist")
            cov = [p for p in cov if p not in missing]
        if len(summary) > 200:
            print(f"  ✗ {cid}: summary is {len(summary)} chars (max 200)")
            return 1
        (CDIR / f"{cid}.md").write_text(
            render(cid, gid, cov, verify, source, summary, 900 + i), encoding="utf-8"
        )
        written.append((cid, len(cov)))
    print(f"wrote {len(written)} wave-1 inventory entries:")
    for cid, n in written:
        print(f"  · {cid:<42} covers {n} artifact(s)")
    print()
    print("⛔ Next: python3 scripts/concepts.py --restamp-cosmetic <id> for each, then")
    print("   scripts/regen-inventory.sh. The digests above are PLACEHOLDERS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
