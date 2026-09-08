import type { HTMLAttributes } from "react";
import { cn } from "./cn";

// Local "Tremor Raw"-style layout primitives — see Card.tsx's header comment
// for why (FORGE dashboard-top1pct P1-7, 2026-09-03).

export interface FlexProps extends HTMLAttributes<HTMLDivElement> {
  justifyContent?: "start" | "end" | "center" | "between" | "around" | "evenly";
  alignItems?: "start" | "end" | "center" | "baseline" | "stretch";
}

const JUSTIFY_CLASS: Record<NonNullable<FlexProps["justifyContent"]>, string> = {
  start: "justify-start",
  end: "justify-end",
  center: "justify-center",
  between: "justify-between",
  around: "justify-around",
  evenly: "justify-evenly",
};

const ALIGN_CLASS: Record<NonNullable<FlexProps["alignItems"]>, string> = {
  start: "items-start",
  end: "items-end",
  center: "items-center",
  baseline: "items-baseline",
  stretch: "items-stretch",
};

export function Flex({
  className,
  justifyContent = "between",
  alignItems = "center",
  children,
  ...rest
}: FlexProps) {
  return (
    <div
      className={cn(
        "flex w-full flex-row",
        JUSTIFY_CLASS[justifyContent],
        ALIGN_CLASS[alignItems],
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}

export interface GridProps extends HTMLAttributes<HTMLDivElement> {
  /** Number of columns at the `md` breakpoint — the only breakpoint this app used. */
  numItemsMd?: number;
}

// Fixed literal class map — Tailwind's JIT compiler scans source text for
// class names, so a template-interpolated `grid-cols-${n}` would never be
// generated. This app only used numItemsMd={3}; extend the map if a future
// engagement needs more.
const GRID_COLS_MD_CLASS: Record<number, string> = {
  1: "md:grid-cols-1",
  2: "md:grid-cols-2",
  3: "md:grid-cols-3",
  4: "md:grid-cols-4",
  6: "md:grid-cols-6",
  12: "md:grid-cols-12",
};

export function Grid({ className, numItemsMd = 1, children, ...rest }: GridProps) {
  return (
    <div
      className={cn(
        "grid grid-cols-1",
        GRID_COLS_MD_CLASS[numItemsMd] ?? "md:grid-cols-1",
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}

export interface ColProps extends HTMLAttributes<HTMLDivElement> {
  numColSpanMd?: number;
}

const COL_SPAN_MD_CLASS: Record<number, string> = {
  1: "md:col-span-1",
  2: "md:col-span-2",
  3: "md:col-span-3",
  4: "md:col-span-4",
  6: "md:col-span-6",
  12: "md:col-span-12",
};

export function Col({ className, numColSpanMd = 1, children, ...rest }: ColProps) {
  return (
    <div className={cn(COL_SPAN_MD_CLASS[numColSpanMd] ?? "md:col-span-1", className)} {...rest}>
      {children}
    </div>
  );
}
