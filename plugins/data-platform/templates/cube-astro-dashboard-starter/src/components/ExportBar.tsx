"use client";

import { useState } from "react";

/**
 * The two export mechanisms this starter implements (FORGE dashboard-top1pct
 * P2-14, 2026-09-03) — see knowledge/dashboard-export-and-delivery-2026.md
 * for the full mechanism comparison. Identical to the Next.js starter's
 * ExportBar.tsx (plain React, no framework-specific API), rendered inside
 * DashboardIsland since it's genuinely interactive — unlike Title/Subtitle,
 * which stay outside the island (see DashboardIsland.tsx's header comment).
 *
 * `data-export-hide` matches src/styles/globals.css's `@media print` rule —
 * this bar must not appear in the printed output.
 */
export function ExportBar() {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleDownloadCsv() {
    setDownloading(true);
    setError(null);
    try {
      const res = await fetch("/api/export");
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error ?? `export failed: ${res.status}`);
      }
      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition") ?? "";
      const match = /filename="([^"]+)"/.exec(disposition);
      const filename = match?.[1] ?? "dashboard-export.csv";

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div data-export-hide className="mb-4 flex items-center gap-3">
      <button
        type="button"
        onClick={() => window.print()}
        className="rounded-md border border-tremor-border px-3 py-1.5 text-sm font-medium text-tremor-content-strong hover:bg-tremor-background-muted"
      >
        Print / Save as PDF
      </button>
      <button
        type="button"
        onClick={handleDownloadCsv}
        disabled={downloading}
        className="rounded-md border border-tremor-border px-3 py-1.5 text-sm font-medium text-tremor-content-strong hover:bg-tremor-background-muted disabled:opacity-50"
      >
        {downloading ? "Preparing…" : "Download CSV"}
      </button>
      {error && (
        <span role="alert" className="text-xs text-rose-600">
          {error}
        </span>
      )}
    </div>
  );
}
