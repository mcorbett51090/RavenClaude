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
// A plain number (e.g. a refund of -12.50) cannot be a formula, so it is
// left as-is; prefixing it would turn a numeric column into text.
const PLAIN_NUMBER = /^[+-]?\d+(\.\d+)?([eE][+-]?\d+)?$/;

export function toCsvRow(values: unknown[]): string {
  return values
    .map((v) => {
      let s = String(v ?? "");
      if (FORMULA_LEAD.test(s) && !PLAIN_NUMBER.test(s)) s = `'${s}`;
      return /["\r\n,]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    })
    .join(",");
}
