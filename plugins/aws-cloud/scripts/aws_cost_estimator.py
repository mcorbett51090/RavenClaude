#!/usr/bin/env python3
"""AWS cost decision-support estimator (stdlib only, Python 3.8+).

A CALCULATOR, NOT A DATA SOURCE. The user supplies EVERY price and quantity —
this script bakes in NO AWS prices (they are region- and date-volatile; pull the
live number from the AWS Pricing page / Cost Explorer / the AWS Pricing MCP server
and pass it in). Outputs are decision-support arithmetic, not financial advice and
not a substitute for the account's actual Cost and Usage Report.

Three modes:

  nat-vs-endpoint   Compare routing AWS-service traffic through a NAT Gateway vs.
                    adding VPC endpoint(s). Gateway endpoints (S3/DynamoDB) are
                    free; interface endpoints have an hourly + per-GB cost. Shows
                    monthly cost each way and the saving. (See the
                    nat-gateway-cost-spike scenario.)

  rightsize         Given current vs. proposed instance count/hours and their
                    per-hour prices, show the monthly delta and annualized saving
                    BEFORE any commitment (rightsize before you commit — see the
                    finops decision tree).

  commit-breakeven  Given an on-demand monthly cost, a committed (Savings Plan/RI)
                    monthly cost, and the commitment term, show the break-even
                    utilization: how much of the committed capacity you must
                    actually use for the commitment to pay off vs. on-demand.

All prices are inputs. Run `--help` or `<mode> --help` for the input list.
"""

import argparse
import sys

HOURS_PER_MONTH = 730.0  # AWS billing convention (~365*24/12); override with --hours-per-month


def _fmt(amount: float) -> str:
    """Format a dollar amount with two decimals (no currency assumption baked in)."""
    return f"{amount:,.2f}"


def cmd_nat_vs_endpoint(args: argparse.Namespace) -> int:
    gb = args.monthly_gb
    nat_hourly = args.nat_hourly
    nat_per_gb = args.nat_per_gb
    # NAT gateways are charged per-NAT regardless of endpoints; the comparison here
    # is the *data-processing* cost of sending this traffic through the NAT vs. an
    # endpoint. Hourly NAT cost is shown for context but is not "saved" by an
    # endpoint unless the NAT is removed entirely.
    nat_data_cost = gb * nat_per_gb
    nat_hourly_cost = nat_hourly * HOURS_PER_MONTH * args.nat_count

    # Endpoint side: gateway endpoints (S3/DynamoDB) are free; interface endpoints
    # have an hourly charge per-AZ plus a per-GB processing charge.
    iface_hourly_cost = (
        args.iface_hourly * HOURS_PER_MONTH * args.iface_count
        if args.iface_count
        else 0.0
    )
    iface_data_cost = gb * args.iface_per_gb if args.iface_count else 0.0
    endpoint_total = iface_hourly_cost + iface_data_cost

    data_saving = nat_data_cost - endpoint_total

    print("NAT Gateway vs. VPC endpoint — monthly data-routing comparison")
    print(f"  Traffic volume:                 {_fmt(gb)} GB/month")
    print("  Through NAT Gateway:")
    print(f"    data processing ({_fmt(nat_per_gb)}/GB):  $ {_fmt(nat_data_cost)}")
    print(
        f"    NAT hourly ({args.nat_count} NAT @ {_fmt(nat_hourly)}/hr, context): "
        f"$ {_fmt(nat_hourly_cost)}"
    )
    if args.iface_count:
        print(f"  Through interface endpoint(s) (x{args.iface_count}):")
        print(f"    hourly:                       $ {_fmt(iface_hourly_cost)}")
        print(f"    data processing ({_fmt(args.iface_per_gb)}/GB): $ {_fmt(iface_data_cost)}")
        print(f"    endpoint total:               $ {_fmt(endpoint_total)}")
    else:
        print("  Through gateway endpoint (S3/DynamoDB): $ 0.00 (gateway endpoints are free)")
    print(f"  Monthly data-routing saving:    $ {_fmt(data_saving)}")
    if data_saving > 0:
        print("  -> Endpoint is cheaper for this traffic. Verify the per-GB rates at use.")
    else:
        print("  -> NAT is cheaper at these inputs (low volume / pricey endpoint).")
    print("\n  Inputs are yours; AWS per-GB and hourly rates are region/date-volatile.")
    print("  [verify-at-use] pull live rates from the AWS VPC pricing page before deciding.")
    return 0


def cmd_rightsize(args: argparse.Namespace) -> int:
    # --hours default is resolved here, not at parser-build time: a global
    # --hours-per-month override (applied in main() after parse_args) would
    # otherwise never reach the rightsize default, which argparse freezes early.
    hours = args.hours if args.hours is not None else HOURS_PER_MONTH
    args.hours = hours
    current = args.current_hourly * args.current_count * args.hours
    proposed = args.proposed_hourly * args.proposed_count * args.hours
    monthly_delta = current - proposed
    annual_delta = monthly_delta * 12

    print("Rightsizing delta (rightsize BEFORE committing — see the finops tree)")
    print(
        f"  Current:  {args.current_count} x {_fmt(args.current_hourly)}/hr "
        f"x {_fmt(args.hours)} hr = $ {_fmt(current)}/month"
    )
    print(
        f"  Proposed: {args.proposed_count} x {_fmt(args.proposed_hourly)}/hr "
        f"x {_fmt(args.hours)} hr = $ {_fmt(proposed)}/month"
    )
    print(f"  Monthly saving:  $ {_fmt(monthly_delta)}")
    print(f"  Annualized:      $ {_fmt(annual_delta)}")
    if monthly_delta <= 0:
        print("  -> Proposed size is not cheaper at these inputs; not the lever here.")
    else:
        print("  -> Capture this BEFORE a Savings Plan/RI so you commit to the smaller size.")
    print("\n  Validate the proposed size against observed p95/p99 utilization (Compute")
    print("  Optimizer / CloudWatch), not a guess. Prices are yours [verify-at-use].")
    return 0


