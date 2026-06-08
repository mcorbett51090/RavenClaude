#!/usr/bin/env bash
# check-data-science-research-anti-patterns.sh — advisory PreToolUse hook for the data-science-research plugin.
# Flags mechanically-detectable analysis anti-patterns on Edit/Write/MultiEdit. Advisory by default
# (exit 0, prints a notice); set DS_STRICT=1 to make it blocking (exit 2).
set -euo pipefail

file="${1:-}"
[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

# Only inspect Python-ish analysis files; skip everything else fast.
case "$file" in
  *.py | *.ipynb) ;;
  *) exit 0 ;;
esac

findings=()

# 1. A scaler/encoder/imputer fit before the train/test split — the classic leakage. Heuristic: the file
#    calls .fit_transform / .fit on a transformer AND a split exists, but the fit appears before the split.
if grep -qE "fit_transform|\.fit\(" "$file" 2>/dev/null \
  && grep -qE "train_test_split|TimeSeriesSplit|GroupKFold|KFold|StratifiedKFold|cross_val" "$file" 2>/dev/null; then
  fit_line=$(grep -nE "(StandardScaler|MinMaxScaler|RobustScaler|OneHotEncoder|OrdinalEncoder|TargetEncoder|SimpleImputer|KNNImputer)[^\n]*\.fit" "$file" 2>/dev/null | head -1 | cut -d: -f1 || true)
  split_line=$(grep -nE "train_test_split" "$file" 2>/dev/null | head -1 | cut -d: -f1 || true)
  if [ -n "$fit_line" ] && [ -n "$split_line" ] && [ "$fit_line" -lt "$split_line" ]; then
    findings+=("A transformer is fit (line $fit_line) before train_test_split (line $split_line) — fitting a scaler/encoder/imputer before the split leaks the test set. Fit inside the CV fold (use a Pipeline).")
  fi
fi

# 2. A modeling script with a single split and no cross-validation — a point estimate with no error bar.
if grep -qE "\.fit\(|\.predict\(" "$file" 2>/dev/null \
  && grep -qE "train_test_split" "$file" 2>/dev/null \
  && ! grep -qE "cross_val|KFold|StratifiedKFold|GroupKFold|TimeSeriesSplit|cross_validate" "$file" 2>/dev/null; then
  findings+=("A model is fit on a single train/test split with no cross-validation — a single split has no error bar. Use k-fold and report the spread.")
fi

# 3. A model script with no random seed set — nondeterministic / irreproducible.
if grep -qE "\.fit\(|train_test_split|RandomForest|XGB|LGBM|GradientBoosting" "$file" 2>/dev/null \
  && ! grep -qE "random_state|np\.random\.seed|random\.seed|seed\(|set_seed|PYTHONHASHSEED" "$file" 2>/dev/null; then
  findings+=("Modeling code with no random seed (random_state / np.random.seed) — set and thread a seed so the result is reproducible.")
fi

if [ ${#findings[@]} -eq 0 ]; then exit 0; fi

printf "%s\n" "── data-science-research advisory: review these before committing ──" >&2
for f in "${findings[@]}"; do printf "  • %s\n" "$f" >&2; done

if [ "${DS_STRICT:-0}" = "1" ]; then
  echo "(blocking: DS_STRICT=1)" >&2
  exit 2
fi
exit 0
