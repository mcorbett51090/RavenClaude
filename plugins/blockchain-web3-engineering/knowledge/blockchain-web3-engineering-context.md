# Blockchain & Web3 Engineering Benchmarks & Context (2025–2026)

> Orientation for the team. **Every figure and regulatory statement here is `[unverified — training knowledge]`** and varies by geography, segment, and date. Confirm against a current, dated source before any deliverable, and route every professional/legal/regulatory determination to the qualified authority (CLAUDE.md §2, §3 #8).

## Where defensible Web3 figures come from

Gas prices, token prices, yields, and exploit statistics are **highly volatile and date-sensitive**. **Cite the source + date for any figure and mark unsourced ones `[unverified — training knowledge]` (§3 #8).** The most defensible evidence is an on-chain measurement at a stated block/time and a named audit report — not a recalled number. Token/securities classification and investment/tax questions are **not** the team's call (§2 #8).

## Directional frames (illustrative only — `[unverified — training knowledge]`)

| Area | Directional frame | Must-verify |
|---|---|---|
| Top exploit classes | Reentrancy, access control, arithmetic dominate high-severity losses | Confirm against a dated audit/incident dataset (§3 #2) |
| Gas cost drivers | SSTORE and unbounded loops dominate | Profile the actual function (§3 #3) |
| Oracle safety | Spot DEX price is manipulable; TWAP/multi-source safer | Design-specific (§3 #7) |
| Yields | Volatile, often unsustainable under stress | Illustrative only — not advice (§3 #8, §2) |

## Operating rhythm

- **Pre-deploy** — audit the top vuln classes, fuzz invariants, exercise on testnet; the gate (§3 #1 #5).
- **Design-time** — decide on/off-chain split and upgrade stance deliberately (§3 #4 #6).
- **Ongoing** — monitor gas, oracle health, and economic/MEV surface; treat the upgrade admin key as a top threat (§3 #6 #7).

## The standing caution

Token/securities **classification**, **investment** advice, and **tax** determinations are qualified counsel's and licensed advisors' call (§2 #8) — the team frames the engineering and economics and routes the rest. Economics/yield outputs are **illustrative engineering, not financial advice**. Never store or request private keys, seed phrases, or signing keys; route any handling to `ravenclaude-core` `security-reviewer` (§2).
