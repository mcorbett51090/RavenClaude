#!/usr/bin/env python3
"""
Tests for powerbi_ingest.py (report-regeneration `powerbi-ingest` skill).

Proves, OFFLINE, against a stdlib http.server MOCK of the three Power BI REST
endpoints this adapter drives (executeQueries, ExportTo trigger, ExportTo
poll+file), the load-bearing behaviors from the task brief:

  1. `data` mode runs every dax-kind binding's DAX query via a real HTTP round
     trip to the mock server, assembles a data.json-shaped fragment keyed by
     each binding's `data_query.expression`, stamps `source_period` on the
     top-level `period` AND on every value -- and NEVER leaks the fake bearer
     token into stdout, the written fragment, or the written receipt.
  2. `shot` mode drives the SAME ExportToFile primary route the probe uses
     (trigger -> poll -> download), returns a `regenerate`-class node embed
     with `source_period` stamped and `period_coherence_checked: false` -- and
     also never leaks the token.
  3. Fail-CLOSED without any network call: missing creds, missing manifest
     dax-kind bindings, and a missing/unresolvable source_period all report
     `not_captured` with the correct named fallback -- proven by asserting the
     mock server logged ZERO requests for those cases.
  4. The scripts/powerbi_probe.py refactor (shared execute_dax_query()) did
     not regress the CLI probe itself -- probe_data() is exercised against the
     SAME mock server.

Stdlib only (unittest + http.server + threading). Runs on Python 3.9.6. Every
test starts an ephemeral-port loopback server -- no real network egress.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

_SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SKILL_DIR))
_SCRIPTS_DIR = _SKILL_DIR.parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

import powerbi_ingest as pi  # noqa: E402
import powerbi_probe as pb  # noqa: E402

FAKE_TOKEN = "super-secret-fake-bearer-token-do-not-leak-9f8e7d"
FAKE_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"FAKE-EXPORT-PNG-BYTES" * 8


# ─────────────────────────────────────────────────────────────────────────────
# Mock Power BI REST server — executeQueries + ExportTo (trigger/poll/file)
# ─────────────────────────────────────────────────────────────────────────────

class _MockHandler(BaseHTTPRequestHandler):
    # Shared, test-controlled state (reset per test in setUp).
    dax_responses: dict = {}
    export_status_sequence: list = ["Running", "Succeeded"]  # states returned across successive polls
    request_log: list = []

    def log_message(self, format, *args):  # noqa: A002 - stdlib signature
        pass  # silence default request logging to stderr

    def _record(self) -> None:
        _MockHandler.request_log.append((self.command, self.path, self.headers.get("Authorization")))

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        return json.loads(raw.decode("utf-8")) if raw else {}

    def _send_json(self, status: int, obj: dict) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802 - stdlib method name
        self._record()
        if self.path.endswith("/executeQueries"):
            body = self._read_json_body()
            queries = body.get("queries") or [{}]
            query_text = queries[0].get("query", "")
            spec = _MockHandler.dax_responses.get(query_text)
            if spec is None:
                self._send_json(200, {"results": [{"tables": [{"rows": []}]}]})
            elif "error" in spec:
                self._send_json(200, {"results": [{"error": spec["error"]}]})
            elif spec.get("http_status"):
                self._send_json(spec["http_status"], {"error": spec.get("error_body", "rate limited")})
            else:
                self._send_json(200, {"results": [{"tables": [{"rows": [spec["row"]]}]}]})
            return
        if "/ExportTo" in self.path:
            _MockHandler.export_poll_index = 0
            first_status = _MockHandler.export_status_sequence[0]
            self._send_json(202, {"id": "export-abc-123", "status": first_status, "resourceFileExtension": ".png"})
            return
        self._send_json(404, {"error": f"mock: no POST route for {self.path}"})

    def do_GET(self) -> None:  # noqa: N802 - stdlib method name
        self._record()
        if self.path.endswith("/file"):
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(FAKE_PNG_BYTES)))
            self.end_headers()
            self.wfile.write(FAKE_PNG_BYTES)
            return
        if "/exports/" in self.path:
            _MockHandler.export_poll_index = getattr(_MockHandler, "export_poll_index", 0) + 1
            seq = _MockHandler.export_status_sequence
            idx = min(_MockHandler.export_poll_index, len(seq) - 1)
            self._send_json(200, {"status": seq[idx], "resourceFileExtension": ".png"})
            return
        self._send_json(404, {"error": f"mock: no GET route for {self.path}"})


def _start_mock_server() -> tuple:
    server = HTTPServer(("127.0.0.1", 0), _MockHandler)
    # poll_interval default (0.5s) makes server.shutdown() in tearDown() block up to
    # 0.5s per test; a much shorter interval keeps the (22-test) suite fast.
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
    thread.start()
    port = server.server_address[1]
    return server, thread, f"http://127.0.0.1:{port}/v1.0/myorg"


def _stop_mock_server(server: HTTPServer, thread: threading.Thread) -> None:
    server.shutdown()
    server.server_close()
    thread.join(timeout=5)


# ─────────────────────────────────────────────────────────────────────────────
# Fixture manifest
# ─────────────────────────────────────────────────────────────────────────────

DAX_REVENUE = 'EVALUATE ROW("revenue_total", [Revenue Total])'
DAX_REPORT_DATE = 'EVALUATE ROW("report_date", [Report Date])'
DAX_BAD = 'EVALUATE ROW("bad_measure", [Missing Measure])'


def _binding(node_id, klass, pbi_route, source_period, data_query, source="acme-pbi-model"):
    return {
        "node_id": node_id,
        "anchor": {"kind": "element_id", "value": node_id},
        "class": klass,
        "confidence": 0.95,
        "provenance": {"source": source, "source_period": source_period, "method": "rule-based", "pbi_route": pbi_route},
        "data_query": data_query,
    }


def _manifest_doc(bindings) -> dict:
    return {
        "manifest_version": "0.1.0",
        "rsg_schema_version": "0.1.0",
        "template_id": "mock-template",
        "format": "html",
        "bindings": bindings,
    }


def _write_manifest(tmpdir: str, bindings) -> Path:
    path = Path(tmpdir) / "manifest.json"
    path.write_text(json.dumps(_manifest_doc(bindings)), encoding="utf-8")
    return path


def _full_bindings():
    return [
        _binding("kpi-revenue", "surgical", "xmla", "2025-Q1",
                 {"kind": "dax", "expression": DAX_REVENUE, "source_ref": "acme-pbi-model"}),
        _binding("kpi-report-date", "surgical", "rest", "2025-Q1",
                 {"kind": "dax", "expression": DAX_REPORT_DATE, "source_ref": "acme-pbi-model"}),
        _binding("kpi-bad", "surgical", "rest", "2025-Q1",
                 {"kind": "dax", "expression": DAX_BAD, "source_ref": "acme-pbi-model"}),
        _binding("hdr-period", "surgical", None, "2025-Q1",
                 {"kind": "literal-from-new-source", "expression": "meta.period_label", "source_ref": "acme-q1-2025"},
                 source="acme-q1-2025"),
        _binding("pbi-screenshot", "regenerate", "screenshot", "2025-Q1",
                 {"kind": "screenshot-capture", "expression": "capture:revenue-trend", "source_ref": "acme-pbi-report"},
                 source="acme-pbi-report"),
        _binding("pbi-screenshot-no-period", "regenerate", "screenshot", None,
                 {"kind": "screenshot-capture", "expression": "capture:no-period", "source_ref": "acme-pbi-report"},
                 source="acme-pbi-report"),
        _binding("odd-class-node", "surgical", None, "2025-Q2",
                 {"kind": "file-cell", "expression": "misc.value", "source_ref": "acme-q1-2025"},
                 source="acme-q1-2025"),
    ]


_ENV_KEYS = (
    "POWERBI_ACCESS_TOKEN", "POWERBI_WORKSPACE_ID", "POWERBI_DATASET_ID",
    "POWERBI_REPORT_ID", "POWERBI_SHOT_OUT_PATH",
)


class _MockServerTestCase(unittest.TestCase):
    """Common setup: mock server + POWERBI_API_BASE monkeypatch + env sandbox."""

    def setUp(self) -> None:
        _MockHandler.dax_responses = {
            DAX_REVENUE: {"row": {"[revenue_total]": 4821300}},
            DAX_REPORT_DATE: {"row": {"[report_date]": "2025-01-15"}},
            DAX_BAD: {"error": {"code": "DAX_ERROR", "message": "Column 'Missing Measure' not found"}},
        }
        _MockHandler.export_status_sequence = ["Running", "Succeeded"]
        _MockHandler.request_log = []

        self._server, self._thread, mock_base = _start_mock_server()
        self._orig_api_base = pb.POWERBI_API_BASE
        self._orig_poll_interval = pb.EXPORT_POLL_INTERVAL_SECONDS
        pb.POWERBI_API_BASE = mock_base
        pb.EXPORT_POLL_INTERVAL_SECONDS = 0.01  # keep the poll loop fast in tests

        self._orig_env = {k: os.environ.get(k) for k in _ENV_KEYS}
        for k in _ENV_KEYS:
            os.environ.pop(k, None)

        self._tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        _stop_mock_server(self._server, self._thread)
        pb.POWERBI_API_BASE = self._orig_api_base
        pb.EXPORT_POLL_INTERVAL_SECONDS = self._orig_poll_interval
        for k, v in self._orig_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self._tmpdir.cleanup()

    def _run_cli(self, argv: list) -> tuple:
        """Invoke powerbi_ingest.main() in-process (so the monkeypatched
        POWERBI_API_BASE applies) and capture stdout, mirroring what a real
        pipeline caller would see on the CLI boundary."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code = pi.main(argv)
        return exit_code, buf.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# `data` mode
