// ---------------------------------------------------------------------------
// CSV row serialization with a spreadsheet formula-injection guard (CWE-1236)
// (FORGE dashboard-top1pct P2-14, 2026-09-03 — added after security review).
//
// ⛔ CSV quoting does NOT neutralize formula injection. Excel/Sheets/
// LibreOffice decide a cell is a formula from its LEADING character AFTER
// the CSV parser has already stripped the surrounding quotes — a value like
// `"=WEBSERVICE(...)"` is still parsed as a formula by the spreadsheet even
// though it was correctly quoted as a single CSV field. Every exported
// dimension in this scaffold's export routes is attacker-influenceable in a
// normal ELT topology (a customer name, an external ID) without requiring
// cross-tenant access — the attacker only needs write access inside their
// OWN tenant's upstream source data.
// ---------------------------------------------------------------------------

const FORMULA_LEAD = /^[=+\-@\t\r]/;

/**
 * Serializes one CSV row. Neutralizes a leading formula-trigger character
 * with a literal-text apostrophe prefix (the standard mitigation for this
 * class — Excel/Sheets both treat a leading `'` as "force text"). This
 * mutates the value; that tradeoff is deliberate (silently dropping the row
 * would be data loss, and there is no way to render an untyped CSV cell that
 * is simultaneously formula-safe and byte-identical to the source value).
 */
export function toCsvRow(values: unknown[]): string {
  return values
    .map((v) => {
      let s = String(v ?? "");
      if (FORMULA_LEAD.test(s)) s = `'${s}`;
      // Quote any field containing a comma, quote, or line break (LF or
      // CR — a bare CR alone is enough to split a row in some parsers).
      return /["\r\n,]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    })
    .join(",");
}
