// ---------------------------------------------------------------------------
// Power BI Embedded App-Owns-Data (React component) — RUNNABLE, promoted
// from power-bi-embedded-react.tsx.md at v0.2.0.
// ---------------------------------------------------------------------------
// SECURITY (revised after mandatory security review): this component no
// longer carries a `tenantId` or `daxRole` prop. Those values were
// previously composed client-side into the request body and passed through
// to Power BI's EffectiveIdentity unvalidated — a cross-tenant read plus a
// roleless-identity fail-open, both closed by moving identity resolution
// entirely into pbi-embed-token-endpoint.ts's getEffectiveIdentityForSession()
// seam. This component now sends only {workspaceId, reportId, datasetId}.
//
// ⚠ Coordinate with power-platform/power-bi-engineer. This template owns the
// embed pattern + integration into a non-Microsoft data stack. DAX role
// authoring, semantic model, and PBIP source control are owned there.
//
// KNOWN GAP: not yet run against a live Power BI Embedded workspace.
// Pinned at promotion time: powerbi-client ^2.23, @azure/msal-node ^2.
//
// Companion docs:
//   - ../knowledge/power-bi-embedded-for-consultants.md
//   - ../skills/embed-csp-and-iframe-sandboxing/SKILL.md
//   - ./pbi-embed-token-endpoint.ts — the host-backend module this component calls
// ---------------------------------------------------------------------------

import { models, service, factories } from "powerbi-client";
import { useEffect, useRef, useState } from "react";

export interface PowerBIEmbedProps {
  workspaceId: string;
  reportId: string;
  datasetId: string;
  /** Host backend endpoint implemented by pbi-embed-token-endpoint.ts. */
  embedTokenEndpoint: string;
  height?: number;
  onError?: (error: Error) => void;
}

let powerbiService: service.Service | null = null;
function getPowerbiService(): service.Service {
  if (!powerbiService) {
    powerbiService = new service.Service(
      factories.hpmFactory,
      factories.wpmpFactory,
      factories.routerFactory,
    );
  }
  return powerbiService;
}

export function PowerBIEmbed({
  workspaceId,
  reportId,
  datasetId,
  embedTokenEndpoint,
  height = 800,
  onError,
}: PowerBIEmbedProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");

  useEffect(() => {
    if (!containerRef.current) return;
    let cancelled = false;
    const container = containerRef.current;

    async function mount() {
      try {
        // Only report/dataset identity travels client-side. The DAX
        // EffectiveIdentity (username + roles) is resolved server-side.
        const res = await fetch(embedTokenEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ workspaceId, reportId, datasetId }),
        });
        if (!res.ok) throw new Error(`embed token fetch failed: ${res.status}`);
        const { embedToken, embedUrl } = await res.json();

        if (cancelled || !container) return;

        const config: models.IReportEmbedConfiguration = {
          type: "report",
          id: reportId,
          embedUrl,
          accessToken: embedToken,
          tokenType: models.TokenType.Embed,
          settings: {
            panes: { filters: { visible: false }, pageNavigation: { visible: true } },
            background: models.BackgroundType.Transparent,
          },
        };

        getPowerbiService().embed(container, config);
        if (!cancelled) setStatus("ready");
      } catch (err) {
        if (!cancelled) {
          setStatus("error");
          onError?.(err instanceof Error ? err : new Error(String(err)));
        }
      }
    }

    mount();

    return () => {
      cancelled = true;
      if (container) getPowerbiService().reset(container);
    };
  }, [workspaceId, reportId, datasetId, embedTokenEndpoint]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: `${height}px` }}
      data-testid="powerbi-embed"
      data-status={status}
    />
  );
}