# ─────────────────────────────────────────────────────────────────────────────

class TestIngestData(_MockServerTestCase):
    def _set_creds(self, dataset_id="ds-guid-999") -> None:
        os.environ["POWERBI_ACCESS_TOKEN"] = FAKE_TOKEN
        os.environ["POWERBI_WORKSPACE_ID"] = "ws-guid-111"
        os.environ["POWERBI_DATASET_ID"] = dataset_id

    def test_partial_success_end_to_end_via_cli(self):
        self._set_creds()
        manifest_path = _write_manifest(self._tmpdir.name, _full_bindings())
        fragment_out = Path(self._tmpdir.name) / "data-fragment.json"
        receipt_out = Path(self._tmpdir.name) / "receipt.json"

        exit_code, stdout = self._run_cli([
            "data", "--manifest", str(manifest_path),
            "--out", str(fragment_out), "--receipt-out", str(receipt_out),
            "--format", "json",
        ])
        self.assertEqual(exit_code, 0)

        receipt = json.loads(stdout)
        self.assertEqual(receipt["verdict"], "PARTIAL")
        self.assertEqual(receipt["bindings_dax"], 3)
        self.assertEqual(len(receipt["succeeded"]), 2)
        self.assertEqual(len(receipt["failed"]), 1)
        self.assertEqual(receipt["failed"][0]["node_id"], "kpi-bad")
        self.assertIn("Missing Measure", receipt["failed"][0]["reason"])

        # source_ref_mismatches: fixture's source_ref is "acme-pbi-model", env dataset is "ds-guid-999"
        mismatched_nodes = {m["node_id"] for m in receipt["source_ref_mismatches"]}
        self.assertIn("kpi-revenue", mismatched_nodes)
        self.assertIn("kpi-report-date", mismatched_nodes)

        # the fragment — data.json-shaped, keyed by data_query.expression, period stamped
        fragment = receipt["fragment"]
        self.assertEqual(fragment["dataset_id"], "ds-guid-999")
        self.assertEqual(fragment["period"], "2025-Q1")
        self.assertEqual(fragment["values"][DAX_REVENUE], {"value": "4821300", "type": "number", "period": "2025-Q1"})
        self.assertEqual(fragment["values"][DAX_REPORT_DATE], {"value": "2025-01-15", "type": "date", "period": "2025-Q1"})
        self.assertNotIn(DAX_BAD, fragment["values"])

        # the written fragment file matches the embedded fragment exactly
        on_disk = json.loads(fragment_out.read_text(encoding="utf-8"))
        self.assertEqual(on_disk, fragment)
        self.assertEqual(json.loads(receipt_out.read_text(encoding="utf-8")), receipt)

        # the mock server actually saw a real Authorization header (auth flow was exercised)
        auth_values = [h for _, _, h in _MockHandler.request_log if h]
        self.assertTrue(auth_values, "expected at least one authenticated request to the mock server")
        self.assertTrue(all(h == f"Bearer {FAKE_TOKEN}" for h in auth_values))

        # the token NEVER appears in anything this process printed or wrote
        self.assertNotIn(FAKE_TOKEN, stdout)
        self.assertNotIn(FAKE_TOKEN, fragment_out.read_text(encoding="utf-8"))
        self.assertNotIn(FAKE_TOKEN, receipt_out.read_text(encoding="utf-8"))
        self.assertNotIn(FAKE_TOKEN, json.dumps(receipt))

    def test_all_success_verdict_pass(self):
        self._set_creds()
        good_bindings = [b for b in _full_bindings() if b["node_id"] in ("kpi-revenue", "kpi-report-date")]
        manifest_path = _write_manifest(self._tmpdir.name, good_bindings)

        exit_code, stdout = self._run_cli(["data", "--manifest", str(manifest_path), "--format", "json"])
        self.assertEqual(exit_code, 0)
        receipt = json.loads(stdout)
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["failed"], [])
        self.assertEqual(len(receipt["succeeded"]), 2)

    def test_missing_creds_fails_closed_not_captured_no_network(self):
        # deliberately do NOT set any POWERBI_* creds
        manifest_path = _write_manifest(self._tmpdir.name, _full_bindings())
        exit_code, stdout = self._run_cli(["data", "--manifest", str(manifest_path), "--format", "json"])
        self.assertEqual(exit_code, 0)
        receipt = json.loads(stdout)
        self.assertEqual(receipt["verdict"], "not_captured")
        self.assertIn("POWERBI_ACCESS_TOKEN", receipt["reason"])
        self.assertIn("labeled unverified", receipt["fallback"])
        self.assertIsNone(receipt["fragment"])
        self.assertEqual(_MockHandler.request_log, [], "no network call should fire without creds")

    def test_no_dax_bindings_not_captured(self):
        self._set_creds()
        non_dax_only = [b for b in _full_bindings() if b["data_query"]["kind"] != "dax"]
        manifest_path = _write_manifest(self._tmpdir.name, non_dax_only)
        exit_code, stdout = self._run_cli(["data", "--manifest", str(manifest_path), "--format", "json"])
        self.assertEqual(exit_code, 0)
        receipt = json.loads(stdout)
        self.assertEqual(receipt["verdict"], "not_captured")
        self.assertIn("no dax-kind bindings", receipt["reason"])
        self.assertEqual(_MockHandler.request_log, [])

    def test_source_period_cli_override_stamps_every_value(self):
        self._set_creds()
        good_bindings = [b for b in _full_bindings() if b["node_id"] in ("kpi-revenue", "kpi-report-date")]
        manifest_path = _write_manifest(self._tmpdir.name, good_bindings)
        exit_code, stdout = self._run_cli([
            "data", "--manifest", str(manifest_path), "--source-period", "2099-Q4", "--format", "json",
        ])
        self.assertEqual(exit_code, 0)
        receipt = json.loads(stdout)
        self.assertEqual(receipt["fragment"]["period"], "2099-Q4")
        for spec in receipt["fragment"]["values"].values():
            self.assertEqual(spec["period"], "2099-Q4")

    def test_text_format_does_not_crash_and_hides_no_secrets(self):
        self._set_creds()
        manifest_path = _write_manifest(self._tmpdir.name, _full_bindings())
        exit_code, stdout = self._run_cli(["data", "--manifest", str(manifest_path), "--format", "text"])
        self.assertEqual(exit_code, 0)
        self.assertIn("verdict:", stdout)
        self.assertNotIn(FAKE_TOKEN, stdout)


