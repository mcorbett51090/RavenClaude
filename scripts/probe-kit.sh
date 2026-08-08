#!/usr/bin/env bash
# probe-kit.sh — ready-made CONTROL probes: the positive-capable counterpart to
# a negative result.
#
# THE RULE THIS EXISTS TO MAKE CHEAP:
#   A negative result is not a diagnosis until a positive control on the SAME
#   subsystem has been observed.
#
# WHY (the incident, 2026-08-07 — real numbers, not a hypothetical):
#   GET https://www.ravenpower.net/cdn-cgi/l/email-protection   -> 404
#   became "the decoder is broken, therefore every visitor sees a mangled
#   address", which became an 85-line component, 10 call sites, 15 marker pairs
#   across 5 files, an owner checklist item pushed to main, and two turns of
#   owner-facing architectural advice. All of it wrong. That URL is a
#   PLACEHOLDER nothing ever fetches — it is SUPPOSED to 404.
#
#   The controls, had anyone run them:
#     GET /cdn-cgi/trace                                        -> 200   (~10s)
#     GET the real decoder script (.../email-decode.min.js)     -> 200
#     a real browser against the allegedly-broken production site:
#       span.__cf_email__ remaining ......... 0
#       href ................................ mailto:matt@ravenpower.net
#
#   The disconfirming probe cost ~10 SECONDS. The construction cost hours and
#   16 files. The control was cheap and nobody ran it, because running it
#   required THINKING OF IT. This script is the thinking-of-it part, pre-done.
#
# THIS IS DELIBERATELY NOT A GATE. It blocks nothing, and it asks you to believe
# nothing. It lowers the activation energy of the right action to one line. If
# the premise-gate plan's "a fail-closed gate beats prose" assumption turns out
# to be wrong, this still works — because it changes a cost, not a rule.
#
# Usage (one line, no setup, no config, no state):
#   bash scripts/probe-kit.sh http <url>     probe the URL + a control on the same host
#   bash scripts/probe-kit.sh dns  <host>    resolve the host + a control in the same zone
#   bash scripts/probe-kit.sh file <path>    stat the path  + a control on the same tree
#   bash scripts/probe-kit.sh cmd  <name>    look up a command + a control on the same PATH
#   bash scripts/probe-kit.sh --explain [type]   what a negative does / does NOT license
#   bash scripts/probe-kit.sh --self-test        prove the instrument before believing it
#
# Options (after the target): --control <c>  --timeout <secs>
#
# EXIT-CODE CONTRACT (stable; scripts may branch on it):
#   0  subject POSITIVE     — nothing negative to diagnose
#   1  CONFIRMED            — subject negative, control positive: the negative is real
#   2  SUSPECT              — control ALSO failed: your probe target may be wrong
#   3  INCONCLUSIVE         — the control could not run (no network/resolver/permission)
#   64 usage error
#
# Portability: stock macOS bash 3.2 — no `declare -A`, no `mapfile`, no `${x^^}`,
# no `shopt -s globstar`, no `grep -P`, no `sed -i`, no GNU `timeout`. Every
# probe carries its own ceiling (curl -m, dig +time) so nothing can hang, and
# every no-network path returns INCONCLUSIVE rather than blocking.

set -uo pipefail

PK_VERSION="1.0.0"
PK_TIMEOUT="${PROBE_KIT_TIMEOUT:-10}"
PK_CONNECT_TIMEOUT=5
PK_DNS_TIMEOUT=3
PK_UA="probe-kit/${PK_VERSION} (RavenClaude verification-discipline)"

if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
  C_DIM=$'\033[2m'; C_RED=$'\033[31m'; C_GRN=$'\033[32m'
  C_YEL=$'\033[33m'; C_BLD=$'\033[1m'; C_OFF=$'\033[0m'
else
  C_DIM=''; C_RED=''; C_GRN=''; C_YEL=''; C_BLD=''; C_OFF=''
fi

# Filled in by each probe, consumed by _pk_report.
PK_KIND=""
PK_S_LABEL=""; PK_S_RESULT=""; PK_S_STATE="UNRUN"
PK_C_LABEL=""; PK_C_RESULT=""; PK_C_STATE="UNRUN"; PK_C_WHY=""
PK_RERUN=""; PK_NOTE=""
# Set to 1 when the control turned out to be the SAME probe as the subject.
# A re-run of the same probe is not a control — it cannot distinguish "the
# target is bad" from "the instrument is bad", because both halves move
# together. (plan.md §2.4: `control` must differ from `kill_shot`.)
PK_SAME=0

