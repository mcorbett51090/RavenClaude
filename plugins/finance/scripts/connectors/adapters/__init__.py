"""Per-provider connector adapters.

Each adapter turns a recorded (synthetic) API payload into a RAW vendor-shaped export
FILE — the exact artifact `tb_stage.py` already normalizes into the canonical staging
schema. Adapters deliberately do NOT re-implement staging: they stop at "produced a raw
export CSV", and the accompanying per-provider column-map (fixtures/<provider>/column-map.json)
tells tb_stage how to normalize it. Reference-impl / offline only; see the package docstrings.
"""
from . import intacct, netsuite, qbo, xero

ADAPTERS = {
    "qbo": qbo,
    "netsuite": netsuite,
    "xero": xero,
    "intacct": intacct,
}
