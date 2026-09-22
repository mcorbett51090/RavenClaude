import type { HTMLAttributes } from "react";
import { cn } from "./cn";

/**
 * Local "Tremor Raw"-style Card — @tremor/react's registry line has had no
 * stable release since 2025-01-13 (confirmed this session: `npm view
 * @tremor/react time.modified`), and the vendor's own distribution model has
 * moved to copy-paste components with no npm package (FORGE dashboard-top1pct
 * P1-7, 2026-09-03). Copied to match Tremor's own Card visual shape closely
 * enough that this is a dependency swap, not a redesign — see this starter's
 * README for the full migration note.
 */
export function Card({ className, children, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-lg border border-tremor-border bg-tremor-background p-6 shadow-sm",
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}
