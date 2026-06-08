#!/usr/bin/env python3
"""blockchain_web3_calc.py — a zero-dependency Blockchain & Web3 Engineering decision calculator.

Removes arithmetic error from 3 recurring blockchain & web3 engineering decisions:

  gas-cost      Transaction cost from gas units, gas price, and token price.

  storage-cost  On-chain storage cost with the on/off-chain framing.

  staking-yield Illustrative net staking APR and annual reward (NOT financial advice).

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No private keys / wallet data belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No private keys / wallet data."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_gas_cost(a):
    if a.gas_units <= 0 or a.gas_price_gwei < 0 or a.token_price_usd < 0:
        print("error: --gas-units > 0 and prices >= 0", file=sys.stderr)
        return 2
    tx_cost_native = a.gas_units * a.gas_price_gwei * 1e-9
    tx_cost_usd = tx_cost_native * a.token_price_usd
    print("=== Transaction gas cost (CLAUDE.md S3 #3) ===")
    print(f"  Gas units           : {a.gas_units:,.0f}")
    print(f"  Gas price           : {a.gas_price_gwei:g} gwei")
    print(f"  Token price (dated) : {_money(a.token_price_usd)}")
    print(f"  >> Tx cost          : {tx_cost_native:.6f} native  =  {_money(tx_cost_usd)}")
    if a.tx_per_day > 0:
        monthly = tx_cost_usd * a.tx_per_day * 30
        print(f"  At {a.tx_per_day:g} tx/day      : {_money(monthly)} / month")
    print("  NOTE: gas price + token price are volatile — date+source them (S3 #8).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_storage_cost(a):
    if a.slots <= 0 or a.gas_per_slot <= 0 or a.gas_price_gwei < 0 or a.token_price_usd < 0:
        print("error: --slots > 0, --gas-per-slot > 0, prices >= 0", file=sys.stderr)
        return 2
    gas_total = a.slots * a.gas_per_slot
    cost_native = gas_total * a.gas_price_gwei * 1e-9
    cost_usd = cost_native * a.token_price_usd
    print("=== On-chain storage cost (CLAUDE.md S3 #4) ===")
    print(f"  Storage slots       : {a.slots:g}")
    print(f"  Gas per slot        : {a.gas_per_slot:,.0f}  (fresh SSTORE)")
    print(f"  Gas price           : {a.gas_price_gwei:g} gwei")
    print(f"  Token price (dated) : {_money(a.token_price_usd)}")
    print(f"  Total gas           : {gas_total:,.0f}")
    print(f"  >> Storage cost     : {cost_native:.6f} native  =  {_money(cost_usd)}")
    print("  --- on-chain vs off-chain ---")
    print("  On-chain  : paid-for-forever AND public; only for consensus-critical data (S3 #4).")
    print("  Off-chain : IPFS/Arweave + an on-chain hash pointer for ancillary/large/private data (S3 #4).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_staking_yield(a):
    if a.staked <= 0 or not (0 < a.gross_rate <= 1) or not (0 <= a.commission < 1):
        print("error: --staked > 0, 0 < --gross-rate <= 1, 0 <= --commission < 1", file=sys.stderr)
        return 2
    net_apr = a.gross_rate * (1 - a.commission)
    annual_reward = a.staked * net_apr
    print("=== Staking yield (ILLUSTRATIVE) (CLAUDE.md S3 #8) ===")
    print(f"  Staked amount       : {a.staked:,.4f}")
    print(f"  Gross reward rate   : {_pct(a.gross_rate)}")
    print(f"  Validator commission: {_pct(a.commission)}")
    print(f"  >> Net APR          : {_pct(net_apr)}  (gross x (1 - commission))")
    print(f"  >> Annual reward    : {annual_reward:,.4f}  (illustrative)")
    print("  NOTE: ILLUSTRATIVE engineering model, NOT financial advice — rates/prices are volatile;")
    print("        route investment/securities/tax to a licensed authority (S3 #8, S2).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='blockchain_web3_calc.py',
        description="Blockchain & Web3 Engineering decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('gas-cost', help='tx cost in native token + USD, plus monthly at N tx/day')
    sp.add_argument('--gas-units', type=float, required=True, help='gas units consumed by the tx')
    sp.add_argument('--gas-price-gwei', type=float, required=True, help='gas price in gwei')
    sp.add_argument('--token-price-usd', type=float, required=True, help='native-token price in USD (dated)')
    sp.add_argument('--tx-per-day', type=float, default=0.0, help='transactions per day (for monthly est.)')
    sp.set_defaults(func=cmd_gas_cost)

    sp = sub.add_parser('storage-cost', help='cost of storage-slot writes; on-chain vs off-chain trade')
    sp.add_argument('--slots', type=float, required=True, help='storage slots written')
    sp.add_argument('--gas-per-slot', type=float, default=20000.0, help='gas per fresh SSTORE')
    sp.add_argument('--gas-price-gwei', type=float, required=True, help='gas price in gwei')
    sp.add_argument('--token-price-usd', type=float, required=True, help='native-token price in USD (dated)')
    sp.set_defaults(func=cmd_storage_cost)

    sp = sub.add_parser('staking-yield', help='net APR = gross rate x (1 - commission); annual reward — illustrative only')
    sp.add_argument('--staked', type=float, required=True, help='staked amount (native token or USD)')
    sp.add_argument('--gross-rate', type=float, required=True, help='gross annual reward rate (0-1)')
    sp.add_argument('--commission', type=float, default=0.0, help='validator commission (0-1)')
    sp.set_defaults(func=cmd_staking_yield)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
