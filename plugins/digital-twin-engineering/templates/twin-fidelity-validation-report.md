# Twin-fidelity validation report — <asset / process name>

> The report that proves a built twin **matches the real asset** — the step teams skip and the one
> that makes a twin trustworthy. Reached from the validation plan in
> [`digital-twin-design-spec.md`](digital-twin-design-spec.md). The verdict is **fit-for-decision**,
> not "photoreal" — a twin can be wrong in absolute terms and still fit-for-decision, or gorgeous and unfit.

**Twin:** <name> · **Date:** <YYYY-MM-DD> · **Validated by:** <name> · **Decision it serves:** <the question + its error tolerance>

## 1. What "correct" means for this twin
- **Decision-relevant outputs (the SLIs):** <the specific outputs that must be right — e.g. predicted RUL, predicted throughput — NOT every variable>
- **Error tolerance the decision accepts:** <from the design spec — e.g. "±1 day RUL" / "±5% throughput">
- **Validation window / dataset:** <hold-out period · live comparison window · the assets/runs used>

## 2. Predicted-vs-actual
| SLI | Predicted | Actual | Error | Method |
|---|---|---|---|---|
| <RUL> | <value> | <value> | <MAE / RMSE / %> | <hold-out on failed units> |
| <throughput> | <value> | <value> | <RMSE / %> | <live window vs measured> |

- **Error bounds:** <MAE / RMSE / % error + a confidence interval — stated, not "looks close">
- **Where the twin diverges most:** <the regime / condition where error is worst — informs the next fidelity/calibration step>

## 3. Calibration
- **Gap found:** <where predicted-vs-actual exceeded tolerance>
- **What was calibrated:** <which model parameters were re-fit · method (parameter estimation / data assimilation)>
- **Error after calibration:** <the improved bounds>

## 4. Fit-for-decision verdict
- **Does the twin clear the decision's tolerance?** <YES / NO — against the tolerance in §1>
- **Verdict:** <fit-for-decision · fit with caveats (name them) · not yet fit — needs more fidelity/calibration/data>
- **If not fit:** <the specific next step — higher fidelity in the diverging regime / more calibration data / a different modeling approach>

## 5. Drift monitor (so it stays valid)
- **Drift SLI:** <the predicted-vs-actual error monitored over time>
- **Tolerance + alert routing:** <e.g. ±10% · to the maintenance channel · with a recalibration runbook link>
- **Recalibration trigger + owner:** <when it fires, who re-fits · root-cause triage: sensor vs model vs asset change>

## 6. Root-cause (if the twin was found off / drifting)
Name which of the three drifted — "recalibrate and move on" without this is symptom-chasing:
- [ ] **Sensor** — miscalibration / fault / degraded signal? <evidence>
- [ ] **Model** — a regime the model was never fit for? <evidence>
- [ ] **Asset** — real change: wear, damage, reconfiguration (e.g. re-impellered pump)? <evidence>
- **Root cause:** <the specific change, with evidence>

## 7. Seams (not this team)
- **Sensor/edge fault behind the drift:** embedded-iot-engineering
- **The raw history for retraining:** data-platform
- **Closed-loop control off a bidirectional twin:** robotics-autonomous-systems-engineering

## Open questions / risks
- <list>

**Sign-off:** <reviewer> · <date>
