#!/usr/bin/env python3
"""embedded_calc.py — a zero-dependency embedded/IoT back-of-envelope calculator.

Removes guesswork from three recurring quantitative calls the embedded-iot
team makes constantly. It implements the team's house doctrine — see
../CLAUDE.md §4 and ../knowledge/embedded-iot-engineering-decision-trees.md:

  power-budget  Average current from an active/sleep duty cycle, then battery
                life from a mAh capacity. Makes "a battery device lives or dies
                on its sleep current x duty cycle" (§4 #8) a number, not a vibe.
                Sleep current usually dominates; this shows by how much.

  baud          UART timing from a peripheral clock + divisor, OR the divisor +
                achievable rate + percent error for a target baud. The clock-
                divisor error is the usual cause of "the link corrupts at high
                baud" before you blame the ISR (decision-tree: Peripheral I/O).

  airtime       LoRa-style on-air time for a payload at a spreading factor +
                bandwidth, plus the duty-cycle headroom: how many messages per
                hour fit inside a regulatory duty-cycle cap (§4 #7). A duty-
                cycle-limited radio's real cadence is its on-air budget, not
                its range.

This is a CALCULATOR, not a data source — it does not read a datasheet, a power
profiler, or a radio stack. The user supplies every input; the tool does the
arithmetic and shows the rule it applied. Stdlib only (argparse); runs anywhere
Python 3.9+ is present.

IMPORTANT: outputs are decision-support, not a measured result. A computed
battery life is only as honest as the sleep-current input — measure it, never
assume it (see scenarios/2026-06-08-coin-cell-died-in-weeks.md). The LoRa
airtime model is the common time-on-air approximation and must be checked
against the modem's own calculator / the regional regulatory plan before you
commit a cadence ([verify-at-build]).

Examples
--------
  # 8 mA active for 50 ms once a minute, 3 uA asleep, on a 225 mAh CR2032
  python3 embedded_calc.py power-budget \\
      --active-ma 8 --active-ms 50 --period-s 60 --sleep-ua 3 --capacity-mah 225

  # 16 MHz clock, want 115200 baud over a 16x-oversampled UART
  python3 embedded_calc.py baud --clock-hz 16000000 --target-baud 115200

  # 40-byte LoRa payload at SF10 / 125 kHz, against a 1% duty-cycle cap
  python3 embedded_calc.py airtime --payload-bytes 40 --sf 10 --bw-khz 125 --duty-pct 1
"""

from __future__ import annotations

import argparse
import math
import sys

# --- power-budget: average current from duty cycle -> battery life -----------


def cmd_power_budget(a: argparse.Namespace) -> int:
    if a.active_ma < 0 or a.sleep_ua < 0:
        print("error: currents must be >= 0", file=sys.stderr)
        return 2
    if a.active_ms < 0:
        print("error: --active-ms must be >= 0", file=sys.stderr)
        return 2
    if a.period_s <= 0:
        print("error: --period-s must be > 0", file=sys.stderr)
        return 2
    active_s = a.active_ms / 1000.0
    if active_s > a.period_s:
        print("error: --active-ms exceeds the period (--period-s)", file=sys.stderr)
        return 2

    duty = active_s / a.period_s
    active_ua = a.active_ma * 1000.0
    # Time-weighted average current over the period.
    avg_ua = active_ua * duty + a.sleep_ua * (1.0 - duty)
    avg_ma = avg_ua / 1000.0

    sleep_share = (a.sleep_ua * (1.0 - duty)) / avg_ua * 100.0 if avg_ua else 0.0
    active_share = 100.0 - sleep_share

    print("Power budget — average current -> battery life")
    print("-" * 58)
    print(f"  Active draw         : {a.active_ma:g} mA for {a.active_ms:g} ms")
    print(f"  Period              : {a.period_s:g} s  (duty cycle {duty * 100:.4g}%)")
    print(f"  Sleep draw          : {a.sleep_ua:g} uA")
    print("-" * 58)
    print(f"  AVERAGE current     : {avg_ua:.3g} uA  ({avg_ma:.4g} mA)")
    print(f"  Spent in sleep      : {sleep_share:.1f}%   active: {active_share:.1f}%")

    if a.capacity_mah is not None:
        if a.capacity_mah <= 0:
            print("error: --capacity-mah must be > 0", file=sys.stderr)
            return 2
        usable = a.capacity_mah * (a.derate_pct / 100.0)
        life_h = usable / avg_ma if avg_ma else math.inf
        life_d = life_h / 24.0
        life_y = life_d / 365.0
        print("-" * 58)
        print(f"  Capacity            : {a.capacity_mah:g} mAh  (usable {usable:g} mAh @ {a.derate_pct:g}%)")
        print(f"  BATTERY LIFE        : {life_d:.1f} days  ({life_y:.2f} years)")
    print("-" * 58)
    print("  Note: sleep current usually dominates a low-duty device — a uA of")
    print("  avoidable leakage swamps a wasted mA in a sub-1% active burst.")
    print("  MEASURE sleep draw with a uA-capable meter; never assume it. The")
    print("  derate (--derate-pct) holds margin for self-discharge, temp, OTA.")
    return 0


