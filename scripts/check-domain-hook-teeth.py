#!/usr/bin/env python3
"""Fires-on-bad / silent-on-good fixtures for domain-plugin advisory hooks.

Each case drives ONE hook exactly as its plugin's hooks/hooks.json registers it:
the registered command string runs through `sh -c` with CLAUDE_PLUGIN_ROOT set,
CLAUDE_TOOL_FILE_PATH unset (so the quoted "$CLAUDE_TOOL_FILE_PATH" argument is
empty, as under Claude Code), and a realistic tool payload as JSON on stdin.

  - PreToolUse cases model the write that has NOT landed yet: the target file is
    absent (Write) or holds the pre-edit bytes (Edit), and the new text is only
    in .tool_input.content / .new_string.
  - PostToolUse cases model the write that HAS landed: the file holds the
    content on disk, and the payload carries it too.

A "fires" case passes when the check's own message (`needle`) is in the hook's
output. A "silent" case passes when that message is absent, and, for a case
marked quiet, when the hook printed nothing at all and exited 0. Asserting the
check's own message, not just "any output", keeps a sibling check in the same
hook from masking a dead one.

Added by the 2026-10-19 repo review (WS-G) for the dead `[\\s\\S]`-in-`grep -E`
checks, the PreToolUse PII scrubber that only read the pre-edit file, the
line-level `<.*>` placeholder filter, the case-insensitive IBAN check, the Swift
self-capture false positive, and the Standard connectors flagged as premium.

Usage:  python3 scripts/check-domain-hook-teeth.py [--root <repo>] [-v]
Exit 0 = every case passed; 1 = at least one failed (each failure is printed).
Stdlib only. Synthetic PII/secret shapes are built by concatenation.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile

# Strict-mode knobs a developer may have exported; a case must see the default.
_STRICT_VARS = (
    "BACKEND_STRICT",
    "STREAM_STRICT",
    "FE_STRICT",
    "ML_STRICT",
    "MOBILE_STRICT",
    "EXP_STRICT",
    "PAY_STRICT",
    "FINANCE_STRICT",
    "POWER_PLATFORM_STRICT",
    "REGCOMP_STRICT",
)

# Synthetic identifier shapes, assembled at runtime (never a literal in source).
SSN = "219-09-" + "9999"
EIN = "53-" + "1234567"
IBAN = "GB82" + "WEST" + "1234" + "5698" + "7654" + "32"

N1_LOOP = (
    "def load(users):\n"
    "    for user in users:\n"
    '        rows = db.query("SELECT * FROM orders WHERE user_id = %s", user.id)\n'
)
N1_ONE_LINE = 'for u in users: rows = db.query("SELECT 1 FROM t WHERE id = %s", u.id)\n'
N1_BATCHED = (
    "ids = []\n"
    "for user in users:\n"
    "    ids.append(user.id)\n"
    'rows = db.query("SELECT * FROM orders WHERE user_id = ANY(%s)", ids)\n'
    "for key in keys:\n"
    "    value = cache.get(key)\n"
    "while True:\n"
    '    idx = text.find("\\n", idx + 1)\n'
)
N1_MONGO = 'for user in users:\n    orders = db.orders.find({"user_id": user.id})\n'

FLOW_STANDARD = {
    "properties": {
        "connectionReferences": {
            "shared_sharepointonline": {
                "api": {"name": "shared_sharepointonline"},
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
            },
            "shared_teams": {
                "api": {"name": "shared_teams"},
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_teams",
            },
        },
        "definition": {"actions": {"Try": {"type": "Scope", "actions": {}}}},
    }
}
FLOW_HTTP = {
    "properties": {
        "connectionReferences": {
            "shared_webcontents": {
                "api": {"name": "shared_webcontents"},
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_webcontents",
            }
        },
        "definition": {"actions": {"Try": {"type": "Scope", "actions": {}}}},
    }
}


def C(cid, plugin, script, event, rel, content, expect, needle, **kw):
    case = {
        "id": cid,
        "plugin": plugin,
        "script": script,
        "event": event,
        "rel": rel,
        "content": content,
        "expect": expect,
        "needle": needle,
    }
    case.update(kw)
    return case


REG = ("regulatory-compliance", "scrub-confidential-pre-write.sh", "PreToolUse")
FIN = ("finance", "flag-finance-anti-patterns.sh", "PostToolUse")
BE = ("backend-engineering", "check-backend-engineering-anti-patterns.sh", "PreToolUse")
DS = (
    "data-streaming-engineering",
    "check-data-streaming-engineering-anti-patterns.sh",
    "PreToolUse",
)
FE = ("frontend-engineering", "check-frontend-engineering-anti-patterns.sh", "PreToolUse")
ML = ("ml-engineering", "check-ml-engineering-anti-patterns.sh", "PreToolUse")
MO = ("mobile-engineering", "check-mobile-engineering-anti-patterns.sh", "PreToolUse")
EX = (
    "experimentation-growth-engineering",
    "check-experimentation-growth-engineering-anti-patterns.sh",
    "PreToolUse",
)
FP = (
    "fintech-payments-engineering",
    "check-fintech-payments-engineering-anti-patterns.sh",
    "PreToolUse",
)
PP = ("power-platform", "check-house-opinions.sh", "PostToolUse")

CASES = [
    # --- regulatory-compliance: content being written is what gets scanned ---
    C(
        "reg-new-file-ssn",
        *REG,
        "compliance/new-sar.md",
        f"Subject SSN {SSN}\n",
        "fires",
        "[pii-ssn]",
    ),
    C(
        "reg-new-file-clean",
        *REG,
        "compliance/new-kyc.md",
        "Customer onboarding notes.\n",
        "silent",
        "[pii-",
        quiet=True,
    ),
    C(
        "reg-edit-introduces-ssn",
        *REG,
        "compliance/clean-kyc.md",
        f"SSN {SSN}\n",
        "fires",
        "[pii-ssn]",
        tool="Edit",
        on_disk="Clean onboarding notes.\n",
    ),
    C(
        "reg-ssn-beside-tag",
        *REG,
        "compliance/kyc-b.md",
        f"| Jane Doe | {SSN} <br> |\n",
        "fires",
        "[pii-ssn]",
    ),
    C(
        "reg-ssn-placeholders",
        *REG,
        "compliance/kyc-p.md",
        "| a | 123-45-6789 <br> |\n| b | XXX-XX-XXXX |\n| c | 000-00-0000 |\n",
        "silent",
        "[pii-ssn]",
    ),
    C(
        "reg-ein-beside-tag",
        *REG,
        "compliance/kyc-c.md",
        f"See ticket <KYC-12>: customer EIN {EIN} verified.\n",
        "fires",
        "[pii-ein]",
    ),
    C(
        "reg-ein-placeholders",
        *REG,
        "compliance/kyc-e.md",
        "EIN 00-0000000 and 99-9999999 <x>\n",
        "silent",
        "[pii-ein]",
    ),
    C("reg-iban-upper", *REG, "compliance/kyc-i.md", f"IBAN {IBAN}\n", "fires", "[pii-iban]"),
    C(
        "reg-iban-lowercase-hash",
        *REG,
        "compliance/kyc-d.md",
        "Ref ab12cdef9012345 is a commit hash.\n",
        "silent",
        "[pii-iban]",
    ),
    # --- finance flag hook: token-level placeholder filter ---
    C(
        "fin-ssn-beside-tag",
        *FIN,
        "finance/payroll.md",
        f"| Jane | {SSN} <br> |\n",
        "fires",
        "[plaintext-pii-ssn]",
    ),
    C(
        "fin-ssn-placeholder-beside-real",
        *FIN,
        "finance/payroll2.md",
        f"| a | 123-45-6789,{SSN} |\n",
        "fires",
        "[plaintext-pii-ssn]",
    ),
    C(
        "fin-ssn-placeholders",
        *FIN,
        "finance/notes.md",
        "| Jane | 123-45-6789 <br> |\n",
        "silent",
        "[plaintext-pii-ssn]",
    ),
    # --- backend-engineering ---
    C("be-n1-loop", *BE, "app/users.py", N1_LOOP, "fires", "Possible N+1"),
    C("be-n1-one-line", *BE, "app/users2.py", N1_ONE_LINE, "fires", "Possible N+1"),
    C("be-n1-mongo-find", *BE, "app/users4.py", N1_MONGO, "fires", "Possible N+1"),
    C("be-n1-batched", *BE, "app/users3.py", N1_BATCHED, "silent", "Possible N+1"),
    C(
        "be-dual-write",
        *BE,
        "app/orders.py",
        'session.commit()\nbus.publish("order.created", order.id)\n',
        "fires",
        "Possible dual-write",
    ),
    C(
        "be-commit-only",
        *BE,
        "app/orders2.py",
        "session.add(OutboxEvent(order.id))\nsession.commit()\nreturn order\n",
        "silent",
        "Possible dual-write",
        quiet=True,
    ),
    # --- data-streaming-engineering ---
    C(
        "ds-commit-then-send",
        *DS,
        "svc/orders.py",
        'db.session.commit()\nproducer.send("orders", value=evt)\n',
        "fires",
        "Possible dual-write",
    ),
    C(
        "ds-send-then-commit",
        *DS,
        "svc/orders2.py",
        'producer.send("orders", value=evt)\ndb.commit()\n',
        "fires",
        "Possible dual-write",
    ),
    C(
        "ds-send-consumer-commit",
        *DS,
        "svc/relay.py",
        'producer.send("out", value=evt)\nproducer.flush()\nconsumer.commit()\n',
        "silent",
        "Possible dual-write",
        quiet=True,
    ),
    # --- frontend-engineering ---
    C(
        "fe-effect-reads-props",
        *FE,
        "src/Profile.tsx",
        "useEffect(() => {\n  fetchUser(props.userId);\n}, []);\n",
        "fires",
        "useEffect with [] deps",
    ),
    C(
        "fe-effect-deps-listed",
        *FE,
        "src/Profile2.tsx",
        'useEffect(() => {\n  fetchUser(props.userId);\n}, [props.userId]);\nuseEffect(() => {\n  document.title = "Home";\n}, []);\n',
        "silent",
        "useEffect with [] deps",
        quiet=True,
    ),
    # --- ml-engineering ---
    C(
        "ml-shuffled-temporal-split",
        *ML,
        "train/split.py",
        'df = load_events(parse_dates=["event_date"])\nX_train, X_test = train_test_split(df, test_size=0.2, shuffle=True)\n',
        "fires",
        "Shuffled split",
    ),
    C(
        "ml-unshuffled-temporal-split",
        *ML,
        "train/split2.py",
        'df = load_events(parse_dates=["event_date"])\nX_train, X_test = train_test_split(df, test_size=0.2, shuffle=False)\n',
        "silent",
        "Shuffled split",
    ),
    C(
        "ml-shuffled-non-temporal",
        *ML,
        "train/split3.py",
        "X_train, X_test = train_test_split(X, y, test_size=0.2, shuffle=True)\n",
        "silent",
        "Shuffled split",
    ),
    C(
        "ml-predict-reads-csv",
        *ML,
        "serve/batch.py",
        'preds = model.predict(pd.read_csv("live_features.csv"))\n',
        "fires",
        "serving features ad-hoc",
    ),
    C(
        "ml-predict-reads-csv-multiline",
        *ML,
        "serve/batch2.py",
        'preds = model.predict(\n    pd.read_csv("live_features.csv")\n)\n',
        "fires",
        "serving features ad-hoc",
    ),
    C(
        "ml-predict-shared-features",
        *ML,
        "serve/batch3.py",
        'preds = model.predict(features)\nreport = pd.read_csv("report.csv")\n',
        "silent",
        "serving features ad-hoc",
        quiet=True,
    ),
    # --- mobile-engineering ---
    C(
        "mo-token-in-userdefaults",
        *MO,
        "ios/Auth.swift",
        'UserDefaults.standard.set(token, forKey: "auth_token")\n',
        "fires",
        "Secret stored in UserDefaults",
    ),
    C(
        "mo-flag-in-userdefaults",
        *MO,
        "ios/Prefs.swift",
        'UserDefaults.standard.set(true, forKey: "hasOnboarded")\n',
        "silent",
        "Secret stored in UserDefaults",
        quiet=True,
    ),
    C(
        "mo-setinterval-fetch",
        *MO,
        "app/poll.js",
        "setInterval(async () => {\n  const r = await fetch(url);\n}, 1000);\n",
        "fires",
        "Possible polling loop",
    ),
    C(
        "mo-while-true-fetch",
        *MO,
        "app/poll2.js",
        "while (true) {\n  await fetch(url);\n}\n",
        "fires",
        "Possible polling loop",
    ),
    C(
        "mo-setinterval-clock",
        *MO,
        "app/clock.js",
        "setInterval(updateClock, 1000);\n",
        "silent",
        "Possible polling loop",
        quiet=True,
    ),
    C(
        "mo-closure-strong-self",
        *MO,
        "ios/Feed.swift",
        "api.load { result in\n    self.items = result\n}\n",
        "fires",
        "Closure capturing self",
    ),
    C(
        "mo-init-body",
        *MO,
        "ios/Store.swift",
        "final class Store {\n    let k: Int\n    init(k: Int) { self.k = k }\n}\n",
        "silent",
        "Closure capturing self",
        quiet=True,
    ),
    C(
        "mo-func-body",
        *MO,
        "ios/Runner.swift",
        "func run() {\n    self.go()\n}\n",
        "silent",
        "Closure capturing self",
        quiet=True,
    ),
    C(
        "mo-func-for-in",
        *MO,
        "ios/Loop.swift",
        "func run() {\n    for x in xs { self.go(x) }\n}\n",
        "silent",
        "Closure capturing self",
        quiet=True,
    ),
    C(
        "mo-weak-self",
        *MO,
        "ios/Feed2.swift",
        "api.load { [weak self] result in\n    self?.items = result\n}\n",
        "silent",
        "Closure capturing self",
        quiet=True,
    ),
    C(
        "mo-js-not-swift",
        *MO,
        "app/legacy.js",
        "var self = this;\nbutton.on('click', function (e) { self.done = true; });\n",
        "silent",
        "Closure capturing self",
        quiet=True,
    ),
    # --- experimentation-growth-engineering ---
    C(
        "ex-title-case-event",
        *EX,
        "web/track.ts",
        'analytics.track("Button Clicked", { plan });\n',
        "fires",
        "ad-hoc/inconsistent event name",
    ),
    C(
        "ex-object-action-event",
        *EX,
        "web/track2.ts",
        'analytics.track("button_clicked", { plan });\n',
        "silent",
        "ad-hoc/inconsistent event name",
        quiet=True,
    ),
    # --- fintech-payments-engineering ---
    C(
        "fp-float-cast-total",
        *FP,
        "pay/order.py",
        "amount = float(order.total)\n",
        "fires",
        "floating-point money",
    ),
    C(
        "fp-integer-cents",
        *FP,
        "pay/order2.py",
        'price_cents: int = 999\nprice = Decimal("9.99")\n',
        "silent",
        "floating-point money",
        quiet=True,
    ),
    C(
        "fp-log-card-number",
        *FP,
        "pay/charge.py",
        "logger.info(card_number)\n",
        "fires",
        "Logging card data",
    ),
    C(
        "fp-log-benign",
        *FP,
        "pay/charge2.py",
        'logger.info("payment expanded for company")\n',
        "silent",
        "Logging card data",
        quiet=True,
    ),
    # --- power-platform: Standard connectors are not premium ---
    C(
        "pp-standard-connectors",
        *PP,
        "Solution/workflows/notify.json",
        json.dumps(FLOW_STANDARD),
        "silent",
        "premium-connector-no-licensing-note",
    ),
    C(
        "pp-premium-http-connector",
        *PP,
        "Solution/workflows/scrape.json",
        json.dumps(FLOW_HTTP),
        "fires",
        "premium-connector-no-licensing-note",
    ),
]


def registered_command(plugin_root: str, event: str, script: str) -> str:
    with open(os.path.join(plugin_root, "hooks", "hooks.json"), encoding="utf-8") as fh:
        hooks = json.load(fh).get("hooks", {})
    for group in hooks.get(event, []):
        for h in group.get("hooks", []):
            if script in h.get("command", ""):
                return h["command"]
    raise LookupError(f"{script} is not registered under {event} in {plugin_root}/hooks/hooks.json")


def run_case(root: str, case: dict, work: str) -> tuple[bool, str]:
    plugin_root = os.path.join(root, "plugins", case["plugin"])
    cmd = registered_command(plugin_root, case["event"], case["script"])
    proj = os.path.join(work, case["id"])
    target = os.path.join(proj, case["rel"])
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tool = case.get("tool", "Write")
    if case["event"] == "PostToolUse":
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(case["content"])
    elif case.get("on_disk") is not None:
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(case["on_disk"])
    if tool == "Edit":
        tool_input = {
            "file_path": target,
            "old_string": case.get("on_disk", ""),
            "new_string": case["content"],
        }
    else:
        tool_input = {"file_path": target, "content": case["content"]}
    payload = {
        "hook_event_name": case["event"],
        "tool_name": tool,
        "tool_input": tool_input,
        "cwd": proj,
    }
    env = {
        k: v
        for k, v in os.environ.items()
        if k != "CLAUDE_TOOL_FILE_PATH" and k not in _STRICT_VARS
    }
    env["CLAUDE_PLUGIN_ROOT"] = plugin_root
    env["CLAUDE_PROJECT_DIR"] = proj
    r = subprocess.run(
        ["sh", "-c", cmd],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=proj,
        env=env,
        timeout=60,
    )
    out = r.stdout + r.stderr
    if case["expect"] == "fires":
        ok = case["needle"] in out
        why = f"expected {case['needle']!r} in the output (rc={r.returncode})"
    else:
        ok = case["needle"] not in out
        why = f"expected no {case['needle']!r} in the output (rc={r.returncode})"
        if ok and case.get("quiet"):
            ok = out.strip() == "" and r.returncode == 0
            why = f"expected no output and exit 0 (rc={r.returncode})"
    detail = "" if ok else f"{why}\n      output: {out.strip()[:600]!r}"
    return ok, detail


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--root", default=".", help="repo root holding plugins/ (default: cwd)")
    ap.add_argument(
        "-v", "--verbose", action="store_true", help="print every case, not only failures"
    )
    args = ap.parse_args(argv)
    root = os.path.abspath(args.root)
    failures = 0
    with tempfile.TemporaryDirectory(prefix="hook-teeth-") as work:
        for case in CASES:
            try:
                ok, detail = run_case(root, case, work)
            except (LookupError, OSError, subprocess.SubprocessError) as exc:
                ok, detail = False, f"could not run: {exc}"
            if not ok:
                failures += 1
                print(f"  FAIL {case['id']} [{case['plugin']}] {detail}")
            elif args.verbose:
                print(f"  PASS {case['id']} [{case['plugin']}]")
    total = len(CASES)
    print(f"domain-hook-teeth: {total - failures}/{total} cases passed.")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