# ── the verdict resolver — the one piece that must be able to fail ───────────
# Pure function. Four inputs must produce four DISTINCT outcomes; a stub that
# always returns the same thing is caught by --self-test's TEETH subtest.
# States: POSITIVE | NEGATIVE | UNRUN
_pk_verdict() {
  case "$1/$2" in
    POSITIVE/*)        printf 'POSITIVE' ;;
    NEGATIVE/POSITIVE) printf 'CONFIRMED' ;;
    NEGATIVE/NEGATIVE) printf 'SUSPECT' ;;
    *)                 printf 'INCONCLUSIVE' ;;
  esac
}

_pk_exit_for() {
  case "$1" in
    POSITIVE)     printf '0' ;;
    CONFIRMED)    printf '1' ;;
    SUSPECT)      printf '2' ;;
    *)            printf '3' ;;
  esac
}

_pk_state_paint() {
  case "$1" in
    POSITIVE) printf '%sPOSITIVE%s' "$C_GRN" "$C_OFF" ;;
    NEGATIVE) printf '%sNEGATIVE%s' "$C_RED" "$C_OFF" ;;
    *)        printf '%sDID NOT RUN%s' "$C_YEL" "$C_OFF" ;;
  esac
}

_pk_rule() {
  printf '%s── probe-kit · %s %s%s\n' "$C_DIM" "$1" \
    "────────────────────────────────────────────────" "$C_OFF"
}

_pk_report() {
  local verdict rc
  if [ "$PK_SAME" = "1" ]; then
    verdict="INCONCLUSIVE"
  else
    verdict="$(_pk_verdict "$PK_S_STATE" "$PK_C_STATE")"
  fi
  rc="$(_pk_exit_for "$verdict")"

  printf '\n'
  _pk_rule "$PK_KIND"
  printf '  %sSUBJECT%s  %s\n' "$C_BLD" "$C_OFF" "$PK_S_LABEL"
  printf '           -> %-44s [%s]\n' "$PK_S_RESULT" "$(_pk_state_paint "$PK_S_STATE")"
  printf '  %sCONTROL%s  %s\n' "$C_BLD" "$C_OFF" "$PK_C_LABEL"
  printf '           -> %-44s [%s]\n' "$PK_C_RESULT" "$(_pk_state_paint "$PK_C_STATE")"
  [ -n "$PK_C_WHY" ] && printf '           %swhy this control: %s%s\n' "$C_DIM" "$PK_C_WHY" "$C_OFF"
  printf '\n'

  case "$verdict" in
    POSITIVE)
      printf '  %sVERDICT%s  subject probe SUCCEEDED — there is no negative result to diagnose.\n' \
        "$C_BLD" "$C_OFF"
      printf '           A positive here says the target answered. It does not say the\n'
      printf '           user-visible behaviour is correct — for that, measure what the user sees.\n'
      ;;
    CONFIRMED)
      printf '  %sVERDICT%s  %snegative result CONFIRMED by control%s\n' \
        "$C_BLD" "$C_OFF" "$C_GRN" "$C_OFF"
      printf '           The probe is demonstrably capable of returning a positive on this\n'
      printf '           subsystem, so the negative is about the TARGET, not the instrument.\n'
      printf '           %sIt still does NOT license a diagnosis of the subsystem or of user\n' "$C_DIM"
      printf '           impact. Run: probe-kit.sh --explain %s%s\n' "$PK_KIND" "$C_OFF"
      ;;
    SUSPECT)
      printf '  %sVERDICT%s  %s⛔ CONTROL ALSO FAILED — your probe target may be wrong, not the subject.%s\n' \
        "$C_BLD" "$C_OFF" "$C_RED" "$C_OFF"
      printf '           A known-good control on the same subsystem failed too, so this probe\n'
      printf '           has NOT been shown capable of succeeding. Treat the subject result as\n'
      printf '           uninformative until the control passes. Fix the control first.\n'
      ;;
    *)
      if [ "$PK_SAME" = "1" ]; then
        printf '  %sVERDICT%s  %s⛔ NOT A CONTROL — it is the SAME probe as the subject.%s\n' \
          "$C_BLD" "$C_OFF" "$C_YEL" "$C_OFF"
        printf '           Re-running the same probe cannot separate "the target is bad" from\n'
        printf '           "the instrument is bad" — both halves move together, so the result is\n'
        printf '           identical under every hypothesis. Pass a DIFFERENT --control.\n'
      else
        printf '  %sVERDICT%s  %s⛔ INCONCLUSIVE — the control could not run.%s\n' \
          "$C_BLD" "$C_OFF" "$C_YEL" "$C_OFF"
        printf '           No network, no resolver, no permission, or a missing tool. This is\n'
        printf '           evidence about your INSTRUMENT, not about the subject. Nothing here\n'
        printf '           licenses any conclusion about the target.\n'
      fi
      ;;
  esac

  [ -n "$PK_NOTE" ] && { printf '\n           %s%s%s\n' "$C_DIM" "$PK_NOTE" "$C_OFF"; }

  if [ -n "$PK_RERUN" ]; then
    printf '\n  %sRERUN THE CONTROL%s (copy-paste):\n    %s\n' "$C_BLD" "$C_OFF" "$PK_RERUN"
  fi
  printf '\n  %sexit %s  (0 positive · 1 negative CONFIRMED · 2 control ALSO failed · 3 inconclusive)%s\n\n' \
    "$C_DIM" "$rc" "$C_OFF"

  return "$rc"
}

# ── http ─────────────────────────────────────────────────────────────────────

_pk_http_status() {
  local url="$1" code rc
  command -v curl >/dev/null 2>&1 || { printf 'nocurl'; return 0; }
  code="$(curl -sS -o /dev/null -w '%{http_code}' \
            --connect-timeout "$PK_CONNECT_TIMEOUT" -m "$PK_TIMEOUT" \
            -A "$PK_UA" "$url" 2>/dev/null)"
  rc=$?
  if [ "$rc" -ne 0 ] || [ -z "$code" ] || [ "$code" = "000" ]; then
    printf 'transport:%s' "$rc"
  else
    printf 'HTTP %s' "$code"
  fi
}

_pk_http_state() {
  case "$1" in
    "HTTP 2"*|"HTTP 3"*) printf 'POSITIVE' ;;
    "HTTP "*)            printf 'NEGATIVE' ;;
    *)                   printf 'UNRUN' ;;
  esac
}

_pk_http_human() {
  case "$1" in
    nocurl)       printf 'curl is not on PATH — the probe could not run' ;;
    transport:6)  printf 'no response (curl 6: host could not be resolved)' ;;
    transport:7)  printf 'no response (curl 7: connection refused / unreachable)' ;;
    transport:28) printf 'no response (curl 28: timed out)' ;;
    transport:35) printf 'no response (curl 35: TLS handshake failed)' ;;
    transport:*)  printf 'no response (curl exit %s)' "${1#transport:}" ;;
    *)            printf '%s' "$1" ;;
  esac
}

# Derive a control URL on the SAME host. Cloudflare's /cdn-cgi/trace is special-
# cased because it is THE edge-health control the incident needed.
_pk_http_control_url() {
  local url="$1" scheme rest host path
  case "$url" in
    http://*)  scheme="http://";  rest="${url#http://}" ;;
    https://*) scheme="https://"; rest="${url#https://}" ;;
    *)         scheme="https://"; rest="$url" ;;
  esac
  host="${rest%%/*}"
  if [ "$rest" = "$host" ]; then path="/"; else path="/${rest#*/}"; fi
  # The control must be a DIFFERENT URL on the same host — a re-run of the same
  # request proves nothing (§2.4). So /cdn-cgi/trace and / are each other's
  # control rather than their own.
  case "$path" in
    /cdn-cgi/trace) printf '%s%s/' "$scheme" "$host" ;;
    /cdn-cgi/*)     printf '%s%s/cdn-cgi/trace' "$scheme" "$host" ;;
    /)              printf '%s%s/cdn-cgi/trace' "$scheme" "$host" ;;
    *)              printf '%s%s/' "$scheme" "$host" ;;
  esac
}

_pk_probe_http() {
  local url="$1" ctl="$2" s c
  PK_KIND="http"
  if [ -z "$ctl" ]; then
    ctl="$(_pk_http_control_url "$url")"
    case "$ctl" in
      */cdn-cgi/trace) PK_C_WHY="same host, same Cloudflare edge — /cdn-cgi/trace is the edge-health endpoint (404 here just means the host is not behind Cloudflare; pass --control)" ;;
      *)               PK_C_WHY="same host: same DNS, same TLS, same edge — the site root" ;;
    esac
  else
    PK_C_WHY="supplied with --control"
  fi
  [ "$ctl" = "$url" ] && PK_SAME=1

  s="$(_pk_http_status "$url")"
  c="$(_pk_http_status "$ctl")"
  PK_S_LABEL="GET $url"; PK_S_RESULT="$(_pk_http_human "$s")"; PK_S_STATE="$(_pk_http_state "$s")"
  PK_C_LABEL="GET $ctl"; PK_C_RESULT="$(_pk_http_human "$c")"; PK_C_STATE="$(_pk_http_state "$c")"
  PK_RERUN="curl -sS -o /dev/null -w '%{http_code}\\n' -m ${PK_TIMEOUT} '${ctl}'"

  if [ "$PK_S_STATE" = "NEGATIVE" ] && [ "$PK_C_STATE" = "POSITIVE" ]; then
    PK_NOTE="Reminder: a 4xx on one URL is not a broken feature. Some URLs are SUPPOSED to 404 (placeholders, sentinels). Before you build on this, measure what a real user sees."
  fi
  _pk_report
}