def cmd_commit_breakeven(args: argparse.Namespace) -> int:
    on_demand = args.on_demand_monthly
    committed = args.committed_monthly
    if on_demand <= 0:
        print("Error: --on-demand-monthly must be greater than 0.", file=sys.stderr)
        return 2

    # The committed cost is paid whether or not the capacity is used. Break-even
    # utilization = committed / on-demand-for-the-same-full-capacity. Below this
    # utilization fraction, on-demand would have been cheaper.
    breakeven_fraction = committed / on_demand
    monthly_saving_at_full = on_demand - committed
    term_saving = monthly_saving_at_full * args.term_months

    print(f"Commitment break-even ({args.term_months}-month term)")
    print(f"  On-demand (full capacity):  $ {_fmt(on_demand)}/month")
    print(f"  Committed (paid regardless): $ {_fmt(committed)}/month")
    print(f"  Break-even utilization:     {breakeven_fraction * 100:.1f}%")
    print(
        "    (you must actually USE at least this fraction of the committed capacity"
    )
    print("     for the commitment to beat on-demand)")
    print(f"  Saving at 100% utilization: $ {_fmt(monthly_saving_at_full)}/month")
    print(f"  Over the {args.term_months}-month term:  $ {_fmt(term_saving)}")
    if breakeven_fraction >= 1.0:
        print("  -> Committed cost >= on-demand: this does NOT pay off. Re-check inputs.")
    elif breakeven_fraction > 0.85:
        print("  -> High break-even: only commit if usage is very stable (rightsize first).")
    else:
        print("  -> Commit only the STABLE BASELINE, never the peak; rightsize first.")
    print("\n  Prices/discounts are your inputs from the live Savings Plans/RI offer.")
    print("  [verify-at-use] pull the actual offer rate before committing.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aws_cost_estimator.py",
        description="AWS cost decision-support — you supply every price; nothing is baked in.",
    )
    parser.add_argument(
        "--hours-per-month",
        type=float,
        default=HOURS_PER_MONTH,
        help=f"Billing hours per month (default {HOURS_PER_MONTH}, AWS convention).",
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    p_nat = sub.add_parser(
        "nat-vs-endpoint",
        help="Compare NAT Gateway vs. VPC endpoint cost for AWS-service traffic.",
    )
    p_nat.add_argument("--monthly-gb", type=float, required=True, help="GB/month of this traffic.")
    p_nat.add_argument(
        "--nat-per-gb", type=float, required=True, help="NAT data-processing $/GB (your region)."
    )
    p_nat.add_argument("--nat-hourly", type=float, default=0.0, help="NAT hourly $ (context only).")
    p_nat.add_argument("--nat-count", type=int, default=1, help="Number of NAT gateways (context).")
    p_nat.add_argument(
        "--iface-count",
        type=int,
        default=0,
        help="Interface endpoints to add (0 = gateway endpoint, which is free).",
    )
    p_nat.add_argument(
        "--iface-hourly", type=float, default=0.0, help="Interface endpoint hourly $ each."
    )
    p_nat.add_argument(
        "--iface-per-gb", type=float, default=0.0, help="Interface endpoint $/GB processed."
    )
    p_nat.set_defaults(func=cmd_nat_vs_endpoint)

    p_rs = sub.add_parser("rightsize", help="Monthly + annual delta of a rightsizing move.")
    p_rs.add_argument("--current-hourly", type=float, required=True, help="Current instance $/hr.")
    p_rs.add_argument("--current-count", type=int, required=True, help="Current instance count.")
    p_rs.add_argument(
        "--proposed-hourly", type=float, required=True, help="Proposed instance $/hr."
    )
    p_rs.add_argument(
        "--proposed-count", type=int, required=True, help="Proposed instance count."
    )
    p_rs.add_argument(
        "--hours",
        type=float,
        default=None,
        help="Running hours/month (defaults to --hours-per-month).",
    )
    p_rs.set_defaults(func=cmd_rightsize)

    p_cb = sub.add_parser(
        "commit-breakeven",
        help="Break-even utilization for a Savings Plan / RI vs. on-demand.",
    )
    p_cb.add_argument(
        "--on-demand-monthly", type=float, required=True, help="On-demand $/month at full capacity."
    )
    p_cb.add_argument(
        "--committed-monthly", type=float, required=True, help="Committed $/month (paid always)."
    )
    p_cb.add_argument(
        "--term-months", type=int, default=12, help="Commitment term in months (e.g. 12 or 36)."
    )
    p_cb.set_defaults(func=cmd_commit_breakeven)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # honor a global --hours-per-month for the rightsize default if the user set it
    global HOURS_PER_MONTH
    HOURS_PER_MONTH = args.hours_per_month
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
