import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import path from "node:path";

/**
 * Rubric #4 (secret / env hygiene), made executable: scan every generated
 * source file in this tier for secret-SHAPED strings. Real Square secrets
 * have recognizable prefixes (`sq0atp-`, `sq0csp-`, `sandbox-sq0atb-`,
 * `EAAA...`) or look like long opaque tokens; a scaffolded template must
 * never contain one, only placeholders.
 */

const SECRET_SHAPED_PATTERNS = [
  /sq0at[pb]-[A-Za-z0-9_-]{20,}/, // Square production/sandbox access token
  /sq0csp-[A-Za-z0-9_-]{20,}/, // Square application secret
  /EAAA[A-Za-z0-9_-]{20,}/, // Square access token (current prefix)
];

const TIER_ROOT = path.resolve(import.meta.dirname, "..");

function listTsFiles(dir: string): string[] {
  const out: string[] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name === "tests") continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      out.push(...listTsFiles(full));
    } else if (entry.name.endsWith(".ts")) {
      out.push(full);
    }
  }
  return out;
}

test("no secret-shaped strings in generated source (rubric #4)", () => {
  const files = listTsFiles(TIER_ROOT);
  assert.ok(files.length > 0, "expected to find .ts source files to scan");

  for (const file of files) {
    const contents = readFileSync(file, "utf8");
    for (const pattern of SECRET_SHAPED_PATTERNS) {
      assert.equal(
        pattern.test(contents),
        false,
        `${file} contains a secret-shaped string matching ${pattern}`,
      );
    }
  }
});

test(".env.example carries only placeholders, never a live-looking value", () => {
  const contents = readFileSync(path.join(TIER_ROOT, ".env.example"), "utf8");
  for (const pattern of SECRET_SHAPED_PATTERNS) {
    assert.equal(pattern.test(contents), false, `.env.example matches ${pattern}`);
  }
  // Every credential-shaped var must be the literal placeholder "xxx".
  for (const line of contents.split("\n")) {
    if (/^SQUARE_(ACCESS_TOKEN|APPLICATION_ID|LOCATION_ID|WEBHOOK_SIGNATURE_KEY)=/.test(line)) {
      assert.equal(line.trim(), line.split("=")[0] + "=xxx", `${line} is not a bare placeholder`);
    }
  }
});