# ── dns ──────────────────────────────────────────────────────────────────────

# echoes: ok:<answer> | norecord | unrun:<reason>
_pk_dns_lookup() {
  local h="$1" out rc
  if command -v dig >/dev/null 2>&1; then
    out="$(dig +short "+time=${PK_DNS_TIMEOUT}" +tries=1 "$h" 2>/dev/null)"
    rc=$?
    if [ "$rc" -ne 0 ]; then printf 'unrun:dig-exit-%s' "$rc"; return 0; fi
    out="$(printf '%s\n' "$out" | awk 'NF{print;exit}')"
    if [ -n "$out" ]; then printf 'ok:%s' "$out"; else printf 'norecord'; fi
    return 0
  fi
  if command -v host >/dev/null 2>&1; then
    out="$(host -W "$PK_DNS_TIMEOUT" "$h" 2>/dev/null)"
    rc=$?
    if [ "$rc" -eq 0 ]; then
      printf 'ok:%s' "$(printf '%s\n' "$out" | awk 'NF{print;exit}')"
    elif [ "$rc" -eq 1 ]; then printf 'norecord'
    else printf 'unrun:host-exit-%s' "$rc"; fi
    return 0
  fi
  if command -v perl >/dev/null 2>&1; then
    out="$(perl -e 'my @a=gethostbyname($ARGV[0]); if(@a && defined $a[4]){print join(".",unpack("C4",$a[4])),"\n"; exit 0} exit 1' "$h" 2>/dev/null)"
    rc=$?
    if [ "$rc" -eq 0 ] && [ -n "$out" ]; then printf 'ok:%s' "$out"; else printf 'norecord'; fi
    return 0
  fi
  printf 'unrun:no-resolver-tool'
}

_pk_dns_state() {
  case "$1" in
    ok:*)     printf 'POSITIVE' ;;
    norecord) printf 'NEGATIVE' ;;
    *)        printf 'UNRUN' ;;
  esac
}

_pk_dns_human() {
  case "$1" in
    ok:*)                printf 'resolved -> %s' "${1#ok:}" ;;
    norecord)            printf 'no record returned (NXDOMAIN or empty answer)' ;;
    unrun:no-resolver-tool) printf 'no dig/host/perl on PATH — the probe could not run' ;;
    unrun:*)             printf 'resolver did not answer (%s)' "${1#unrun:}" ;;
    *)                   printf '%s' "$1" ;;
  esac
}

