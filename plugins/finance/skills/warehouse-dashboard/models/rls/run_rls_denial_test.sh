#!/usr/bin/env bash
# run_rls_denial_test.sh — stand up a throwaway Postgres and EXECUTE the shipped
# FORCE-RLS policy + cross-entity denial test against it. No live credentials, no
# warehouse — just Docker + a disposable postgres:16 container.
#
# This is what moves the warehouse-dashboard RLS from "specified" to "executed": it
# proves the load-bearing control — a viewer granted entity A cannot see entity B even
# with an explicit filter, and an empty/unset grant denies all (fail-closed). It is
# the go-live gate the security review requires for the DB layer. (The Cube layer
# still needs a running Cube instance — see the SKILL.)
#
# Usage:  bash run_rls_denial_test.sh          # needs docker on PATH
# Exit 0 iff every assertion holds; non-zero otherwise (suitable as a CI gate).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CTR="fin-rls-denial-$$"
PG_IMAGE="${PG_IMAGE:-postgres:16-alpine}"

command -v docker >/dev/null 2>&1 || { echo "SKIP: docker not on PATH (this test needs a container)"; exit 0; }

cleanup() { docker rm -f "$CTR" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "== starting $PG_IMAGE ($CTR) =="
docker run -d --name "$CTR" -e POSTGRES_PASSWORD=x -e POSTGRES_DB=closedb "$PG_IMAGE" >/dev/null
for _ in $(seq 1 60); do docker exec "$CTR" pg_isready -U postgres >/dev/null 2>&1 && break; sleep 1; done

psql() { docker exec -i "$CTR" psql -U postgres -d closedb -v ON_ERROR_STOP=1 "$@"; }

echo "== 1. bootstrap marts =="
psql -q < "$HERE/bootstrap_test_schema.sql"
echo "== 2. apply the SHIPPED close_rls_policies.sql (roles, ENABLE+FORCE RLS, array policy) =="
psql -q < "$HERE/close_rls_policies.sql" >/dev/null
echo "== 3. grant the ELT build role (what dbt-project-scaffolding does) =="
psql -q -c "GRANT USAGE ON SCHEMA analytics TO finance_close_build_role;
            GRANT INSERT ON ALL TABLES IN SCHEMA analytics TO finance_close_build_role;"
echo "== 4. run the SHIPPED cross-entity denial test =="
out="$(psql -t -A < "$HERE/rls_cross_entity_denial_test.sql")"
echo "$out" | grep '^RESULT ' | sed 's/^/   /'

fail=0
check() { # name expected actual
  if [ "$2" = "$3" ]; then echo "   PASS $1 ($3)"; else echo "   FAIL $1 (got $3, expected $2)"; fail=1; fi
}
g=$(echo "$out" | sed -n 's/^RESULT granted=\([0-9]*\).*/\1/p')
l=$(echo "$out" | sed -n 's/^RESULT leaked=\([0-9]*\).*/\1/p')
u=$(echo "$out" | sed -n 's/^RESULT unset=\([0-9]*\).*/\1/p')
e=$(echo "$out" | sed -n 's/^RESULT empty=\([0-9]*\).*/\1/p')
p=$(echo "$out" | sed -n 's/^RESULT portfolio_AC=\([0-9]*\).*/\1/p')
echo "== assertions =="
check "granted portfolio {A} sees A only"        1 "$g"
check "explicit filter for B LEAKS nothing"      0 "$l"
check "unset context denies all (fail-closed)"   0 "$u"
check "empty {} grant denies all"                0 "$e"
check "array claim {A,C} returns the 2-entity portfolio" 2 "$p"

if [ "$fail" = 0 ]; then
  echo "== ✅ FORCE-RLS cross-entity denial PROVEN against $PG_IMAGE =="; exit 0
else
  echo "== ❌ RLS denial test FAILED =="; exit 1
fi
