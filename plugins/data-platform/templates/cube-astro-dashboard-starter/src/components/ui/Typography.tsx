import type { HTMLAttributes } from "react";
import { cn } from "./cn";

// Local "Tremor Raw"-style typography primitives — see Card.tsx's header
// comment for why (FORGE dashboard-top1pct P1-7, 2026-09-03).

const TEXT_COLOR_CLASS: Record<string, string> = {
  rose: "text-rose-600",
  default: "text-tremor-content",
};

export interface TextProps extends HTMLAttributes<HTMLParagraphElement> {
  /** Matches the small subset of @tremor/react's `color` prop this app used. */
  color?: "rose" | "default";
}

export function Text({ className, color = "default", children, ...rest }: TextProps) {
  return (
    <p className={cn("text-sm", TEXT_COLOR_CLASS[color], className)} {...rest}>
      {children}
    </p>
  );
}

export function Metric({ className, children, ...rest }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("text-2xl font-semibold text-tremor-content-strong", className)} {...rest}>
      {children}
    </p>
  );
}

export function Title({ className, children, ...rest }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("text-xl font-medium text-tremor-content-strong", className)} {...rest}>
      {children}
    </p>
  );
}

export function Subtitle({ className, children, ...rest }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={cn("text-sm text-tremor-content", className)} {...rest}>
      {children}
    </p>
  );
}