# Control host: the parent zone when there is one (same registrable domain, so
# a positive there proves the resolver answers for this zone), else an
# IANA-reserved name that is guaranteed to exist.
_pk_dns_control_host() {
  local h="$1" labels parent
  labels="$(printf '%s\n' "$h" | awk -F. '{print NF}')"
  if [ "${labels:-0}" -ge 3 ]; then
    parent="${h#*.}"
    printf '%s' "$parent"
    return 0
  fi
  case "$h" in
    example.com|www.example.com) printf 'example.net' ;;
    *)                           printf 'example.com' ;;
  esac
}

_pk_probe_dns() {
  local h="$1" ctl="$2" s c tool
  PK_KIND="dns"
  if [ -z "$ctl" ]; then
    ctl="$(_pk_dns_control_host "$h")"
    case "$ctl" in
      example.com|example.net) PK_C_WHY="IANA-reserved name that always exists — proves the resolver answers at all" ;;
      *)                       PK_C_WHY="the parent zone of the subject — proves this zone resolves for you" ;;
    esac
  else
    PK_C_WHY="supplied with --control"
  fi
  [ "$ctl" = "$h" ] && PK_SAME=1

  s="$(_pk_dns_lookup "$h")"
  c="$(_pk_dns_lookup "$ctl")"
  PK_S_LABEL="resolve $h"; PK_S_RESULT="$(_pk_dns_human "$s")"; PK_S_STATE="$(_pk_dns_state "$s")"
  PK_C_LABEL="resolve $ctl"; PK_C_RESULT="$(_pk_dns_human "$c")"; PK_C_STATE="$(_pk_dns_state "$c")"

  if command -v dig >/dev/null 2>&1; then
    PK_RERUN="dig +short +time=${PK_DNS_TIMEOUT} +tries=1 '${ctl}'"
  elif command -v host >/dev/null 2>&1; then
    PK_RERUN="host -W ${PK_DNS_TIMEOUT} '${ctl}'"
  else
    PK_RERUN="perl -e 'print join(\".\",unpack(\"C4\",(gethostbyname(\$ARGV[0]))[4])),\"\\n\"' '${ctl}'"
  fi
  tool=""
  command -v dig >/dev/null 2>&1 && tool="dig"
  [ -z "$tool" ] && command -v host >/dev/null 2>&1 && tool="host"
  [ -z "$tool" ] && tool="perl gethostbyname"
  PK_NOTE="Resolved with: ${tool}. One resolver is one data point — split-horizon DNS, a captive portal, a VPN, and propagation delay all produce the same negative."
  _pk_report
}

# ── file ─────────────────────────────────────────────────────────────────────

_pk_nearest_ancestor() {
  local d="$1"
  while [ -n "$d" ] && [ "$d" != "/" ] && [ "$d" != "." ]; do
    if [ -e "$d" ]; then printf '%s' "$d"; return 0; fi
    d="$(dirname "$d")"
  done
  if [ -e "$d" ]; then printf '%s' "$d"; else printf ''; fi
}

_pk_ftype() {
  if [ -d "$1" ]; then printf 'directory'
  elif [ -L "$1" ]; then printf 'symlink'
  elif [ -f "$1" ]; then printf 'file'
  else printf 'other'; fi
}

_pk_probe_file() {
  local target="$1" ctl="$2" dir n anc
  PK_KIND="file"

  if [ -e "$target" ]; then
    PK_S_STATE="POSITIVE"; PK_S_RESULT="exists ($(_pk_ftype "$target"))"
  elif [ -L "$target" ]; then
    PK_S_STATE="NEGATIVE"; PK_S_RESULT="a symlink exists but its target does not"
  else
    PK_S_STATE="NEGATIVE"; PK_S_RESULT="not found"
  fi
  PK_S_LABEL="stat $target"

  if [ -n "$ctl" ]; then
    dir="$ctl"; PK_C_WHY="supplied with --control"
  else
    dir="$(dirname "$target")"
    PK_C_WHY="the containing directory — if the reader can list it, an absent file is genuinely absent"
  fi
  [ "$dir" = "$target" ] && PK_SAME=1

  if [ -d "$dir" ] && [ -r "$dir" ] && [ -x "$dir" ]; then
    n="$(ls -A "$dir" 2>/dev/null | wc -l | tr -d ' ')"
    PK_C_STATE="POSITIVE"; PK_C_RESULT="directory readable, lists ${n} entries"
  elif [ -e "$dir" ] && [ ! -d "$dir" ]; then
    PK_C_STATE="NEGATIVE"; PK_C_RESULT="exists but is not a directory"
  elif [ -e "$dir" ]; then
    PK_C_STATE="UNRUN"; PK_C_RESULT="exists but is not readable/traversable (permission)"
  else
    PK_C_STATE="NEGATIVE"; PK_C_RESULT="the containing directory does not exist either"
  fi
  PK_C_LABEL="list $dir"
  PK_RERUN="ls -la '${dir}'"

  if [ "$PK_C_STATE" = "NEGATIVE" ]; then
    anc="$(_pk_nearest_ancestor "$dir")"
    PK_NOTE="Deepest existing ancestor: ${anc:-<none>}. A missing PARENT usually means a wrong base path or a wrong cwd (currently $(pwd)) — not a missing file."
  elif [ "$PK_C_STATE" = "UNRUN" ]; then
    PK_NOTE="You cannot distinguish 'absent' from 'not permitted to see' here. Running as uid $(id -u 2>/dev/null || printf '?')."
  fi
  _pk_report
}

# ── cmd ──────────────────────────────────────────────────────────────────────

