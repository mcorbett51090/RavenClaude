/**
 * Secret-hygiene test (CLAUDE.md §2 #4 / §4 dimension 4): production source
 * in this tier must read secrets from `process.env` only — never a literal
 * key-shaped string.
 *
 * Scope: this scans the tier's PRODUCTION files (everything except this
 * `tests/` directory and `.env.example`, whose entire job is to hold
 * placeholder-shaped values). Test fixtures elsewhere in `tests/` legitimately
 * contain fake-but-key-shaped strings (to exercise the signature parser) and
 * are intentionally out of scope here — that's the same reason `.env.example`
 * is excluded rather than "the only allowed file" in the literal sense.
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const TIER_ROOT = join(import.meta.dirname, "..");

// Real Stripe key/secret shapes, long enough to distinguish a genuine
// credential from a short illustrative fragment (e.g. "sk_test_xxx" in docs).
const SECRET_SHAPED_PATTERNS = [
  /\b(sk|rk)_(live|test)_[A-Za-z0-9]{16,}\b/,
  /\bwhsec_[A-Za-z0-9]{16,}\b/,
  /\bpk_(live|test)_[A-Za-z0-9]{16,}\b/,
];

function listProductionFiles(dir: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir)) {
    if (entry === "tests" || entry === "node_modules") continue;
    const full = join(dir, entry);
    const stat = statSync(full);
    if (stat.isDirectory()) {
      out.push(...listProductionFiles(full));
    } else if (/\.(ts|tsx)$/.test(entry)) {
      out.push(full);
    }
  }
  return out;
}

test("no secret-shaped string appears in production source", () => {
  const offenders: string[] = [];
  for (const file of listProductionFiles(TIER_ROOT)) {
    const content = readFileSync(file, "utf8");
    for (const pattern of SECRET_SHAPED_PATTERNS) {
      if (pattern.test(content)) {
        offenders.push(`${file} matches ${pattern}`);
      }
    }
  }
  assert.deepEqual(offenders, []);
});