# --- baud: UART clock-divisor error % ----------------------------------------


def cmd_baud(a: argparse.Namespace) -> int:
    if a.clock_hz <= 0:
        print("error: --clock-hz must be > 0", file=sys.stderr)
        return 2
    if a.target_baud <= 0:
        print("error: --target-baud must be > 0", file=sys.stderr)
        return 2
    if a.oversample <= 0:
        print("error: --oversample must be > 0", file=sys.stderr)
        return 2

    # Ideal (fractional) divisor for the target baud at this oversampling.
    ideal_div = a.clock_hz / (a.oversample * a.target_baud)
    # Hardware uses an integer divisor (rounded to nearest); the residual is the error.
    int_div = max(1, round(ideal_div))
    actual_baud = a.clock_hz / (a.oversample * int_div)
    error_pct = (actual_baud - a.target_baud) / a.target_baud * 100.0

    # Rule of thumb: a UART frame tolerates roughly +/- ~2-2.5% accumulated error.
    if abs(error_pct) <= 2.0:
        verdict = "OK — within the ~2% per-frame UART tolerance"
    elif abs(error_pct) <= 2.5:
        verdict = "MARGINAL — near the ~2% tolerance; expect framing errors under load/temp"
    else:
        verdict = "TOO HIGH — frames will corrupt; pick a clock that divides cleanly"

    print("UART baud — clock divisor + error")
    print("-" * 58)
    print(f"  Peripheral clock    : {a.clock_hz:g} Hz")
    print(f"  Oversampling        : {a.oversample}x")
    print(f"  Target baud         : {a.target_baud:g}")
    print("-" * 58)
    print(f"  Ideal divisor       : {ideal_div:.4f}")
    print(f"  Integer divisor     : {int_div}")
    print(f"  Achievable baud     : {actual_baud:.2f}")
    print(f"  ERROR               : {error_pct:+.3f}%")
    print(f"  Verdict             : {verdict}")
    print("-" * 58)
    print("  Note: clock-divisor error accumulates across a 10-bit frame; both")
    print("  ends add their own. A clean integer divisor (e.g. a crystal sized")
    print("  for the baud) beats a fast ISR for fixing 'it corrupts at speed'.")
    return 0


# --- airtime: LoRa on-air time + duty-cycle headroom -------------------------


def _lora_airtime_ms(
    payload_bytes: int,
    sf: int,
    bw_khz: float,
    coding_rate: int,
    preamble: int,
    header: bool,
    low_dr_opt: bool,
    crc: bool,
) -> float:
    """Semtech LoRa time-on-air, in milliseconds. The standard approximation."""
    bw_hz = bw_khz * 1000.0
    t_sym_ms = (2.0**sf) / bw_hz * 1000.0  # symbol duration

    # Low-data-rate optimization auto-engages at long symbol times; allow override.
    de = 1 if (low_dr_opt or t_sym_ms > 16.0) else 0
    ih = 0 if header else 1  # implicit header drops the header symbols
    crc_term = 16 if crc else 0

    numerator = 8 * payload_bytes - 4 * sf + 28 + crc_term - 20 * ih
    denominator = 4 * (sf - 2 * de)
    payload_sym = 8 + max(math.ceil(numerator / denominator) * (coding_rate + 4), 0)

    t_preamble_ms = (preamble + 4.25) * t_sym_ms
    t_payload_ms = payload_sym * t_sym_ms
    return t_preamble_ms + t_payload_ms