_pk_probe_cmd() {
  local name="$1" ctl="$2" p cp_ nparts cand
  PK_KIND="cmd"
  # The control must be a DIFFERENT command, or it is the same probe twice.
  if [ -z "$ctl" ]; then
    for cand in sh cat ls; do
      if [ "$cand" != "$name" ]; then ctl="$cand"; break; fi
    done
  fi
  [ "$ctl" = "$name" ] && PK_SAME=1

  p="$(command -v "$name" 2>/dev/null)"
  if [ -n "$p" ]; then
    PK_S_STATE="POSITIVE"; PK_S_RESULT="found at $p"
  else
    PK_S_STATE="NEGATIVE"; PK_S_RESULT="not on PATH"
  fi
  PK_S_LABEL="command -v $name"

  cp_="$(command -v "$ctl" 2>/dev/null)"
  if [ -n "$cp_" ]; then
    PK_C_STATE="POSITIVE"; PK_C_RESULT="found at $cp_"
  else
    PK_C_STATE="NEGATIVE"; PK_C_RESULT="NOT found — the lookup itself is broken"
  fi
  PK_C_LABEL="command -v $ctl"
  PK_C_WHY="a command present on every POSIX host — proves PATH lookup works at all"
  PK_RERUN="command -v ${ctl}; printf 'PATH=%s\\n' \"\$PATH\""

  nparts="$(printf '%s\n' "${PATH:-}" | awk -F: '{print NF}')"
  [ -z "${PATH:-}" ] && nparts=0
  if [ "$PK_S_STATE" = "NEGATIVE" ] && [ "$PK_C_STATE" = "POSITIVE" ]; then
    PK_NOTE="PATH has ${nparts} entries. 'not on PATH' is not 'not installed' and is never 'this host cannot do X' — the tool may be off-PATH (homebrew vs env -i PATH=/usr/bin:/bin). This repo shipped that exact bug: stock macOS has no GNU 'timeout', which exits 127 and silently disarmed the decision-review tribunal."
  else
    PK_NOTE="PATH has ${nparts} entries."
  fi
  _pk_report
}

# ── --explain ────────────────────────────────────────────────────────────────

_pk_explain_head() {
  printf '\n%sA negative result is not a diagnosis until a positive control on the same\n' "$C_BLD"
  printf 'subsystem has been observed.%s\n\n' "$C_OFF"
  printf '%sA negative tells you what did NOT happen in ONE probe. It never tells you why,\n' "$C_DIM"
  printf 'and it never tells you the blast radius. Those are separate measurements.%s\n' "$C_OFF"
}

_pk_explain_http() {
  cat <<'EOF'

── http ────────────────────────────────────────────────────────────────────
  A negative (4xx/5xx) LICENSES exactly this:
    "this URL returned this status, at this moment, from this client."

  It does NOT license:
    - "the host is down"          -> the control on the same host may be 200
    - "the feature is broken"     -> some URLs are SUPPOSED to 404
    - "every visitor is affected" -> that is a user-visible measurement, not a status code
    - "the edge/CDN is misconfigured"

  WORKED EXAMPLE (the incident this kit exists for):
    GET /cdn-cgi/l/email-protection  -> 404   EXPECTED. A placeholder href that
                                              nothing ever fetches.
    GET /cdn-cgi/trace               -> 200   the edge is healthy.
    GET the real decoder .js         -> 200   the decoder is being served.
    a real browser on production     -> 0 mangled spans, href = mailto:...

  The 404 was true. "The decoder is broken" was false. The gap between them is
  inferential distance, and only a control closes it.

  To claim USER IMPACT you need a user-visible measurement (a real browser
  render), never a status code.
EOF
}

_pk_explain_dns() {
  cat <<'EOF'

── dns ─────────────────────────────────────────────────────────────────────
  A negative (NXDOMAIN / empty answer) LICENSES exactly this:
    "this resolver, at this moment, returned no record for this name."

  It does NOT license:
    - "the domain does not exist"   -> split-horizon DNS, VPN, captive portal
    - "the record was never created"-> propagation delay is minutes to hours
    - "the service is down"         -> DNS is not the service
    - a conclusion about a DIFFERENT record type than the one you asked for

  The control resolves the parent zone (or an IANA-reserved name). If the
  control also returns nothing, you have learned about YOUR RESOLVER and
  nothing at all about the subject.
EOF
}

_pk_explain_file() {
  cat <<'EOF'

── file ────────────────────────────────────────────────────────────────────
  A negative ([ -e ] false) LICENSES exactly this:
    "this process, with this uid and this cwd, could not stat this path."

  It does NOT license:
    - "the file was never created"  -> wrong cwd / wrong base path is far more common
    - "the step did not run"        -> it may have written somewhere else
    - "the data is gone"            -> a permission-denied traverse reads as false
    - "the build is broken"

  The control lists the CONTAINING DIRECTORY. If the parent is missing too,
  you are looking in the wrong place — the file is not the finding. If the
  parent exists but is not traversable, you cannot distinguish "absent" from
  "not permitted to see", and the probe is inconclusive by construction.
EOF
}

_pk_explain_cmd() {
  cat <<'EOF'

── cmd ─────────────────────────────────────────────────────────────────────
  A negative (command -v fails, or exit 127) LICENSES exactly this:
    "this name is not on THIS PATH, in THIS process."

  It does NOT license:
    - "the tool is not installed"   -> it may be off-PATH (homebrew vs env -i)
    - "this host cannot do X"       -> that is the capability-grounding error:
                                       a dead route is never a missing capability
    - "the feature is unsupported"

  WORKED EXAMPLE (this repo, macOS door 2): stock macOS has no GNU `timeout`.
  Inside `out="$(timeout N cmd)" || echo ''` that 127 is NOT a timeout — it is
  command-not-found, so the caller silently took its error path on every macOS
  session and the decision-review tribunal was never consulted. Nothing failed
  loudly. The control (`command -v sh`) is what separates "this name is absent"
  from "lookup itself is broken / PATH is empty".
EOF
}