# ─────────────────────────────────────────────────────────────────────────────
# `shot` mode
# ─────────────────────────────────────────────────────────────────────────────

class TestIngestShot(_MockServerTestCase):
    def _set_creds(self) -> None:
        os.environ["POWERBI_ACCESS_TOKEN"] = FAKE_TOKEN
        os.environ["POWERBI_WORKSPACE_ID"] = "ws-guid-111"
        os.environ["POWERBI_REPORT_ID"] = "report-guid-222"

    def test_success_end_to_end_via_cli(self):
        self._set_creds()
        manifest_path = _write_manifest(self._tmpdir.name, _full_bindings())
        capture_out = Path(self._tmpdir.name) / "capture.png"
        receipt_out = Path(self._tmpdir.name) / "shot-receipt.json"

        exit_code, stdout = self._run_cli([
            "shot", "--manifest", str(manifest_path), "--node-id", "pbi-screenshot",
            "--out", str(capture_out), "--receipt-out", str(receipt_out), "--format", "json",
        ])
        self.assertEqual(exit_code, 0)
        receipt = json.loads(stdout)

        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["node_id"], "pbi-screenshot")
        self.assertEqual(receipt["class"], "regenerate")
        self.assertEqual(receipt["route"], "export-to-file")
        self.assertEqual(receipt["source_period"], "2025-Q1")
        self.assertFalse(receipt["period_coherence_checked"])
        self.assertTrue(receipt["path"].endswith(".png"))

        written = Path(receipt["path"])
        self.assertTrue(written.is_file())
        self.assertEqual(written.read_bytes(), FAKE_PNG_BYTES)

        # the poll loop was actually exercised (Running -> Succeeded), not just the trigger
        get_paths = [p for m, p, _ in _MockHandler.request_log if m == "GET"]
        self.assertTrue(any("/exports/" in p and not p.endswith("/file") for p in get_paths),
                         "expected at least one status-poll GET")
        self.assertTrue(any(p.endswith("/file") for p in get_paths), "expected the file-download GET")

        self.assertEqual(json.loads(receipt_out.read_text(encoding="utf-8")), receipt)

        # token never leaks
        self.assertNotIn(FAKE_TOKEN, stdout)
        self.assertNotIn(FAKE_TOKEN, receipt_out.read_text(encoding="utf-8"))
        self.assertNotIn(FAKE_TOKEN, json.dumps(receipt))
        auth_values = [h for _, _, h in _MockHandler.request_log if h]
        self.assertTrue(all(h == f"Bearer {FAKE_TOKEN}" for h in auth_values))

    def test_missing_period_refuses_before_any_network_call(self):
        self._set_creds()
        manifest_path = _write_manifest(self._tmpdir.name, _full_bindings())
        exit_code, stdout = self._run_cli([
            "shot", "--manifest", str(manifest_path), "--node-id", "pbi-screenshot-no-period", "--format", "json",
        ])
        self.assertEqual(exit_code, 0)
        receipt = json.loads(stdout)
        self.assertEqual(receipt["verdict"], "not_captured")
        self.assertIsNone(receipt["source_period"])
        self.assertIn("no source_period resolvable", receipt["reason"])
        self.assertIn("user-provided image", receipt["fallback"])
        self.assertEqual(_MockHandler.request_log, [], "must refuse BEFORE attempting capture")

    def test_class_mismatch_warns_but_still_attempts_capture(self):
        self._set_creds()
        manifest_path = _write_manifest(self._tmpdir.name, _full_bindings())
        exit_code, stdout = self._run_cli([
            "shot", "--manifest", str(manifest_path), "--node-id", "odd-class-node", "--format", "json",
        ])
        self.assertEqual(exit_code, 0)
        receipt = json.loads(stdout)
        self.assertEqual(receipt["verdict"], "PASS")  # capture itself is class-agnostic
        self.assertEqual(receipt["class"], "regenerate")  # embed is ALWAYS regenerate, regardless of the source binding's class
        self.assertTrue(any("expected class='regenerate'" in w for w in receipt["warnings"]))

    def test_node_not_found_is_a_usage_error_exit_2(self):
        self._set_creds()
        manifest_path = _write_manifest(self._tmpdir.name, _full_bindings())
        exit_code, stdout = self._run_cli([
            "shot", "--manifest", str(manifest_path), "--node-id", "does-not-exist", "--format", "json",
        ])
        self.assertEqual(exit_code, 2)
        self.assertEqual(_MockHandler.request_log, [])

    def test_missing_creds_fails_closed_not_captured_no_network(self):
        manifest_path = _write_manifest(self._tmpdir.name, _full_bindings())
        exit_code, stdout = self._run_cli([
            "shot", "--manifest", str(manifest_path), "--node-id", "pbi-screenshot", "--format", "json",
        ])
        self.assertEqual(exit_code, 0)
        receipt = json.loads(stdout)
        self.assertEqual(receipt["verdict"], "not_captured")
        self.assertIn("user-provided image", receipt["fallback"])
        self.assertEqual(_MockHandler.request_log, [])


