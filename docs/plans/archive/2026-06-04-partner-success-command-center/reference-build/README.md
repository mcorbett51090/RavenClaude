# Reference build — Partner Success Command Center

A **known-good, verified** implementation of [Prompt 1](../codex-build-prompts.md#prompt-1--data-foundation-essential)
(data foundation) and [Prompt 2](../codex-build-prompts.md#prompt-2--the-daily-operating-system-dashboard-essential)
(the Daily Operating System dashboard).

**Why this exists:** it proves the prompts produce a coherent, working dashboard
_before_ anyone spends Codex credits, and it gives a zero-credit fallback — if
Codex stumbles on Prompt 1 or 2, copy these two files into your repo and you
already have a working dashboard.

## What's here

```
reference-build/
├── data/
│   ├── synthesize.py   # Prompt 1 output — generates the synthetic fixture
│   └── data.json       # generated: 25 partners (seeded, FERPA-safe)
└── dashboard.html      # Prompt 2 output — reads ./data/data.json, 4 widgets
```

## Run it

```shell
# 1. (re)generate the synthetic data — reproducible, byte-identical each run
python3 data/synthesize.py

# 2. serve the folder, then open the dashboard
python3 -m http.server 8000
#    → open http://localhost:8000/dashboard.html
```

> **Why a server?** Browsers block `fetch()` of a local file opened via
> `file://`, so double-clicking `dashboard.html` shows a friendly "couldn't
> load" message with this same tip. The one-line `http.server` above is the
> fix. (If you'd rather double-click with no server, ask Codex to inline the
> data as a `data.js` `window.__DATA__ = {…}` script instead of fetching JSON.)

## What was verified (no browser needed)

- `synthesize.py` is **reproducible** — byte-identical output across runs.
- **Score math holds** for all 25 partners: `priority_score == round(Σ breakdown[k]·weights[k] / 100)`.
- **Spread** meets the spec: ≥3 partners per health band (green/yellow/red), ≥2 per renewal bucket (180/120/90/60/30 d).
- **Referential integrity:** every `contacts/timeline/usage/…` row joins to a real `account_uid`.
- **Dashboard renders** (headless execution of its render logic): 4 widgets, all 25 Action Center rows, top-5 emphasis, every row shows its driving signal %, calendar capped at 15, no `undefined` leaks.

This is a reference fixture — the real dashboard is built in your own repo via
the prompts. Swap `data.json` for a real-data export later and `dashboard.html`
doesn't change.