_pk_explain() {
  _pk_explain_head
  case "${1:-all}" in
    http) _pk_explain_http ;;
    dns)  _pk_explain_dns ;;
    file) _pk_explain_file ;;
    cmd)  _pk_explain_cmd ;;
    *)    _pk_explain_http; _pk_explain_dns; _pk_explain_file; _pk_explain_cmd ;;
  esac
  cat <<'EOF'

── exit codes ──────────────────────────────────────────────────────────────
  0  subject POSITIVE      nothing negative to diagnose
  1  CONFIRMED             subject negative, control positive -> the negative is real
  2  SUSPECT               the control ALSO failed -> fix the probe before believing it
  3  INCONCLUSIVE          the control could not run -> evidence about your instrument
  64 usage error

EOF
}

_pk_usage() {
  cat <<'EOF'
probe-kit.sh — ready-made CONTROL probes. A negative result is not a diagnosis
until a positive control on the same subsystem has been observed.

  probe-kit.sh http <url>    [--control <url>]  [--timeout <s>]
  probe-kit.sh dns  <host>   [--control <host>]
  probe-kit.sh file <path>   [--control <dir>]
  probe-kit.sh cmd  <name>   [--control <name>]
  probe-kit.sh --explain [http|dns|file|cmd]
  probe-kit.sh --self-test

Exit: 0 positive · 1 negative CONFIRMED · 2 control ALSO failed · 3 inconclusive · 64 usage
EOF
}

# ── --self-test ──────────────────────────────────────────────────────────────
# "Prove the instrument before believing its verdict." Every subtest below is
# offline-capable: the http fixtures use a loopback server, never the network.

PK_ST_PASS=0
PK_ST_FAIL=0
PK_ST_SKIP=0
# Global on purpose: the EXIT trap fires long after _pk_self_test's locals are
# out of scope, and under `set -u` a trap referencing a dead local aborts the
# cleanup — leaving the temp tree behind while the run still reports success.
PK_ST_TD=""

_pk_st_cleanup() {
  [ -n "${PK_ST_TD:-}" ] && [ -d "${PK_ST_TD}" ] && rm -rf "${PK_ST_TD}"
  return 0
}

_st_ok()   { PK_ST_PASS=$((PK_ST_PASS+1)); printf '  %s✓%s %s\n' "$C_GRN" "$C_OFF" "$1"; }
_st_bad()  { PK_ST_FAIL=$((PK_ST_FAIL+1)); printf '  %s✗%s %s\n' "$C_RED" "$C_OFF" "$1"; }
_st_skip() { PK_ST_SKIP=$((PK_ST_SKIP+1)); printf '  %s! LOUD SKIP (NOT A PASS):%s %s\n' "$C_YEL" "$C_OFF" "$1"; }

# Run a probe quietly and echo its exit code.
_st_rc() {
  "$@" >/dev/null 2>&1
  printf '%s' "$?"
}