def cmd_airtime(a: argparse.Namespace) -> int:
    if a.payload_bytes < 0:
        print("error: --payload-bytes must be >= 0", file=sys.stderr)
        return 2
    if not 6 <= a.sf <= 12:
        print("error: --sf must be 6..12", file=sys.stderr)
        return 2
    if a.bw_khz <= 0:
        print("error: --bw-khz must be > 0", file=sys.stderr)
        return 2
    if not 1 <= a.coding_rate <= 4:
        print("error: --coding-rate must be 1..4 (the 4/(4+CR) denominator)", file=sys.stderr)
        return 2
    if a.preamble < 0:
        print("error: --preamble must be >= 0", file=sys.stderr)
        return 2

    airtime_ms = _lora_airtime_ms(
        a.payload_bytes,
        a.sf,
        a.bw_khz,
        a.coding_rate,
        a.preamble,
        header=not a.implicit_header,
        low_dr_opt=a.low_dr_opt,
        crc=not a.no_crc,
    )

    print("LoRa airtime — time-on-air + duty-cycle headroom")
    print("-" * 58)
    print(f"  Payload             : {a.payload_bytes} bytes")
    print(f"  SF / BW             : SF{a.sf} / {a.bw_khz:g} kHz   (CR 4/{4 + a.coding_rate})")
    print(f"  Preamble            : {a.preamble} symbols")
    print("-" * 58)
    print(f"  TIME ON AIR         : {airtime_ms:.1f} ms")

    if a.duty_pct is not None:
        if not 0.0 < a.duty_pct <= 100.0:
            print("error: --duty-pct must be in (0, 100]", file=sys.stderr)
            return 2
        # Allowed on-air per hour, then how many messages fit + the min gap.
        allowed_ms_per_hr = 3_600_000.0 * (a.duty_pct / 100.0)
        msgs_per_hr = allowed_ms_per_hr / airtime_ms if airtime_ms else math.inf
        min_gap_s = airtime_ms / (a.duty_pct / 100.0) / 1000.0
        print("-" * 58)
        print(f"  Duty-cycle cap      : {a.duty_pct:g}%  ({allowed_ms_per_hr / 1000:.1f} s on-air/hour)")
        print(f"  HEADROOM            : {msgs_per_hr:.1f} messages/hour max")
        print(f"  Min gap between TX  : {min_gap_s:.1f} s")
    print("-" * 58)
    print("  Note: airtime grows fast with SF — a cadence the duty cycle won't")
    print("  allow shows up as silent stack-enforced deferral, not an error")
    print("  (scenarios/2026-06-08-lora-duty-cycle-throttled.md). Pack the")
    print("  payload + batch readings to fit. [verify-at-build] vs the modem.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="embedded_calc.py",
        description="Embedded/IoT back-of-envelope calculator (decision-support, not a measurement).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="command", required=True)

    pb = sub.add_parser("power-budget", help="duty-cycle average current -> battery life")
    pb.add_argument("--active-ma", type=float, required=True, help="active-mode current in mA")
    pb.add_argument("--active-ms", type=float, required=True, help="active duration per wake, in ms")
    pb.add_argument("--period-s", type=float, required=True, help="wake period in seconds")
    pb.add_argument("--sleep-ua", type=float, required=True, help="sleep-mode current in uA (MEASURE this)")
    pb.add_argument("--capacity-mah", type=float, default=None, help="battery capacity in mAh (optional)")
    pb.add_argument(
        "--derate-pct",
        type=float,
        default=80.0,
        help="usable %% of nominal capacity for self-discharge/temp/OTA margin (default 80)",
    )
    pb.set_defaults(func=cmd_power_budget)

    bd = sub.add_parser("baud", help="UART clock-divisor + error %% for a target baud")
    bd.add_argument("--clock-hz", type=float, required=True, help="UART peripheral clock in Hz")
    bd.add_argument("--target-baud", type=float, required=True, help="desired baud rate")
    bd.add_argument("--oversample", type=int, default=16, help="UART oversampling, 16 or 8 (default 16)")
    bd.set_defaults(func=cmd_baud)

    at = sub.add_parser("airtime", help="LoRa on-air time + duty-cycle headroom")
    at.add_argument("--payload-bytes", type=int, required=True, help="application payload size in bytes")
    at.add_argument("--sf", type=int, required=True, help="spreading factor 6..12")
    at.add_argument("--bw-khz", type=float, default=125.0, help="bandwidth in kHz (default 125)")
    at.add_argument("--coding-rate", type=int, default=1, help="coding rate CR in 4/(4+CR); 1..4 (default 1)")
    at.add_argument("--preamble", type=int, default=8, help="preamble length in symbols (default 8)")
    at.add_argument("--implicit-header", action="store_true", help="implicit (no) header mode")
    at.add_argument("--no-crc", action="store_true", help="disable the payload CRC term")
    at.add_argument("--low-dr-opt", action="store_true", help="force low-data-rate optimization on")
    at.add_argument("--duty-pct", type=float, default=None, help="regulatory duty-cycle cap %% (optional)")
    at.set_defaults(func=cmd_airtime)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
