// ---------------------------------------------------------------------------
// Superset embed (React component) — RUNNABLE, promoted from
// superset-embed-iframe.tsx.md at v0.2.0.
// ---------------------------------------------------------------------------
// SECURITY (fixed after mandatory security review — see plugin CLAUDE.md §9):
// by design, this component does not resolve tenantId and does not call
// Superset's guest-token endpoint from the client. It calls exactly one host
// endpoint (guestTokenEndpoint) with only `dashboardId`; the server side
// (superset-guest-token-endpoint.ts) resolves tenantId/userId from a
// server-verified session and performs the JWT + guest-token exchange.
//
// Pinned at promotion time: @superset-ui/embedded-sdk ^0.1.3, React 18.
// KNOWN GAP: not yet run against a live Superset instance in this repo.
//
// Companion docs:
//   - ./superset-guest-token-endpoint.ts — the server-side counterpart (required)
//   - ../skills/embed-csp-and-iframe-sandboxing/SKILL.md
// ---------------------------------------------------------------------------

import { embedDashboard } from "@superset-ui/embedded-sdk";
import { useEffect, useRef, useState } from "react";

export interface SupersetTheme {
  colorPrimary?: string;
  colorBgBase?: string;
  colorTextBase?: string;
}

export interface SupersetEmbedProps {
  /** Superset dashboard UUID — the engagement-specific dashboard to render. */
  dashboardId: string;
  /** Superset instance origin, e.g. "https://superset.client-domain.com". */
  supersetDomain: string;
  /**
   * Host endpoint implementing superset-guest-token-endpoint.ts's
   * handleGuestTokenRequest, called with only `{ dashboardId }`. Tenant
   * scope is resolved server-side from the session — this component's own
   * code path has no tenantId variable at all, by design.
   */
  guestTokenEndpoint: string;
  height?: number;
  themeOverride?: SupersetTheme;
  onError?: (error: Error) => void;
}

export function SupersetEmbed({
  dashboardId,
  supersetDomain,
  guestTokenEndpoint,
  height = 800,
  themeOverride,
  onError,
}: SupersetEmbedProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    if (!containerRef.current) return;
    let cancelled = false;

    async function mount() {
      try {
        const res = await fetch(guestTokenEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dashboardId }),
        });
        if (!res.ok) throw new Error(`guest token endpoint failed: ${res.status}`);
        const { guestToken } = await res.json();

        if (cancelled || !containerRef.current) return;

        await embedDashboard({
          id: dashboardId,
          supersetDomain,
          mountPoint: containerRef.current,
          fetchGuestToken: () => Promise.resolve(guestToken),
          dashboardUiConfig: {
            hideTitle: true,
            hideChartControls: false,
            ...(themeOverride && { theme: themeOverride }),
          },
        });

        if (!cancelled) setStatus("ready");
      } catch (err) {
        if (!cancelled) {
          setStatus("error");
          onError?.(err instanceof Error ? err : new Error(String(err)));
        }
      }
    }

    mount();

    // Resize/theme postMessage — origin MUST be checked (see
    // embed-csp-and-iframe-sandboxing/SKILL.md "Anti-patterns").
    function handleMessage(event: MessageEvent) {
      if (event.origin !== new URL(supersetDomain).origin) return;
      if (typeof event.data !== "object" || event.data === null || !("type" in event.data)) return;
    }
    window.addEventListener("message", handleMessage);

    return () => {
      cancelled = true;
      window.removeEventListener("message", handleMessage);
    };
  }, [dashboardId, supersetDomain, guestTokenEndpoint]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: `${height}px` }}
      data-testid="superset-embed"
      data-status={status}
    />
  );
}
