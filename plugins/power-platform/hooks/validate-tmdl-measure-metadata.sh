#!/usr/bin/env bash
# validate-tmdl-measure-metadata.sh
# PostToolUse hook for Edit | Write | MultiEdit on Power BI TMDL files (*.tmdl).
#
# Enforces the measure-metadata discipline (see plugins/power-platform/best-practices/
# enforce-measure-metadata.md): every model measure should carry a DESCRIPTION
# (a `///` doc comment), a `formatString`, and a `displayFolder`. These are TOM
# properties and a standard Tabular Editor Best-Practice-Analyzer expectation; they
# make a model discoverable, self-documenting, consistently formatted, and AI-ready.
#
# DETERMINISTIC + ADVISORY: fires on a structural pattern (a `measure` block missing
# one of the three), not by LLM judgment. Prints warnings to stderr so Claude and the
# user both see them, but exits 0 — it never blocks the edit (to enforce, flip the final
# `exit 0` to `exit 1`). FAIL-SAFE: any error exits 0. Discovery-credit: the Power BI
# agentic-development hook pattern this mirrors is Data Goblins' work
# (https://github.com/data-goblin/power-bi-agentic-development) — re-implemented here in
# our own words against the underlying TOM/TMDL facts.
#
# HONEST SCOPE: this is a single-file structural check. It CANNOT validate cross-model
# referential integrity, DAX correctness against a live model, or whether a description
# is meaningful — only that the three metadata properties are structurally present. Those
# deeper checks need a connected model (out of scope for a file-edit hook).

set -euo pipefail

file="${1:-}"
[[ -z "$file" ]] && exit 0
[[ ! -f "$file" ]] && exit 0
# Only TMDL files.
case "$file" in
  *.tmdl) ;;
  *) exit 0 ;;
esac

# Best-effort TMDL measure-block scan. A measure is `<indent>measure <name> = ...`.
# Its property lines are MORE-indented lines that follow it until the next object at
# the same-or-lower indent (measure/column/table/hierarchy/partition/calculationGroup)
# or EOF. A description is a `///` doc-comment line immediately preceding the measure.
warnings="$(
  awk '
    function indent(s,   i,c,n) { n=0; for(i=1;i<=length(s);i++){c=substr(s,i,1); if(c==" "||c=="\t") n++; else break} return n }
    function flush(   miss) {
      if (in_measure) {
        miss=""
        if (!has_desc) miss=miss " description(///)"
        if (!has_fmt)  miss=miss " formatString"
        if (!has_df)   miss=miss " displayFolder"
        if (miss!="") printf("  measure %s — missing:%s\n", mname, miss)
      }
      in_measure=0
    }
    {
      line=$0
      # strip trailing CR
      sub(/\r$/,"",line)
      # blank line: does not end a property block, does not reset desc-pending mid-doc
      if (line ~ /^[ \t]*$/) { next }
      ind=indent(line)
      stripped=line; sub(/^[ \t]+/,"",stripped)

      # doc comment line
      if (stripped ~ /^\/\/\//) { doc_pending=1; doc_seen_blank=0; next }

      # measure definition
      if (stripped ~ /^measure[ \t]/) {
        flush()                      # finalize any previous measure
        in_measure=1; m_ind=ind; has_fmt=0; has_df=0
        has_desc=doc_pending
        # name = between "measure" and "=" (or rest of line if no =)
        nm=stripped; sub(/^measure[ \t]+/,"",nm)
        if (nm ~ /=/) sub(/[ \t]*=.*/,"",nm)
        gsub(/^[ \t]+|[ \t]+$/,"",nm)
        mname=nm
        doc_pending=0
        next
      }

      # any other object keyword at <= measure indent ends the measure block
      if (in_measure && ind <= m_ind && stripped ~ /^(measure|column|table|hierarchy|partition|calculationGroup|relationship|role|expression|model|database)[ \t]/) {
        flush()
      }

      # property lines inside the measure block (more-indented)
      if (in_measure && ind > m_ind) {
        if (stripped ~ /^formatString[ \t]*[:=]/) has_fmt=1
        if (stripped ~ /^displayFolder[ \t]*[:=]/) has_df=1
        # a description can also be a `description = "..."` property (rare in TMDL)
        if (stripped ~ /^description[ \t]*[:=]/) has_desc=1
      }

      # a non-doc, non-blank line clears a stray pending doc that was not immediately a measure
      doc_pending=0
    }
    END { flush() }
  ' "$file" 2>/dev/null || true
)"

if [[ -n "$warnings" ]]; then
  {
    echo "⚠️  TMDL measure-metadata (advisory) — $file"
    echo "$warnings"
    echo "  → every measure should have a /// description, a formatString, and a displayFolder."
    echo "    See plugins/power-platform/best-practices/enforce-measure-metadata.md."
  } >&2
fi

exit 0