_pk_self_test() {
  local rc port srv pid tries got

  printf '\n%sprobe-kit %s — self-test%s\n' "$C_BLD" "$PK_VERSION" "$C_OFF"
  printf '%sEvery subtest is offline-capable. A skip is never a pass.%s\n\n' "$C_DIM" "$C_OFF"

  # ── TEETH: the verdict resolver must be able to fail ──────────────────────
  printf '── TEETH: the verdict resolver produces four DISTINCT outcomes ──\n'
  local v1 v2 v3 v4
  v1="$(_pk_verdict POSITIVE POSITIVE)"
  v2="$(_pk_verdict NEGATIVE POSITIVE)"
  v3="$(_pk_verdict NEGATIVE NEGATIVE)"
  v4="$(_pk_verdict NEGATIVE UNRUN)"
  [ "$v1" = "POSITIVE" ]     && _st_ok "positive/positive -> POSITIVE"     || _st_bad "positive/positive -> $v1"
  [ "$v2" = "CONFIRMED" ]    && _st_ok "negative/positive -> CONFIRMED"    || _st_bad "negative/positive -> $v2"
  [ "$v3" = "SUSPECT" ]      && _st_ok "negative/negative -> SUSPECT"      || _st_bad "negative/negative -> $v3"
  [ "$v4" = "INCONCLUSIVE" ] && _st_ok "negative/unrun    -> INCONCLUSIVE" || _st_bad "negative/unrun -> $v4"
  if [ "$v1" != "$v2" ] && [ "$v2" != "$v3" ] && [ "$v3" != "$v4" ] && [ "$v1" != "$v3" ] \
     && [ "$v1" != "$v4" ] && [ "$v2" != "$v4" ]; then
    _st_ok "all four outcomes differ — a constant-verdict stub cannot pass this"
  else
    _st_bad "outcomes collapse — a probe that cannot fail is not a probe"
  fi
  # exit-code contract
  [ "$(_pk_exit_for POSITIVE)" = "0" ] && [ "$(_pk_exit_for CONFIRMED)" = "1" ] \
    && [ "$(_pk_exit_for SUSPECT)" = "2" ] && [ "$(_pk_exit_for INCONCLUSIVE)" = "3" ] \
    && _st_ok "exit-code contract 0/1/2/3 holds" || _st_bad "exit-code contract drifted"

  PK_ST_TD="$(mktemp -d 2>/dev/null)" || { printf 'mktemp failed\n'; return 1; }
  trap _pk_st_cleanup EXIT
  local td="$PK_ST_TD"

  # ── file ──────────────────────────────────────────────────────────────────
  printf '\n── file ──\n'
  printf 'x' > "$td/present.txt"
  rc="$(_st_rc _pk_probe_file "$td/present.txt" "")"
  [ "$rc" = "0" ] && _st_ok "existing file -> 0 (POSITIVE)" || _st_bad "existing file -> $rc (want 0)"
  rc="$(_st_rc _pk_probe_file "$td/absent.txt" "")"
  [ "$rc" = "1" ] && _st_ok "missing file, parent listable -> 1 (CONFIRMED)" || _st_bad "missing file -> $rc (want 1)"
  rc="$(_st_rc _pk_probe_file "$td/no/such/dir/absent.txt" "")"
  [ "$rc" = "2" ] && _st_ok "missing file, parent ALSO missing -> 2 (SUSPECT)" || _st_bad "missing parent -> $rc (want 2)"

  # ── cmd ───────────────────────────────────────────────────────────────────
  printf '\n── cmd ──\n'
  rc="$(_st_rc _pk_probe_cmd sh "")"
  [ "$rc" = "0" ] && _st_ok "cmd sh -> 0 (POSITIVE)" || _st_bad "cmd sh -> $rc (want 0)"
  rc="$(_st_rc _pk_probe_cmd probe-kit-no-such-command-xyzzy "")"
  [ "$rc" = "1" ] && _st_ok "absent command, control found -> 1 (CONFIRMED)" || _st_bad "absent command -> $rc (want 1)"
  # A broken PATH must read as SUSPECT, never as "the command is absent".
  # NOTE: the assignment goes INSIDE the subshell — `VAR=x func` persists after
  # the call in bash, which would silently break every later subtest.
  rc="$( PATH="/probe-kit/nonexistent"; _st_rc _pk_probe_cmd git "" )"
  [ "$rc" = "2" ] && _st_ok "broken PATH -> 2 (SUSPECT, not a false 'absent')" || _st_bad "broken PATH -> $rc (want 2)"

  # ── http (loopback only — no network) ─────────────────────────────────────
  printf '\n── http (loopback fixture — no network required) ──\n'
  if ! command -v curl >/dev/null 2>&1; then
    _st_skip "curl absent — the http probe cannot be exercised on this host"
  else
    # unroutable loopback port: both subject and control must fail to connect
    rc="$(PROBE_KIT_TIMEOUT=2 _st_rc _pk_probe_http "http://127.0.0.1:1/whatever" "")"
    [ "$rc" = "3" ] && _st_ok "unreachable host -> 3 (INCONCLUSIVE, degrades without hanging)" \
                    || _st_bad "unreachable host -> $rc (want 3)"

    if command -v python3 >/dev/null 2>&1; then
      srv="$td/www"; mkdir -p "$srv"; printf 'ok' > "$srv/index.html"
      port="$(python3 -c 'import socket;s=socket.socket();s.bind(("127.0.0.1",0));print(s.getsockname()[1]);s.close()' 2>/dev/null)"
      if [ -n "${port:-}" ]; then
        python3 -m http.server "$port" --bind 127.0.0.1 --directory "$srv" >/dev/null 2>&1 &
        pid=$!
        tries=0; got=""
        while [ "$tries" -lt 40 ]; do
          got="$(curl -sS -o /dev/null -w '%{http_code}' -m 2 "http://127.0.0.1:${port}/" 2>/dev/null)"
          [ "$got" = "200" ] && break
          tries=$((tries+1)); sleep 0.1
        done
        if [ "$got" = "200" ]; then
          rc="$(PROBE_KIT_TIMEOUT=5 _st_rc _pk_probe_http "http://127.0.0.1:${port}/" "")"
          [ "$rc" = "0" ] && _st_ok "200 subject -> 0 (POSITIVE)" || _st_bad "200 subject -> $rc (want 0)"
          rc="$(PROBE_KIT_TIMEOUT=5 _st_rc _pk_probe_http "http://127.0.0.1:${port}/definitely-not-here" "")"
          [ "$rc" = "1" ] && _st_ok "404 subject + 200 control -> 1 (CONFIRMED) — the incident's shape" \
                          || _st_bad "404 subject + 200 control -> $rc (want 1)"
        else
          _st_skip "loopback http server did not come up — http CONFIRMED path unexercised"
        fi
        kill "$pid" >/dev/null 2>&1
        wait "$pid" >/dev/null 2>&1
      else
        _st_skip "could not reserve a loopback port — http CONFIRMED path unexercised"
      fi
    else
      _st_skip "python3 absent — http CONFIRMED path unexercised"
    fi

    # control derivation is pure and must special-case the edge-health endpoint
    got="$(_pk_http_control_url 'https://www.ravenpower.net/cdn-cgi/l/email-protection')"
    [ "$got" = "https://www.ravenpower.net/cdn-cgi/trace" ] \
      && _st_ok "/cdn-cgi/* control resolves to /cdn-cgi/trace (the incident's control)" \
      || _st_bad "/cdn-cgi/* control resolved to '$got'"
    got="$(_pk_http_control_url 'https://example.org/a/b/c')"
    [ "$got" = "https://example.org/" ] \
      && _st_ok "ordinary path control resolves to the site root on the same host" \
      || _st_bad "ordinary path control resolved to '$got'"
  fi

  # ── a control that IS the subject is not a control (plan.md §2.4) ──────────
  printf '\n── "a re-run is not a control" guard ──\n'
  got="$(_pk_http_control_url 'https://example.org/cdn-cgi/trace')"
  [ "$got" = "https://example.org/" ] \
    && _st_ok "/cdn-cgi/trace does NOT become its own control (falls back to the root)" \
    || _st_bad "/cdn-cgi/trace control resolved to '$got' — a re-run of the subject"
  got="$(_pk_http_control_url 'https://example.org/')"
  [ "$got" != "https://example.org/" ] \
    && _st_ok "the site root does NOT become its own control" \
    || _st_bad "the site root resolved to itself as control"
  # explicit identical --control must be refused, not silently trusted
  rc="$(_st_rc _pk_probe_file "$td/present.txt" "$td/present.txt")"
  [ "$rc" = "3" ] && _st_ok "explicit --control identical to the subject -> 3 (refused as not-a-control)" \
                  || _st_bad "identical --control -> $rc (want 3)"
  rc="$(_st_rc _pk_probe_cmd sh sh)"
  [ "$rc" = "3" ] && _st_ok "cmd with --control equal to the subject -> 3 (refused)" \
                  || _st_bad "cmd identical control -> $rc (want 3)"
  # ...and the default control must never collide with the subject
  rc="$(_st_rc _pk_probe_cmd sh "")"
  [ "$rc" = "0" ] && _st_ok "cmd sh picks a different default control (still POSITIVE)" \
                  || _st_bad "cmd sh default control -> $rc (want 0)"

  # ── dns ───────────────────────────────────────────────────────────────────
  printf '\n── dns ──\n'
  # .invalid is reserved and can never resolve, so both sides must fail. Whether
  # that reads as SUSPECT (resolver answered NXDOMAIN) or INCONCLUSIVE (no
  # resolver reachable) depends on connectivity — but it must NEVER read 0 or 1.
  rc="$(_st_rc _pk_probe_dns "probe-kit.self-test.invalid" "probe-kit.control.invalid")"
  if [ "$rc" = "2" ] || [ "$rc" = "3" ]; then
    _st_ok "reserved .invalid names -> $rc (2 SUSPECT or 3 INCONCLUSIVE, never a false negative-confirmed)"
  else
    _st_bad "reserved .invalid names -> $rc (want 2 or 3)"
  fi
  got="$(_pk_dns_control_host 'api.staging.example.com')"
  [ "$got" = "staging.example.com" ] && _st_ok "control host = parent zone for a 4-label name" \
                                     || _st_bad "control host resolved to '$got'"
  got="$(_pk_dns_control_host 'example.com')"
  [ "$got" = "example.net" ] && _st_ok "2-label subject falls back to a reserved always-resolvable control" \
                             || _st_bad "2-label fallback resolved to '$got'"

  # ── --explain must actually say something about every probe type ──────────
  printf '\n── --explain ──\n'
  got="$(_pk_explain all 2>/dev/null)"
  local missing=""
  case "$got" in *"── http ─"*) : ;; *) missing="$missing http" ;; esac
  case "$got" in *"── dns ─"*)  : ;; *) missing="$missing dns" ;; esac
  case "$got" in *"── file ─"*) : ;; *) missing="$missing file" ;; esac
  case "$got" in *"── cmd ─"*)  : ;; *) missing="$missing cmd" ;; esac
  [ -z "$missing" ] && _st_ok "--explain covers http, dns, file and cmd" \
                    || _st_bad "--explain is missing:$missing"
  case "$got" in
    *"does NOT license"*) _st_ok "--explain states what a negative does NOT license" ;;
    *)                    _st_bad "--explain never says what a negative does NOT license" ;;
  esac

  printf '\n%s──────────────────────────────────────────────%s\n' "$C_DIM" "$C_OFF"
  printf '  probe-kit self-test: %d passed, %d failed, %d loud-skipped\n' \
    "$PK_ST_PASS" "$PK_ST_FAIL" "$PK_ST_SKIP"
  if [ "$PK_ST_FAIL" -ne 0 ]; then
    printf '  %sThe kit is not trustworthy on this host. Fix it before using a verdict.%s\n\n' "$C_RED" "$C_OFF"
    return 1
  fi
  printf '  %sThe instrument can distinguish all four outcomes on this host.%s\n\n' "$C_GRN" "$C_OFF"
  return 0
}

