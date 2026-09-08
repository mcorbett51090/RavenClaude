import type { HTMLAttributes } from "react";
import { cn } from "./cn";

// Local "Tremor Raw"-style delta badge — see Card.tsx's header comment for
// why (FORGE dashboard-top1pct P1-7, 2026-09-03).

export interface BadgeDeltaProps extends HTMLAttributes<HTMLSpanElement> {
  deltaType?: "increase" | "decrease";
}

export function BadgeDelta({
  className,
  deltaType = "increase",
  children,
  ...rest
}: BadgeDeltaProps) {
  const isIncrease = deltaType === "increase";
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium",
        isIncrease ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700",
        className,
      )}
      {...rest}
    >
      <span aria-hidden="true">{isIncrease ? "▲" : "▼"}</span>
      {children}
    </span>
  );
}
