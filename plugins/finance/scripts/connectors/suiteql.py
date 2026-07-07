#!/usr/bin/env python3
"""suiteql.py - the NetSuite SuiteQL trial-balance query + governed serial pager + tie-out.

WHAT THIS IS (and is NOT). A REFERENCE implementation of the SuiteQL extraction path that
feeds tb_stage.py. It runs against the offline ReplayTransport (zero creds, zero network);
the live HTTPS call to POST /services/rest/query/v1/suiteql is the CONSUMER's step. Not a
live-verified connector (../../CLAUDE.md sec.3). Every NetSuite fact below is settling-gated
(../../knowledge/finance-elt-connector-facts.md) — verify against a sandbox before go-live.

THE CORRECTNESS TRAP THIS MODULE EXISTS TO AVOID (FORGE G4a critic CE-2). A naive
period-scoped `SUM(TransactionAccountingLine.amount) ... WHERE postingperiod = <target>`
is correct for INCOME-STATEMENT accounts (flows) but WRONG for BALANCE-SHEET accounts
(stocks), which need CUMULATIVE-FROM-INCEPTION balances. The dangerous part: a period-only
TB can still FOOT TO ZERO while every BS account is understated — a silent-wrong number, the
worst class for a close. So build_tb_query classifies each account by NetSuite's `accttype`
enum and sums cumulatively for BS accounts / per-period for IS accounts. Footing to zero is
NECESSARY, NOT SUFFICIENT: the go-live gate (SG-B) is a tie-out to NetSuite's NATIVE Trial
Balance report per account, not merely a zero net.

Governance: NetSuite concurrency is account-level [settling-gated] — a TB pull is a single
SERIAL request stream, so we page serially (no fan-out) and hard-stop at the 100,000-result
SuiteQL cap LOUDLY (never silently truncate a trial balance).

Stdlib only. Python 3.8+.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from oauth_client import BACKOFF_RETRY, classify_error, honor_retry_after  # noqa: E402

# NetSuite documented `accttype` enum → statement class. BALANCE-SHEET types need cumulative
# balances; INCOME-STATEMENT types are period-scoped. [settling-gated — NetSuite Account record]
BALANCE_SHEET_TYPES = frozenset({
    "Bank", "AcctRec", "OthCurrAsset", "FixedAsset", "OthAsset", "DeferExpense",
    "AcctPay", "CredCard", "OthCurrLiab", "LongTermLiab", "DeferRevenue", "Equity",
})
INCOME_STATEMENT_TYPES = frozenset({
    "Income", "COGS", "Expense", "OthIncome", "OthExpense",
})
# Retained-earnings / cumulative types NetSuite computes; kept BS-cumulative if pulled.
SUITEQL_RESULT_CAP = 100_000   # NetSuite hard cap on total SuiteQL results [settling-gated]


class SuiteQLError(Exception):
    """A non-retryable SuiteQL page failure."""


class SuiteQLCapExceeded(SuiteQLError):
    """The result set exceeded the 100k SuiteQL cap — raised LOUDLY; never truncate a TB."""


def build_tb_query(period_id, *, subsidiary=None, book=None) -> str:
    """Return the SuiteQL text for a trial balance that is BS-cumulative / IS-period.

    The query UNIONs two branches on Account.accttype: balance-sheet accounts sum every
    posting line up to and including the target period (cumulative-from-inception); income-
    statement accounts sum only the target period. subsidiary + accountingbook + currency are
    exposed because omitting subsidiary silently pulls a consolidated (wrong-grain) result —
    the #1 tie-out failure mode netsuite_doctor.py diagnoses. Parameters are inlined as
    integer/whitelisted tokens only (no free-text interpolation) — the caller passes ids, not
    strings. [Query SHAPE is settling-gated: verify column/table names vs a sandbox — SG-B.]
    """
    period_id = int(period_id)                       # ints only — injection guard
    sub = f" AND t.subsidiary = {int(subsidiary)}" if subsidiary is not None else ""
    bk = f" AND tal.accountingbook = {int(book)}" if book is not None else ""
    bs_types = ", ".join(f"'{t}'" for t in sorted(BALANCE_SHEET_TYPES))
    is_types = ", ".join(f"'{t}'" for t in sorted(INCOME_STATEMENT_TYPES))
    return (
        "-- Balance-sheet accounts: CUMULATIVE from inception through the target period\n"
        "SELECT a.acctnumber AS account, a.fullname AS name, SUM(tal.amount) AS amount\n"
        "FROM transactionaccountingline tal\n"
        "  JOIN transaction t ON t.id = tal.transaction\n"
        "  JOIN account a ON a.id = tal.account\n"
        "  JOIN accountingperiod ap ON ap.id = t.postingperiod\n"
        f"WHERE tal.posting = 'T' AND a.accttype IN ({bs_types})\n"
        f"  AND ap.enddate <= (SELECT enddate FROM accountingperiod WHERE id = {period_id})"
        f"{sub}{bk}\n"
        "GROUP BY a.acctnumber, a.fullname\n"
        "UNION ALL\n"
        "-- Income-statement accounts: the TARGET PERIOD only\n"
        "SELECT a.acctnumber AS account, a.fullname AS name, SUM(tal.amount) AS amount\n"
        "FROM transactionaccountingline tal\n"
        "  JOIN transaction t ON t.id = tal.transaction\n"
        "  JOIN account a ON a.id = tal.account\n"
        f"WHERE tal.posting = 'T' AND a.accttype IN ({is_types})\n"
        f"  AND t.postingperiod = {period_id}{sub}{bk}\n"
        "GROUP BY a.acctnumber, a.fullname"
    )


def _page_field(page, key, default=None):
    if isinstance(page, dict):
        return page.get(key, default)
    return getattr(page, key, default)


def pull(transport, query, *, limit=1000, cap=SUITEQL_RESULT_CAP,
         retry_after=honor_retry_after, sleep=lambda s: None, max_retries=5) -> list:
    """Serially page a SuiteQL query via transport.suiteql(query, limit=, offset=). Each page
    exposes items + hasMore (+ optional status/headers for 429/5xx retry). Accumulates rows,
    honors Retry-After backoff on a throttled page, and HARD-STOPS at `cap` (loud) — a trial
    balance is never silently truncated."""
    rows: list = []
    offset = 0
    while True:
        attempt = 0
        while True:
            page = transport.suiteql(query, limit=limit, offset=offset)
            status = int(_page_field(page, "status", 200))
            if status == 200:
                break
            action = classify_error(status, _page_field(page, "body"))
            if action == BACKOFF_RETRY and attempt < max_retries:
                sleep(retry_after(_page_field(page, "headers"), attempt))
                attempt += 1
                continue
            raise SuiteQLError(f"SuiteQL page failed at offset={offset} status={status} action={action}")
        items = _page_field(page, "items", []) or []
        rows.extend(items)
        if len(rows) > cap:
            raise SuiteQLCapExceeded(
                f"SuiteQL result exceeded the {cap:,}-row cap at offset={offset}. A trial balance "
                "must not be truncated — scope the query (period/subsidiary) or enable "
                "SuiteAnalytics Connect for unlimited results."
            )
        if not _page_field(page, "hasMore", False):
            break
        offset += limit
    return rows


def tie_out(rows, *, tolerance=0.01) -> float:
    """Assert the trial balance nets to zero (debits == credits) within tolerance. Returns the
    net. Raises LOUDLY on a non-tying TB. NOTE: footing to zero is necessary, not sufficient —
    a wrong-subsidiary/wrong-book pull can still net to zero (see netsuite_doctor.py + SG-B)."""
    net = round(sum(float(r["amount"]) for r in rows), 2)
    if abs(net) > tolerance:
        raise SuiteQLError(
            f"Trial balance does not tie: net = {net} (should be ~0). Run netsuite_doctor.py "
            "diagnose for the ranked NetSuite-specific causes."
        )
    return net