# ── main ─────────────────────────────────────────────────────────────────────

main() {
  local kind target control=""
  [ $# -eq 0 ] && { _pk_usage; return 64; }

  case "$1" in
    -h|--help)   _pk_usage; return 0 ;;
    --version)   printf 'probe-kit %s\n' "$PK_VERSION"; return 0 ;;
    --explain)   shift; _pk_explain "${1:-all}"; return 0 ;;
    --self-test) _pk_self_test; return $? ;;
  esac

  kind="$1"; shift
  case "$kind" in
    http|dns|file|cmd) : ;;
    *) printf 'probe-kit: unknown probe type "%s"\n\n' "$kind" >&2; _pk_usage >&2; return 64 ;;
  esac

  [ $# -eq 0 ] && { printf 'probe-kit: %s needs a target\n\n' "$kind" >&2; _pk_usage >&2; return 64; }
  target="$1"; shift

  while [ $# -gt 0 ]; do
    case "$1" in
      --control) shift; [ $# -gt 0 ] || { printf 'probe-kit: --control needs a value\n' >&2; return 64; }
                 control="$1" ;;
      --timeout) shift; [ $# -gt 0 ] || { printf 'probe-kit: --timeout needs a value\n' >&2; return 64; }
                 PK_TIMEOUT="$1" ;;
      *) printf 'probe-kit: unknown option "%s"\n' "$1" >&2; return 64 ;;
    esac
    shift
  done

  case "$kind" in
    http) _pk_probe_http "$target" "$control" ;;
    dns)  _pk_probe_dns  "$target" "$control" ;;
    file) _pk_probe_file "$target" "$control" ;;
    cmd)  _pk_probe_cmd  "$target" "$control" ;;
  esac
}

main "$@"