# ─────────────────────────────────────────────────────────────────────────────
# The scripts/powerbi_probe.py refactor (shared execute_dax_query) — regression
# ─────────────────────────────────────────────────────────────────────────────

class TestProbeRefactorRegression(_MockServerTestCase):
    def test_probe_data_still_passes_against_mock_server(self):
        os.environ["POWERBI_ACCESS_TOKEN"] = FAKE_TOKEN
        os.environ["POWERBI_WORKSPACE_ID"] = "ws-guid-111"
        os.environ["POWERBI_DATASET_ID"] = "ds-guid-999"
        # probe_data() always queries DEFAULT_DAX_QUERY unless POWERBI_DAX_QUERY is set
        os.environ["POWERBI_DAX_QUERY"] = DAX_REVENUE
        receipt = pb.probe_data()
        self.assertEqual(receipt["verdict"], "PASS")
        self.assertEqual(receipt["route"], "rest-execute-queries")
        self.assertEqual(receipt["row_count"], 1)
        self.assertNotIn(FAKE_TOKEN, json.dumps(receipt))

    def test_execute_dax_query_surfaces_rate_limit_reason(self):
        _MockHandler.dax_responses["RATE_LIMITED_QUERY"] = {"http_status": 429, "error_body": "Too Many Requests"}
        outcome = pb.execute_dax_query(
            "RATE_LIMITED_QUERY", workspace_id="ws", dataset_id="ds", token=FAKE_TOKEN,
        )
        self.assertFalse(outcome["ok"])
        self.assertIn("429", outcome["reason"])
        self.assertIn("rate limit", outcome["reason"])
        self.assertNotIn(FAKE_TOKEN, outcome["reason"])


