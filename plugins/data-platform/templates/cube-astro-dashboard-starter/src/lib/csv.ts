// ---------------------------------------------------------------------------
// CSV row serialization with a spreadsheet formula-injection guard (CWE-1236)
// — Astro-side twin of the Next.js starter's lib/csv.ts (FORGE dashboard-
// top1pct P2-14, 2026-09-03, added after security review).
//
// ⛔ CSV quoting does NOT neutralize formula injection. Excel/Sheets/
// LibreOffice decide a cell is a formula from its LEADING character AFTER
// the CSV parser has already stripped the surrounding quotes.
// ---------------------------------------------------------------------------

const FORMULA_LEAD = /^[=+\-@\t\r]/;

export function toCsvRow(values: unknown[]): string {
  return values
    .map((v) => {
      let s = String(v ?? "");
      if (FORMULA_LEAD.test(s)) s = `'${s}`;
      return /["\r\n,]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    })
    .join(",");
}
