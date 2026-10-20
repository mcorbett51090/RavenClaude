#!/usr/bin/env bash
# Gate — managed-solution-import pure-logic (offline, no tenant).
#   Exercises the deterministic core: PROD-guard boundaries, the SSRF host allow-list
#   (FM4 — rejects look-alikes, accepts sovereign clouds), baseline-aware reactivation by
#   STABLE key (FM6 — survives a managed import recreating the flow with a new GUID),
#   pac-argv flag economy (publish/force OPT-IN), config validation, and the exit-code map.
#   Teeth: a mutant whose reactivation_targets() returns [] no longer targets the recreated flow.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
# MANAGED_IMPORT_PY lets a caller point the whole test at another copy of the module
# (used to show the orchestration cases fail against a pre-fix tree).
SK="${MANAGED_IMPORT_PY:-$(cd "$HERE/../.." && pwd)/skills/managed-solution-import/managed_import.py}"
fails=0
pass() { echo "  ✓ $1"; }
fail() {
  echo "  ✗ $1"
  fails=$((fails + 1))
}

# Run the pure-logic assertions against a given module file (real or mutant).
assert_core() {
  python3 - "$1" <<'PY'
import importlib.util, sys
from datetime import datetime, timezone

spec = importlib.util.spec_from_file_location("mi", sys.argv[1])
mi = importlib.util.module_from_spec(spec); spec.loader.exec_module(mi)

def utc(h, m, wd_anchor="2026-06-29"):  # 2026-06-29 is a Monday
    return datetime.fromisoformat(f"{wd_anchor}T{h:02d}:{m:02d}:00+00:00")

pg = {"environments": ["prod"], "business_hours": {"window": "09:00-17:00"},
      "blocked_weekdays": [0,1,2,3,4]}
checks = []
def ck(name, cond): checks.append((name, bool(cond)))

# PROD guard boundaries
ck("guard 08:59 allow", mi.prod_guard_verdict(utc(8,59), "prod", pg, False)[0] is False)
ck("guard 09:00 block", mi.prod_guard_verdict(utc(9,0), "prod", pg, False)[0] is True)
ck("guard 17:00 allow", mi.prod_guard_verdict(utc(17,0), "prod", pg, False)[0] is False)
ck("guard --approved override", mi.prod_guard_verdict(utc(10,0), "prod", pg, True)[0] is False)
ck("guard non-prod never blocked", mi.prod_guard_verdict(utc(10,0), "test", pg, False)[0] is False)
ck("guard weekend not blocked", mi.prod_guard_verdict(utc(10,0,"2026-06-28"), "prod", pg, False)[0] is False)
bad_pg = {"environments": ["prod"], "business_hours": {"window": "oops"}}
ck("guard fail-closed on bad window", mi.prod_guard_verdict(utc(10,0), "prod", bad_pg, False)[0] is True)

# SSRF host allow-list
ck("ssrf accepts commercial", mi.is_allowed_dataverse_host("org.crm.dynamics.com"))
ck("ssrf accepts numbered region", mi.is_allowed_dataverse_host("org.crm4.dynamics.com"))
ck("ssrf accepts api infix", mi.is_allowed_dataverse_host("org.api.crm.dynamics.com"))
ck("ssrf accepts GCC-High", mi.is_allowed_dataverse_host("org.crm.microsoftdynamics.us"))
ck("ssrf rejects lookalike suffix", not mi.is_allowed_dataverse_host("evil-dynamics.com"))
ck("ssrf rejects subdomain trick", not mi.is_allowed_dataverse_host("org.crm.dynamics.com.attacker.tld"))
try:
    mi.validate_env_url("http://org.crm.dynamics.com"); ck("ssrf rejects http", False)
except ValueError: ck("ssrf rejects http", True)
try:
    mi.validate_env_url("https://user@org.crm.dynamics.com"); ck("ssrf rejects userinfo", False)
except ValueError: ck("ssrf rejects userinfo", True)

# Baseline-aware reactivation by STABLE key (FM6)
baseline = [{"uniquename": "mc_flowA", "name": "Flow A", "workflowid": "11111111-1111-1111-1111-111111111111"}]
# Managed import recreated Flow A with a NEW guid; it is now Draft. Same uniquename.
current = [
    {"uniquename": "mc_flowA", "name": "Flow A", "workflowid": "99999999-9999-9999-9999-999999999999", "statecode": 0},
    {"uniquename": "mc_flowB", "name": "Flow B", "workflowid": "22222222-2222-2222-2222-222222222222", "statecode": 0},
]
tg = mi.reactivation_targets(baseline, current)
ck("fm6 targets recreated-GUID flow by stable key", len(tg) == 1 and tg[0]["uniquename"] == "mc_flowA")
ck("fm6 does NOT target a flow that was Draft pre-import", all(f["uniquename"] != "mc_flowB" for f in tg))

# Hardening: a Draft flow with NO uniquename must NOT be matched on a colliding display name
collide_baseline = [{"uniquename": "mc_flowA", "name": "Notify", "workflowid": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}]
collide_current = [{"name": "Notify", "workflowid": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", "statecode": 0}]
ck("hardening: no-uniquename Draft flow not matched on display name", mi.reactivation_targets(collide_baseline, collide_current) == [])
ck("hardening: flow_key returns None without uniquename", mi.flow_key({"name": "X", "workflowid": "g"}) is None)

# AAD login-host allow-list (token-endpoint redirect guard)
ck("aad host accepts commercial login", mi.is_aad_login_host("login.microsoftonline.com"))
ck("aad host accepts US-gov login", mi.is_aad_login_host("login.microsoftonline.us"))
ck("aad host rejects lookalike", not mi.is_aad_login_host("login.microsoftonline.com.attacker.tld"))

# pac argv flag economy
argv = mi.build_pac_argv("/s.zip", "https://org.crm.dynamics.com", "settings.json")
ck("argv is a list", isinstance(argv, list))
ck("argv activate-plugins default on", "--activate-plugins" in argv)
ck("argv publish-changes off by default", "--publish-changes" not in argv)
ck("argv force-overwrite off by default", "--force-overwrite" not in argv)
argv2 = mi.build_pac_argv("/s.zip", "https://org.crm.dynamics.com", None, publish_changes=True, force_overwrite=True)
ck("argv publish/force opt-in when asked", "--publish-changes" in argv2 and "--force-overwrite" in argv2)

# backoff + exit-code map + config validation
ck("backoff schedule 3->[15,45]", mi.retry_backoff_schedule(3, 15) == [15, 45])
ck("exit map all active -> 0", mi.map_results_to_exit(3, 3) == mi.EXIT_OK)
ck("exit map none active -> 20", mi.map_results_to_exit(3, 0) == mi.EXIT_ALL_FAILED)
ck("exit map partial -> 10", mi.map_results_to_exit(3, 1) == mi.EXIT_PARTIAL)
ck("config rejects secret-shaped key",
   any("secret" in p for p in mi.validate_config({"environments": {"t": {"url": "https://org.crm.dynamics.com", "client_secret": "x"}}})))
ck("config rejects bad url",
   bool(mi.validate_config({"environments": {"t": {"url": "http://evil.com"}}})))
ck("config rejects non-GUID oid",
   any("impersonate_oid" in p for p in mi.validate_config({"environments": {"t": {"url": "https://org.crm.dynamics.com", "impersonate_oid": "not-a-guid"}}})))
ck("config accepts clean", mi.validate_config({"environments": {"t": {"url": "https://org.crm.dynamics.com"}}}) == [])

bad = [n for n, ok in checks if not ok]
print("MISSING:" + ",".join(bad) if bad else "ALLPASS")
sys.exit(1 if bad else 0)
PY
}

# Orchestration cases (mocked network + pac; no tenant). Section name in $2.
assert_orch() {
  python3 - "$1" "$2" <<'PY'
import contextlib, importlib.util, io, json, os, sys, tempfile, types, urllib.error
from datetime import datetime, timezone

spec = importlib.util.spec_from_file_location("mi", sys.argv[1])
mi = importlib.util.module_from_spec(spec); spec.loader.exec_module(mi)
SECTION = sys.argv[2]
TMP = tempfile.mkdtemp()
checks = []
def ck(name, cond): checks.append((name, bool(cond)))

PROD = "https://prod.crm.dynamics.com"
DEV = "https://dev.crm.dynamics.com"
OTHER = "https://other.crm.dynamics.com"

class FixedDT(datetime):  # Monday 2026-06-29 10:00 in whatever tz is asked for
    @classmethod
    def now(cls, tz=None):
        return datetime(2026, 6, 29, 10, 0, tzinfo=tz or timezone.utc)
mi.datetime = FixedDT

state = {"flows": []}
mi.acquire_token = lambda url: "tok"
mi.query_solution_flows = lambda opener, org, tok, oid: [dict(f) for f in state["flows"]]
mi._pac_on_path = lambda: True

def call(argv, cfg_obj=None):
    """Run mi.main in-process; return (rc, stderr). A raised exception is rc 'RAISED:<type>'."""
    full = list(argv)
    if cfg_obj is not None:
        path = os.path.join(TMP, "cfg.json")
        with open(path, "w") as fh: json.dump(cfg_obj, fh)
        full += ["--config", path]
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = mi.main(full)
    except BaseException as e:  # noqa: BLE001 - an escaped exception is the failure under test
        rc = "RAISED:" + type(e).__name__
    return rc, err.getvalue()

if SECTION == "b14":
    # B-14: the PROD business-hours guard must also classify by the RESOLVED env URL.
    cfg = {"environments": {"prod": {"url": PROD}, "dev": {"url": DEV}},
           "prod_guard": {"environments": ["prod"], "timezone": "UTC",
                          "business_hours": {"window": "09:00-17:00"}}}
    base = ["import", "--solution-path", "s.zip", "--skip-preflight", "--dry-run",
            "--baseline-file", os.path.join(TMP, "b14.json")]
    G = mi.EXIT_PROD_GUARD
    ck("b14 control: --env prod is blocked", call(base + ["--env", "prod"], cfg)[0] == G)
    ck("b14 --env-url equal to the prod url is blocked", call(base + ["--env-url", PROD], cfg)[0] == G)
    ck("b14 --env dev --env-url <prod url> is blocked", call(base + ["--env", "dev", "--env-url", PROD], cfg)[0] == G)
    ck("b14 prod url match is host-normalised (case)", call(base + ["--env-url", "https://PROD.crm.dynamics.com"], cfg)[0] == G)
    ck("b14 --approved still overrides a url-classified prod", call(base + ["--env-url", PROD, "--approved"], cfg)[0] == mi.EXIT_OK)
    ck("b14 a non-prod config url proceeds", call(base + ["--env-url", DEV], cfg)[0] == mi.EXIT_OK)
    ck("b14 an unknown url stays unclassified (no new refusal)", call(base + ["--env-url", OTHER], cfg)[0] == mi.EXIT_OK)
    ck("b14 --env dev alone proceeds", call(base + ["--env", "dev"], cfg)[0] == mi.EXIT_OK)

if SECTION == "b15":
    # B-15: a re-run after a failed pac import must not forget the flows that import disabled.
    pac = {"fail": True}
    def fake_run(argv, check=False):  # the managed import turns every flow off
        for f in state["flows"]:
            f["statecode"], f["statuscode"] = 0, 1
        return types.SimpleNamespace(returncode=1 if pac["fail"] else 0)
    def fake_patch(opener, org, tok, wid, oid):
        for f in state["flows"]:
            if f["workflowid"] == wid:
                f["statecode"], f["statuscode"] = 1, 2
    mi.subprocess.run = fake_run
    mi.patch_flow_active = fake_patch
    bpath = os.path.join(TMP, "b15.json")
    def flow(i, name, code):
        return {"workflowid": str(i), "name": name, "uniquename": "mc_" + name.lower(),
                "statecode": code, "statuscode": 2 if code else 1}
    def names(path):
        return sorted(f["name"] for f in json.load(open(path))["active_flows"])
    imp = ["import", "--env-url", DEV, "--solution-path", "s.zip", "--skip-preflight",
           "--baseline-file", bpath, "--retry-wait", "0"]
    state["flows"] = [flow(1, "A", 1), flow(2, "B", 1)]
    rc1, _ = call(imp)
    ck("b15 run 1: pac failure surfaces as EXIT_PAC_FAILED", rc1 == mi.EXIT_PAC_FAILED)
    ck("b15 run 1 left the flows Draft", all(f["statecode"] == 0 for f in state["flows"]))
    ck("b15 run 1 baseline holds A,B and is pending",
       names(bpath) == ["A", "B"] and json.load(open(bpath)).get("status") == "pending")
    pac["fail"] = False
    rc2, err2 = call(imp)
    ck("b15 run 2: the pending baseline is carried forward (A,B reactivated)",
       rc2 == mi.EXIT_OK and all(f["statecode"] == 1 for f in state["flows"]))
    ck("b15 run 2 baseline still names A,B", names(bpath) == ["A", "B"])
    ck("b15 run 2 says it carried the pending baseline forward", "pending" in err2)
    ck("b15 run 2 marks the baseline complete", json.load(open(bpath)).get("status") == "complete")
    # A completed prior run -> a fresh baseline (operator turned A off deliberately).
    state["flows"] = [flow(1, "A", 0), flow(2, "B", 1)]
    rc3, _ = call(imp)
    ck("b15 run 3 (prior complete): fresh baseline holds only B", names(bpath) == ["B"])
    ck("b15 run 3 does not reactivate the deliberately-off flow",
       rc3 == mi.EXIT_OK and state["flows"][0]["statecode"] == 0 and state["flows"][1]["statecode"] == 1)
    # A pending baseline for a DIFFERENT environment is not merged.
    json.dump({"env_url": OTHER, "status": "pending",
               "active_flows": [{"uniquename": "mc_z", "name": "Z", "workflowid": "9"}]}, open(bpath, "w"))
    state["flows"] = [flow(1, "A", 1)]
    call(imp)
    ck("b15 a pending baseline for another env is overwritten, not merged", names(bpath) == ["A"])
    # A legacy baseline (no status key) is re-captured as today.
    json.dump({"env_url": DEV, "active_flows": [{"uniquename": "mc_old", "name": "Old", "workflowid": "8"}]},
              open(bpath, "w"))
    state["flows"] = [flow(1, "A", 1)]
    call(imp)
    ck("b15 a legacy status-less baseline is re-captured", names(bpath) == ["A"])

bad = [n for n, ok in checks if not ok]
print("MISSING:" + ",".join(bad) if bad else "ALLPASS")
sys.exit(1 if bad else 0)
PY
}

echo "A — pure-logic core"
out="$(assert_core "$SK")"
if [ "$out" = "ALLPASS" ]; then pass "all core assertions hold"; else fail "core assertions failed -> $out"; fi

echo "B — teeth (must-fail): a mutant reactivation_targets() that returns [] stops targeting the recreated flow"
TMP="$(mktemp -d)"; MUT="$TMP/mut.py"
sed 's/^    return targets$/    return []/' "$SK" >"$MUT"
if ! grep -q "^    return \[\]$" "$MUT"; then
  fail "could not neuter reactivation_targets() (sed no-op — fixture stale)"
else
  # mutant must now FAIL the FM6 assertion, i.e. assert_core returns non-ALLPASS mentioning fm6
  mout="$(assert_core "$MUT")"
  if printf '%s' "$mout" | grep -q "fm6"; then
    pass "must-fail half: neutered targeting drops the recreated-flow case (logic is load-bearing)"
  else
    fail "must-fail: neutered targeting still passed FM6 (no teeth) -> $mout"
  fi
fi

echo "C — orchestration (mocked network/pac): B-14 PROD guard also classifies by the resolved env url"
out="$(assert_orch "$SK" b14)"
if [ "$out" = "ALLPASS" ]; then pass "B-14 prod guard holds for --env-url / --env+--env-url, unknown urls unaffected"; else fail "B-14 orchestration failed -> $out"; fi

echo "C — orchestration (mocked network/pac): B-15 a re-run after a failed pac import keeps the pending baseline"
out="$(assert_orch "$SK" b15)"
if [ "$out" = "ALLPASS" ]; then pass "B-15 pending baseline carried forward; completed/foreign/legacy baselines re-captured"; else fail "B-15 orchestration failed -> $out"; fi

echo ""
if [ "$fails" -eq 0 ]; then
  echo "managed-import gate PASS — guard/SSRF/baseline-by-stable-key/flag-economy hold, with teeth."
  exit 0
else
  echo "managed-import gate FAIL — $fails subtest(s)."
  exit 1
fi
