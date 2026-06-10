# Blockchain & Web3 Engineering Unit Economics

> The arithmetic behind the team's house opinions. Every formula here is reproduced in [`../scripts/blockchain_web3_calc.py`](../scripts/blockchain_web3_calc.py) so the math is auditable. All multipliers/benchmarks are `[unverified — training knowledge]` — supply the client's actual figures (§3 #8).

## 1. Audit-before-deploy is the gate, not a step (§3 #1)

```
deploy_risk = irreversible AND exploit_speed == one_block
# A non-upgradeable contract has no hotfix; the audit + invariant fuzz + testnet IS the release gate.
```

The cost of shipping a bug is the value the contract holds — there is no rollback.

## 2. Transaction cost in human terms (§3 #3 #8)

```
tx_cost_native = gas_units * gas_price_gwei * 1e-9
tx_cost_usd    = tx_cost_native * native_token_price_usd
monthly_usd    = tx_cost_usd * tx_per_day * 30
```

Gas price and token price are volatile — every figure carries a source + date (§3 #8). SSTORE and unbounded loops dominate `gas_units` (§3 #3).

## 3. On-chain storage is paid-for-forever and public (§3 #4)

```
storage_cost = slots_written * gas_per_slot * gas_price_gwei * 1e-9 * token_price_usd
```

Put only consensus-critical data on-chain; push the rest off-chain with an on-chain hash pointer. The decision is cost AND privacy, never 'on-chain to be safe.'

## 4. Staking yield is illustrative, never advice (§3 #8, §2)

```
net_apr       = gross_reward_rate * (1 - validator_commission)
annual_reward = staked_amount * net_apr
```

This is an engineering model, not a return promise — investment/securities/tax route to a licensed authority (§2).