# ─────────────────────────────────────────────────────────────────────────────
# Pure-function unit tests (no server needed)
# ─────────────────────────────────────────────────────────────────────────────

class TestInferTypeAndValue(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(pi.infer_type_and_value(4821300), ("number", "4821300"))

    def test_float_non_integer(self):
        self.assertEqual(pi.infer_type_and_value(18.7), ("number", "18.7"))

    def test_iso_date_string(self):
        self.assertEqual(pi.infer_type_and_value("2025-01-15"), ("date", "2025-01-15"))

    def test_period_yq_string(self):
        self.assertEqual(pi.infer_type_and_value("2025-Q1"), ("period", "2025-Q1"))

    def test_period_qy_string_uppercased(self):
        self.assertEqual(pi.infer_type_and_value("q1 2025"), ("period", "Q1 2025"))

    def test_plain_string(self):
        self.assertEqual(pi.infer_type_and_value("North Region"), ("string", "North Region"))

    def test_bool_is_string_not_number(self):
        # bool is a subclass of int in Python -- must not be misread as "number"
        self.assertEqual(pi.infer_type_and_value(True), ("string", "True"))


class TestGuardPath(unittest.TestCase):
    def test_rejects_traversal(self):
        with self.assertRaises(pi.IngestError):
            pi._guard_path("../etc/passwd", must_exist=False)

    def test_rejects_missing_required_file(self):
        with self.assertRaises(pi.IngestError):
            pi._guard_path("/nonexistent/path/should/not/exist.json", must_exist=True)


if __name__ == "__main__":
    unittest.main()
