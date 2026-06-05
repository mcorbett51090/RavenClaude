# Profile serving latency under realistic load before production deployment

**Status:** Absolute rule
**Domain:** MLOps / model serving
**Applies to:** `ml-engineering`

---

## Why this exists

Inference latency profiled on a developer laptop against a single example is rarely representative of production latency under concurrent load, with production feature retrieval, and on the actual serving hardware. A model that runs in 30ms locally may take 400ms on the target GPU/CPU configuration when handling concurrent requests, retrieving features from the online store, and running postprocessing. Discovering this after deploy means an emergency serving optimization sprint under production SLO pressure. Profile before deploy and the optimization is planned work.

## How to apply

Run a latency profile job as part of the model promotion pipeline. Test on the target hardware type with a realistic concurrency level and realistic feature inputs (not synthetic zeros).

```python
# Serving latency profile script — run in the staging serving environment
import concurrent.futures, time, statistics, mlflow.pyfunc

MODEL_URI = "models:/churn-predictor/staging"
TARGET_P95_MS = 150   # defined serving budget (see optimize-serving-to-a-budget.md)
CONCURRENCY = 20      # realistic concurrent requests

model = mlflow.pyfunc.load_model(MODEL_URI)

# Use realistic feature values sampled from the validation set
sample_inputs = load_sample_inputs("data/latency_probe_samples.parquet", n=100)

def single_request(inputs):
    start = time.perf_counter()
    _ = model.predict(inputs)
    return (time.perf_counter() - start) * 1000  # ms

latencies = []
with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
    futures = [pool.submit(single_request, inp) for inp in sample_inputs * 5]
    latencies = [f.result() for f in futures]

p50 = statistics.median(latencies)
p95 = statistics.quantiles(latencies, n=20)[18]   # 95th percentile
p99 = statistics.quantiles(latencies, n=100)[98]

print(f"Latency profile: P50={p50:.1f}ms P95={p95:.1f}ms P99={p99:.1f}ms")

if p95 > TARGET_P95_MS:
    raise ValueError(f"P95 latency {p95:.1f}ms exceeds budget {TARGET_P95_MS}ms — optimize before promote")
```

**Do:**
- Profile on the same hardware tier (instance type, GPU SKU) that production will use.
- Include the full inference path: feature retrieval + preprocessing + model forward pass + postprocessing.
- Test at realistic concurrency — 1 request at a time is not a production profile.
- Gate model promotion on passing the latency budget defined in the serving SLO.

**Don't:**
- Profile on a development laptop and extrapolate to production hardware.
- Use only the P50 latency as the gate — the P95 and P99 are what users experience on bad days.
- Skip the profile because the model "looks fast" — GPU batching and feature retrieval latency are not visible in a local test.

## Edge cases / when the rule does NOT apply

Batch inference does not need latency profiling in the same way — profile throughput (records per second) and total job runtime instead. Set a throughput budget that ensures the batch job completes within its schedule window.

## See also

- [`../agents/model-serving-engineer.md`](../agents/model-serving-engineer.md) — owns serving infrastructure, latency optimization, and the serving budget.
- [`./optimize-serving-to-a-budget.md`](./optimize-serving-to-a-budget.md) — the latency budget the profile is tested against.

## Provenance

Codifies serving latency profiling practices from TFX and MLflow serving documentation, and the SLO-driven serving model promotion pattern from Chip Huyen's "Designing Machine Learning Systems."

---

_Last reviewed: 2026-06-05 by `claude`_
