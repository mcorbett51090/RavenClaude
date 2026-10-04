import base64
import contextlib
import copy
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

os.environ["ATLAS_TEST_ALLOW_ANY_TREE"] = "1"
TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))

import render  # noqa: E402
import validate  # noqa: E402
from atlas_common import DATA_DIR, SCHEMA_DIR  # noqa: E402
from quotes import CONTEXT_SCRUBBED, INSTALL_DESCRIPTION, install_text  # noqa: E402

DROP = object()  # a fixture change that removes the key

SURFACES = ["claude-code", "grok-bot"]
HOSTS = {"claude-code": "code.claude.com", "grok-bot": "docs.x.ai"}
CORE_ROWS = [
    "F01.loop-shape",
    "F01.turn-limits",
    "F17.model-picker",
    "F18.effort-values",
    "F19.named-modes",
    "F19.plan-mode",
]
OPTIONAL_ROW = "F90.editor-lsp"
REAL_FACETS = json.loads((DATA_DIR / "facets.json").read_text(encoding="utf-8"))
REAL_SURFACES = json.loads((DATA_DIR / "surfaces.json").read_text(encoding="utf-8"))
SPAN_SHA = "f" * 64


def install_line():
    """A piped installer line, assembled here so the file never contains the literal shape."""
    return "cu" + "rl -fsSL https://example.com/get | " + "s" + "h"


def eid(surface, number):
    return f"E-{surface}-{number:05d}"


def make_facets():
    facets = []
    for facet in copy.deepcopy(REAL_FACETS["facets"]):
        facet["rows"] = [r for r in facet["rows"] if r["id"] in CORE_ROWS]
        if facet["rows"]:
            facets.append(facet)
    kept = [r["id"] for f in facets for r in f["rows"]]
    assert sorted(kept) == sorted(CORE_ROWS), "fixture rows must come from the real facets.json"
    optional_row = {"id": OPTIONAL_ROW, "label": "LSP", "definition": "d", "lever": None}
    return {
        "schema_version": 1,
        "facets": facets,
        "optional_facets": [
            {"id": "F90", "name": "Editor", "definition": "d", "rows": [optional_row]}
        ],
        "unmapped": REAL_FACETS["unmapped"],
    }


def make_surfaces():
    chosen = [s for s in REAL_SURFACES["surfaces"] if s["id"] in SURFACES]
    assert [s["id"] for s in chosen] == SURFACES
    return {"schema_version": 1, "surfaces": chosen}


def make_evidence(surface, number, **changes):
    record = {
        "id": eid(surface, number),
        "surface": surface,
        "tier": "E1",
        "url": f"https://{HOSTS[surface]}/docs/page{number}",
        "retrieved": "2026-10-04",
        "sha256": "a" * 64,
        "locator": {"heading": "Heading", "raw_line_start": 1, "raw_line_end": 2},
        "quote": "The agent loop runs until the task is done.",
        "context_before": ["line before"],
        "context_after": ["line after"],
        "quote_verified": True,
    }
    apply_changes(record, changes)
    return record


def make_cell(surface, row, state, verification, **extra):
    cell = {
        "id": f"{surface}/{row}",
        "surface": surface,
        "row": row,
        "state": state,
        "verification": verification,
        "evidence": [],
    }
    cell.update(extra)
    return cell


def make_cells(surface):
    e1, e2, e3 = eid(surface, 1), eid(surface, 2), eid(surface, 3)
    sweep = {
        "terms": ["mode"],
        "corpus_sha256": "e" * 64,
        "hits": 2,
        "hits_reviewed": 2,
        "positive_control_term": "model",
        "positive_control_hits": 5,
    }
    cells = [
        make_cell(surface, "F01.loop-shape", "supported", "verified", evidence=[e1]),
        make_cell(
            surface,
            "F01.turn-limits",
            "partial",
            "verified",
            evidence=[e1],
            limitation="Only in print mode.",
        ),
        make_cell(surface, "F17.model-picker", "not-exposed", "verified", vendor_statement=e2),
        make_cell(surface, "F18.effort-values", "not-applicable", "verified", na_quote=e3),
        make_cell(
            surface,
            "F19.named-modes",
            "undocumented",
            "unverified",
            sweep_report=sweep,
            settles_by="probe: re-run the sweep on the full mirror",
        ),
        make_cell(
            surface,
            "F19.plan-mode",
            "supported",
            "unverified",
            evidence=[e1],
            settles_by="probe: run plan mode once",
        ),
    ]
    if surface == "claude-code":
        cells.append(make_cell(surface, "U00", "supported", "verified", evidence=[eid(surface, 5)]))
    return cells


def make_levers():
    pointer = {"file": "agent-routing-matrix.json", "path": "$.rules[0]"}
    return {
        "levers": [
            {
                "surface": "claude-code",
                "lever": "model",
                "row": "F17.model-picker",
                "model": None,
                "location_kind": "cli_flag",
                "literal": "--model",
                "state": "supported",
                "verification": "verified",
                "evidence": [eid("claude-code", 6)],
            },
            {
                "surface": "grok-bot",
                "lever": "effort",
                "row": "F18.effort-values",
                "location_kind": "vendor_managed",
                "state": "not-exposed",
                "verification": "verified",
                "evidence": [eid("grok-bot", 6)],
            },
        ],
        "task_shape_rows": [
            {
                "surface": "claude-code",
                "task_class": "refactor",
                "pointer": pointer,
                "basis": "framework-rule",
                "pending_label": None,
                "lever_settings": [],
            }
        ],
    }


def make_snapshot():
    return {
        "freeze_start": "2026-10-04",
        "freeze_end": "2026-10-04",
        "columns": [
            {
                "surface": "claude-code",
                "retrieved": "2026-10-04",
                "version": None,
                "version_source": None,
            }
        ],
        "index_hashes": {"claude-code": "b" * 64},
        "matrix_sha": "c" * 40,
    }


def make_entry(number, kind, cells, **extra):
    entry = {
        "id": f"ENH-{number:03d}",
        "title": f"Entry {number}",
        "type": kind,
        "surfaces": ["claude-code"],
        "cells": cells,
        "proposal": "Do the small thing.",
        "value": 2,
        "reach": 2,
        "effort": 1,
        "risk": 1,
        "basis": {"kind": "observation"},
        "rank": number,
        "status": "proposed",
    }
    entry.update(extra)
    return entry


def make_register():
    claim = {"blob_sha": "d" * 40, "path": "README.md", "line": 3, "quote": "a repo statement"}
    verified, unverified = "claude-code/U00", "claude-code/F19.plan-mode"
    return {
        "entries": [
            make_entry(
                1, "extend", [verified], repo_files=[{"path": "new/file.md", "exists": False}]
            ),
            make_entry(2, "probe", [unverified]),
            make_entry(3, "correct", [verified], repo_claim=claim, score=4.5),
        ]
    }


def apply_changes(obj, changes):
    for key, value in changes.items():
        if value is DROP:
            obj.pop(key, None)
        else:
            obj[key] = value
    return obj


class Fixture:
    """A minimal valid dataset in a temp directory: two surfaces, six frozen rows each."""

    def __init__(self, root):
        self.root = Path(root)
        self.write("facets.json", make_facets())
        self.write("surfaces.json", make_surfaces())
        for surface in SURFACES:
            self.write(f"cells/{surface}.json", {"surface": surface, "cells": make_cells(surface)})
            records = [make_evidence(surface, n) for n in (1, 2, 3, 4, 5, 6)]
            self.write(f"evidence/{surface}.json", {"surface": surface, "evidence": records})
        self.write("levers.json", make_levers())
        self.write("register.json", make_register())
        self.write("snapshot.json", make_snapshot())

    def path(self, rel):
        return self.root / rel

    def read(self, rel):
        return json.loads(self.path(rel).read_text(encoding="utf-8"))

    def write(self, rel, doc):
        path = self.path(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=1), encoding="utf-8")

    def edit(self, rel, fn):
        doc = self.read(rel)
        fn(doc)
        self.write(rel, doc)

    def _edit_item(self, rel, key, predicate, changes):
        def fn(doc):
            matches = [x for x in doc[key] if predicate(x)]
            assert len(matches) == 1, f"{rel}: {len(matches)} matches"
            apply_changes(matches[0], changes)

        self.edit(rel, fn)

    def cell(self, surface, row, **changes):
        self._edit_item(f"cells/{surface}.json", "cells", lambda c: c["row"] == row, changes)

    def evidence(self, surface, number, **changes):
        self._edit_item(
            f"evidence/{surface}.json",
            "evidence",
            lambda e: e["id"] == eid(surface, number),
            changes,
        )

    def add_cell(self, surface, cell):
        self.edit(f"cells/{surface}.json", lambda d: d["cells"].append(cell))

    def lever(self, index, **changes):
        self.edit("levers.json", lambda d: apply_changes(d["levers"][index], changes))

    def task_row(self, index, **changes):
        self.edit("levers.json", lambda d: apply_changes(d["task_shape_rows"][index], changes))

    def entry(self, index, **changes):
        self.edit("register.json", lambda d: apply_changes(d["entries"][index], changes))

    def snapshot(self, **changes):
        self.edit("snapshot.json", lambda d: apply_changes(d, changes))

    def html(self, name, content):
        path = self.root / "html" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    @property
    def html_flags(self):
        return ("--html-dir", str(self.root / "html"))


class ValidatorCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._count = 0

    def fresh(self):
        self._count += 1
        return Fixture(Path(self._tmp.name) / f"d{self._count}")

    def run_validator(self, fx, *flags, repo_paths=False):
        """Run the CLI; temp-dir data has no repository, so pointer files are skipped by default."""
        extra = [] if repo_paths else ["--no-repo-paths"]
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = validate.main(["--data-dir", str(fx.root), *extra, *flags])
        return code, buffer.getvalue()

    @staticmethod
    def error_lines(out):
        return [line for line in out.splitlines() if line.startswith("error ")]

    def error_rules(self, out):
        return {line.split()[1] for line in self.error_lines(out)}

    def assertClean(self, fx, *flags):
        code, out = self.run_validator(fx, *flags)
        self.assertEqual(self.error_lines(out), [], out)
        self.assertEqual(code, 0, out)
        return out

    def assertRejected(self, fx, rule, *flags, also=(), where=None):
        """Non-zero exit, the rule is named, and no rule outside rule+also fired."""
        code, out = self.run_validator(fx, *flags)
        rules = self.error_rules(out)
        self.assertNotEqual(code, 0, out)
        self.assertIn(rule, rules, out)
        self.assertEqual(rules - {rule, *also}, set(), out)
        if where is not None:
            hit = [ln for ln in self.error_lines(out) if ln.split()[1] == rule and where in ln]
            self.assertTrue(hit, f"no {rule} finding mentioning {where!r}:\n{out}")
        return out

    def cases(self, rule, table, *flags):
        """Each (name, mutate, also) must be rejected under ``rule`` and only ``rule``+also."""
        for name, mutate, also in table:
            with self.subTest(name):
                fx = self.fresh()
                mutate(fx)
                self.assertRejected(fx, rule, *flags, also=also)

    def passes(self, table, *flags):
        for name, mutate in table:
            with self.subTest(name):
                fx = self.fresh()
                mutate(fx)
                self.assertClean(fx, *flags)


CC, GB = "claude-code", "grok-bot"
LOOP, TURN, PICKER = "F01.loop-shape", "F01.turn-limits", "F17.model-picker"
EFFORT, MODES, PLAN = "F18.effort-values", "F19.named-modes", "F19.plan-mode"


class GoodFixtureTests(ValidatorCase):
    def test_good_fixture_exits_zero_with_and_without_completeness(self):
        fx = self.fresh()
        self.assertClean(fx)
        self.assertClean(fx, "--require-complete")

    def test_summary_counts_cells_by_state_and_verification_per_surface(self):
        out = self.assertClean(self.fresh())
        lines = {ln.split()[2].rstrip(":"): ln for ln in out.splitlines() if " summary " in ln}
        self.assertEqual(set(lines), set(SURFACES))
        cc = lines[CC]
        for fragment in (
            "cells=7",
            "state:supported=3",
            "state:partial=1",
            "state:not-exposed=1",
            "state:not-applicable=1",
            "state:undocumented=1",
            "verification:verified=5",
            "verification:unverified=2",
        ):
            self.assertIn(fragment, cc)
        self.assertIn("cells=6", lines[GB])

    def test_json_output_is_parseable_and_counts_errors(self):
        fx = self.fresh()
        fx.cell(CC, LOOP, evidence=[])
        code, out = self.run_validator(fx, "--json")
        doc = json.loads(out)
        self.assertEqual(code, 1)
        self.assertEqual(doc["errors"], len([f for f in doc["findings"] if f["level"] == "error"]))
        self.assertIn("R03-state-obligation", {f["rule"] for f in doc["findings"]})
        self.assertEqual(doc["summary"][CC]["cells"], 7)

    def test_finding_lines_use_the_documented_shape(self):
        fx = self.fresh()
        fx.cell(CC, LOOP, evidence=[])
        _, out = self.run_validator(fx)
        for line in out.splitlines():
            self.assertRegex(line, r"^(error|warn|info) \S+ \S+: .+$")

    def test_u00_cells_are_accepted_and_not_counted_for_completeness(self):
        fx = self.fresh()
        self.assertClean(fx, "--require-complete")
        fx.add_cell(GB, make_cell(GB, "U00", "supported", "verified", evidence=[eid(GB, 1)]))
        self.assertClean(fx, "--require-complete")

    def test_real_facets_and_surfaces_load_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("facets.json", "surfaces.json"):
                (Path(tmp) / name).write_bytes((DATA_DIR / name).read_bytes())
            findings, _ = validate.validate(tmp)
            self.assertEqual([f for f in findings if f.level == "error"], [])
            rows = sum(len(f["rows"]) for f in REAL_FACETS["facets"])
            findings, _ = validate.validate(tmp, require_complete=True)
            text = "\n".join(f.line() for f in findings)
            self.assertIn(f"{rows} of {rows} frozen rows have no cell", text)
            self.assertEqual(text.count("frozen rows have no cell"), len(REAL_SURFACES["surfaces"]))

    def test_cli_runs_as_a_script_and_signals_with_its_exit_code(self):
        script = str(TOOLS / "validate.py")
        good = self.fresh()
        run = subprocess.run(
            [sys.executable, script, "--data-dir", str(good.root), "--no-repo-paths"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        bad = self.fresh()
        bad.cell(CC, LOOP, evidence=[])
        run = subprocess.run(
            [sys.executable, script, "--data-dir", str(bad.root), "--no-repo-paths"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertRegex(run.stdout, r"(?m)^error R03-state-obligation \S+: ")

    def test_selftest_prints_ok(self):
        run = subprocess.run(
            [sys.executable, str(TOOLS / "validate.py"), "--selftest"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual((run.returncode, run.stdout.strip()), (0, "OK"), run.stderr)

    def test_the_worktree_assertion_runs_before_anything_else(self):
        fx = self.fresh()
        env = {k: v for k, v in os.environ.items() if k != "ATLAS_TEST_ALLOW_ANY_TREE"}
        with tempfile.TemporaryDirectory() as elsewhere:
            run = subprocess.run(
                [sys.executable, str(TOOLS / "validate.py"), "--data-dir", str(fx.root)],
                capture_output=True,
                text=True,
                cwd=elsewhere,
                env=env,
                check=False,
            )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("atlas:", run.stderr)
        self.assertNotIn("summary", run.stdout)


class StructureTests(ValidatorCase):
    R = "R01-structure"

    def test_structure_violations_each_name_the_rule(self):
        table = [
            ("unknown key", lambda fx: fx.cell(CC, LOOP, extra=1), ()),
            ("missing required key", lambda fx: fx.cell(CC, LOOP, state=DROP), ()),
            ("unknown state", lambda fx: fx.cell(CC, LOOP, state="maybe"), ()),
            ("unknown verification", lambda fx: fx.cell(CC, LOOP, verification="sure"), ()),
            ("pattern", lambda fx: fx.evidence(CC, 4, retrieved="yesterday"), ()),
            ("evidence id pattern", lambda fx: fx.evidence(CC, 4, id="E-bad"), ()),
            ("maxLength", lambda fx: fx.cell(CC, LOOP, value="v" * 401), ()),
            (
                "minimum",
                lambda fx: fx.evidence(CC, 4, locator={"raw_line_start": 0, "raw_line_end": 1}),
                (),
            ),
            ("maxItems", lambda fx: fx.evidence(CC, 4, context_before=["a", "b", "c"]), ()),
            (
                "minItems",
                lambda fx: fx.cell(
                    CC,
                    MODES,
                    sweep_report={
                        "terms": [],
                        "corpus_sha256": "e" * 64,
                        "hits": 0,
                        "hits_reviewed": 0,
                        "positive_control_term": "m",
                        "positive_control_hits": 1,
                    },
                ),
                (),
            ),
            ("type", lambda fx: fx.evidence(CC, 4, bytes="big"), ()),
            ("bool is not an integer", lambda fx: fx.evidence(CC, 4, http_status=True), ()),
            ("lever enum", lambda fx: fx.lever(0, location_kind="teleport"), ()),
            ("register enum", lambda fx: fx.entry(0, value=4), ()),
            ("snapshot required key", lambda fx: fx.snapshot(freeze_end=DROP), ()),
            ("snapshot unknown key", lambda fx: fx.snapshot(surprise=1), ()),
            (
                "cell record is not an object",
                lambda fx: fx.edit(f"cells/{CC}.json", lambda d: d["cells"].append("nope")),
                (),
            ),
            (
                "cells file has no cells list",
                lambda fx: fx.write(f"cells/{GB}.json", {"surface": GB}),
                (),
            ),
            (
                "evidence list holds a non-string",
                lambda fx: fx.cell(CC, LOOP, evidence=[eid(CC, 1), 7]),
                (),
            ),
        ]
        self.cases(self.R, table)

    def test_unparseable_json_is_a_structure_error(self):
        fx = self.fresh()
        fx.path("levers.json").write_text("{not json", encoding="utf-8")
        self.assertRejected(fx, self.R, where="levers.json")

    def test_facets_and_surfaces_are_required_even_without_completeness(self):
        for name in ("facets.json", "surfaces.json"):
            with self.subTest(name):
                fx = self.fresh()
                fx.path(name).unlink()
                code, out = self.run_validator(fx)
                self.assertNotEqual(code, 0, out)
                self.assertIn(f"error {self.R} {name}: file is missing", out)

    def test_enums_come_from_the_schema_files_not_from_the_code(self):
        fx = self.fresh()
        self.assertEqual(
            [
                f
                for f in validate.validate(fx.root, check_repo_paths=False)[0]
                if f.level == "error"
            ],
            [],
        )
        with tempfile.TemporaryDirectory() as tmp:
            for path in SCHEMA_DIR.glob("*.json"):
                (Path(tmp) / path.name).write_bytes(path.read_bytes())
            cell_schema = json.loads((Path(tmp) / "cell.schema.json").read_text(encoding="utf-8"))
            cell_schema["properties"]["state"]["enum"].remove("partial")
            (Path(tmp) / "cell.schema.json").write_text(json.dumps(cell_schema), encoding="utf-8")
            findings, _ = validate.validate(fx.root, schema_dir=tmp, check_repo_paths=False)
        hits = [
            f for f in findings if f.rule == self.R and TURN in f.where and "partial" in f.message
        ]
        self.assertTrue(hits, [f.line() for f in findings])

    def test_schema_with_a_keyword_outside_the_subset_fails_closed(self):
        fx = self.fresh()
        with tempfile.TemporaryDirectory() as tmp:
            for path in SCHEMA_DIR.glob("*.json"):
                (Path(tmp) / path.name).write_bytes(path.read_bytes())
            lever_schema = json.loads((Path(tmp) / "lever.schema.json").read_text(encoding="utf-8"))
            lever_schema["oneOf"] = []
            (Path(tmp) / "lever.schema.json").write_text(json.dumps(lever_schema), encoding="utf-8")
            with self.assertRaises(validate.SchemaError):
                validate.validate(fx.root, schema_dir=tmp, check_repo_paths=False)

    def test_snapshot_may_carry_matrix_pending(self):
        fx = self.fresh()
        fx.snapshot(matrix_pending=True)
        self.assertClean(fx)
        fx.snapshot(matrix_pending="yes")
        self.assertRejected(fx, self.R)


class ReferentialTests(ValidatorCase):
    R = "R02-referential-integrity"

    def test_dangling_references_each_name_the_rule(self):
        unknown = eid(CC, 9)
        new_row = make_cell(CC, "F99.nonexistent", "supported", "verified", evidence=[eid(CC, 1)])
        table = [
            ("cell evidence id", lambda fx: fx.cell(CC, LOOP, evidence=[eid(CC, 1), unknown]), ()),
            (
                "vendor statement id",
                lambda fx: fx.cell(CC, PICKER, vendor_statement=unknown),
                (validate.R_STATE,),
            ),
            ("lever evidence id", lambda fx: fx.lever(0, evidence=[eid(CC, 1), unknown]), ()),
            ("row not in facets", lambda fx: fx.add_cell(CC, new_row), ()),
            ("lever row not in facets", lambda fx: fx.lever(0, row="F99.nonexistent"), ()),
            (
                "lever surface not in surfaces.json",
                lambda fx: fx.lever(0, surface="cursor"),
                (validate.R_LEVER,),
            ),
            ("task row surface", lambda fx: fx.task_row(0, surface="cursor"), ()),
            (
                "register cell id",
                lambda fx: fx.entry(0, cells=["claude-code/F01.nope"]),
                (validate.R_REGISTER,),
            ),
            (
                "duplicate evidence id",
                lambda fx: fx.edit(
                    f"evidence/{CC}.json",
                    lambda d: d["evidence"].append(copy.deepcopy(d["evidence"][0])),
                ),
                (),
            ),
            (
                "duplicate cell id",
                lambda fx: fx.edit(
                    f"cells/{CC}.json", lambda d: d["cells"].append(copy.deepcopy(d["cells"][0]))
                ),
                (),
            ),
            (
                "cell id disagrees with surface/row",
                lambda fx: fx.cell(CC, LOOP, id="claude-code/F01.x"),
                (),
            ),
            (
                "cell in another surface's file",
                lambda fx: fx.edit(
                    f"cells/{GB}.json",
                    lambda d: d["cells"][0].update(surface=CC, id=f"{CC}/{LOOP}"),
                ),
                (validate.R_STATE,),
            ),
            (
                "file name is not a surface",
                lambda fx: fx.write("cells/unknown.json", {"surface": "unknown", "cells": []}),
                (),
            ),
            (
                "file surface disagrees with its name",
                lambda fx: fx.edit(f"cells/{GB}.json", lambda d: d.update(surface=CC)),
                (),
            ),
        ]
        self.cases(self.R, table)

    def test_existing_references_pass(self):
        self.assertClean(self.fresh())


class StateObligationTests(ValidatorCase):
    R = "R03-state-obligation"

    def test_each_state_obligation_fails_when_unmet(self):
        e1, e3 = eid(CC, 1), eid(CC, 3)
        sweep = {
            "terms": ["mode"],
            "corpus_sha256": "e" * 64,
            "hits": 2,
            "hits_reviewed": 2,
            "positive_control_term": "model",
            "positive_control_hits": 5,
        }
        table = [
            ("uncited core cell", lambda fx: fx.cell(CC, LOOP, evidence=[]), ()),
            ("supported on tier S only", lambda fx: fx.evidence(CC, 1, tier="S"), ()),
            ("supported on tier U only", lambda fx: fx.evidence(CC, 1, tier="U"), ()),
            (
                "supported on unverified quote",
                lambda fx: fx.evidence(CC, 1, quote_verified=None),
                (),
            ),
            ("partial without limitation", lambda fx: fx.cell(CC, TURN, limitation=DROP), ()),
            ("partial with blank limitation", lambda fx: fx.cell(CC, TURN, limitation="  "), ()),
            ("partial without evidence", lambda fx: fx.cell(CC, TURN, evidence=[]), ()),
            (
                "not-exposed with neither statement nor reference page",
                lambda fx: fx.cell(CC, PICKER, vendor_statement=DROP, evidence=[e1]),
                (),
            ),
            (
                "not-exposed with reference page but no ordinary evidence",
                lambda fx: fx.cell(CC, PICKER, vendor_statement=DROP, reference_page_evidence=e1),
                (),
            ),
            (
                "not-exposed with an ordinary id but no reference page",
                lambda fx: fx.cell(CC, PICKER, vendor_statement=DROP, evidence=[e1, e3]),
                (),
            ),
            (
                "not-applicable without na_quote",
                lambda fx: fx.cell(CC, EFFORT, na_quote=DROP, evidence=[e1]),
                (),
            ),
            (
                "undocumented without a sweep report",
                lambda fx: fx.cell(CC, MODES, sweep_report=DROP),
                (),
            ),
            (
                "undocumented, hits not all reviewed",
                lambda fx: fx.cell(CC, MODES, sweep_report={**sweep, "hits_reviewed": 1}),
                (),
            ),
            (
                "undocumented, more reviewed than hits",
                lambda fx: fx.cell(CC, MODES, sweep_report={**sweep, "hits_reviewed": 3}),
                (),
            ),
            (
                "undocumented, positive control found nothing",
                lambda fx: fx.cell(CC, MODES, sweep_report={**sweep, "positive_control_hits": 0}),
                (validate.R_STRUCTURE,),
            ),
            (
                "not-researched on a core row",
                lambda fx: fx.cell(
                    CC,
                    LOOP,
                    state="not-researched",
                    verification="unverified",
                    evidence=[],
                    settles_by="probe: read the page",
                ),
                (),
            ),
            (
                "not-researched on the unmapped bucket",
                lambda fx: fx.add_cell(
                    GB,
                    make_cell(
                        GB, "U00", "not-researched", "unverified", settles_by="probe: read the page"
                    ),
                ),
                (),
            ),
            (
                "verified not-exposed on a tier S vendor statement",
                lambda fx: fx.evidence(CC, 2, tier="S"),
                (),
            ),
            (
                "verified not-applicable on a tier U quote",
                lambda fx: fx.evidence(CC, 3, tier="U"),
                (),
            ),
            (
                "verified not-exposed on a script-unverified quote",
                lambda fx: fx.evidence(CC, 2, quote_verified=None),
                (),
            ),
        ]
        self.cases(self.R, table)

    def test_tier_s_evidence_alone_never_makes_a_cell_verified(self):
        fx = self.fresh()
        fx.evidence(CC, 2, tier="S")
        self.assertRejected(fx, self.R, where=f"{CC}/{PICKER}")
        fx = self.fresh()
        fx.evidence(CC, 1, tier="S")
        out = self.assertRejected(fx, self.R)
        self.assertIn(f"{CC}/{LOOP}", out)
        self.assertIn(f"{CC}/{PLAN}", out)

    def test_obligations_that_are_met_pass(self):
        e1, e3 = eid(CC, 1), eid(CC, 3)
        optional = make_cell(
            CC, OPTIONAL_ROW, "not-researched", "unverified", settles_by="probe: read the page"
        )
        table = [
            (
                "not-exposed via reference page plus ordinary evidence",
                lambda fx: fx.cell(
                    CC, PICKER, vendor_statement=DROP, reference_page_evidence=e3, evidence=[e1]
                ),
            ),
            ("supported on tier E2", lambda fx: fx.evidence(CC, 1, tier="E2")),
            ("supported on tier E3", lambda fx: fx.evidence(CC, 1, tier="E3")),
            ("supported on tier E4", lambda fx: fx.evidence(CC, 1, tier="E4")),
            ("not-researched on an optional facet row", lambda fx: fx.add_cell(CC, optional)),
            (
                "supported with a second evidence id beside the verified one",
                lambda fx: fx.cell(CC, LOOP, evidence=[e1, eid(CC, 4)]),
            ),
        ]
        self.passes(table)

    def test_optional_row_can_be_not_researched_in_complete_mode(self):
        fx = self.fresh()
        fx.add_cell(
            CC,
            make_cell(CC, OPTIONAL_ROW, "not-researched", "unverified", settles_by="probe: read"),
        )
        self.assertClean(fx, "--require-complete")


class UndocumentedAndUnmappedTests(ValidatorCase):
    def test_a_swept_undocumented_cell_may_be_verified_without_evidence(self):
        # Its proof is the sweep report (positive control hit, every hit reviewed), not a quote.
        fx = self.fresh()
        fx.cell(CC, MODES, verification="verified")
        self.assertClean(fx)

    def test_a_verified_undocumented_cell_still_needs_a_valid_sweep(self):
        fx = self.fresh()
        fx.cell(CC, MODES, verification="verified", sweep_report=DROP)
        self.assertRejected(fx, validate.R_STATE)

    def test_numbered_unmapped_ids_are_accepted_and_malformed_ones_are_not(self):
        fx = self.fresh()
        good = make_cell(CC, "U00", "supported", "verified", evidence=[eid(CC, 5)])
        good["id"] = f"{CC}/U00/2"
        fx.add_cell(CC, good)
        self.assertClean(fx)
        bad_fx = self.fresh()
        bad = make_cell(CC, "U00", "supported", "verified", evidence=[eid(CC, 5)])
        bad["id"] = f"{CC}/U00/x"
        bad_fx.add_cell(CC, bad)
        self.assertRejected(bad_fx, validate.R_REFERENCE, where="U00")


class MarkerTests(ValidatorCase):
    R = "R04-marker"

    def test_unverified_cell_without_settles_by_fails(self):
        table = [
            ("settles_by absent", lambda fx: fx.cell(CC, PLAN, settles_by=DROP), ()),
            ("settles_by empty", lambda fx: fx.cell(CC, PLAN, settles_by=""), ()),
            ("settles_by blank", lambda fx: fx.cell(CC, MODES, settles_by="   "), ()),
        ]
        self.cases(self.R, table)

    def test_unverified_cell_with_settles_by_and_verified_cell_without_pass(self):
        out = self.assertClean(self.fresh())
        self.assertIn("verification:unverified=2", out)


class EvidenceQualityTests(ValidatorCase):
    R = "R05-evidence-quality"

    def test_evidence_quality_violations_each_name_the_rule(self):
        s = validate.R_STRUCTURE
        table = [
            ("quote over 300 characters", lambda fx: fx.evidence(CC, 4, quote="q" * 301), (s,)),
            ("sha256 absent", lambda fx: fx.evidence(CC, 4, sha256=DROP), (s,)),
            ("sha256 empty", lambda fx: fx.evidence(CC, 4, sha256=""), (s,)),
            ("context_before absent", lambda fx: fx.evidence(CC, 4, context_before=DROP), (s,)),
            ("context_after absent", lambda fx: fx.evidence(CC, 4, context_after=DROP), (s,)),
            (
                "url not https",
                lambda fx: fx.evidence(CC, 4, url="http://code.claude.com/docs/x"),
                (s,),
            ),
            (
                "url off the allow-list",
                lambda fx: fx.evidence(CC, 4, url="https://evil.example/x"),
                (),
            ),
            (
                "url_effective off the allow-list",
                lambda fx: fx.evidence(CC, 4, url_effective="https://evil.example/x"),
                (),
            ),
            (
                "url_effective not https",
                lambda fx: fx.evidence(CC, 4, url_effective="http://code.claude.com/x"),
                (s,),
            ),
            (
                "host suffix trick",
                lambda fx: fx.evidence(CC, 4, url="https://code.claude.com.evil.example/x"),
                (),
            ),
            (
                "host in the query only",
                lambda fx: fx.evidence(CC, 4, url="https://evil.example/?u=code.claude.com"),
                (),
            ),
            (
                "userinfo trick",
                lambda fx: fx.evidence(CC, 4, url="https://code.claude.com@evil.example/x"),
                (),
            ),
            (
                "backslash trick",
                lambda fx: fx.evidence(CC, 4, url="https://evil.example\\@code.claude.com/x"),
                (),
            ),
            (
                "another surface's host",
                lambda fx: fx.evidence(CC, 4, url="https://docs.x.ai/docs/x"),
                (),
            ),
            (
                "cursor.com is not a claude-code host",
                lambda fx: fx.evidence(CC, 4, url="https://cursor.com/docs/x"),
                (),
            ),
            (
                "E1 with quote_verified false",
                lambda fx: fx.evidence(CC, 4, quote_verified=False),
                (),
            ),
            (
                "E2 with quote_verified false",
                lambda fx: fx.evidence(CC, 4, tier="E2", quote_verified=False),
                (),
            ),
            (
                "E4 with quote_verified false",
                lambda fx: fx.evidence(CC, 4, tier="E4", quote_verified=False),
                (),
            ),
            (
                "described span with a quote",
                lambda fx: fx.evidence(
                    CC,
                    4,
                    described_span={
                        "description": INSTALL_DESCRIPTION,
                        "raw_line_start": 1,
                        "raw_line_end": 1,
                        "span_sha256": SPAN_SHA,
                    },
                ),
                (),
            ),
        ]
        self.cases(self.R, table)

    def test_quote_verified_false_on_a_cited_record_also_breaks_its_cells(self):
        fx = self.fresh()
        fx.evidence(CC, 1, quote_verified=False)
        out = self.assertRejected(fx, self.R, also=(validate.R_STATE,))
        self.assertIn(f"{CC}/{LOOP}", out)

    def test_quote_verified_null_and_non_primary_tiers_are_allowed(self):
        table = [
            ("E1 with quote_verified null", lambda fx: fx.evidence(CC, 4, quote_verified=None)),
            (
                "tier S with quote_verified false",
                lambda fx: fx.evidence(CC, 4, tier="S", quote_verified=False),
            ),
            (
                "tier U with quote_verified false",
                lambda fx: fx.evidence(CC, 4, tier="U", quote_verified=False),
            ),
            ("quote of exactly 300 characters", lambda fx: fx.evidence(CC, 4, quote="q" * 300)),
            (
                "url_effective on the allow-list",
                lambda fx: fx.evidence(
                    CC, 4, url_effective="https://code.claude.com/docs/en/final"
                ),
            ),
            (
                "grok-bot may cite cursor.com",
                lambda fx: fx.evidence(GB, 4, url="https://cursor.com/docs/x"),
            ),
            (
                "grok-bot may cite docs.x.ai",
                lambda fx: fx.evidence(GB, 4, url="https://docs.x.ai/docs/x"),
            ),
            (
                "host match ignores case",
                lambda fx: fx.evidence(CC, 4, url="https://CODE.Claude.com/docs/x"),
            ),
            (
                "described span with an empty quote",
                lambda fx: fx.evidence(
                    CC,
                    4,
                    quote="",
                    described_span={
                        "description": INSTALL_DESCRIPTION,
                        "raw_line_start": 1,
                        "raw_line_end": 1,
                        "span_sha256": SPAN_SHA,
                    },
                ),
            ),
        ]
        self.passes(table)

    def test_grok_bot_is_not_allowed_arbitrary_hosts(self):
        fx = self.fresh()
        fx.evidence(GB, 4, url="https://evil.example/x")
        self.assertRejected(fx, self.R, where=eid(GB, 4))


class InstallLineTests(ValidatorCase):
    R = "R06-install-line"

    def test_the_sample_really_is_an_install_line(self):
        self.assertTrue(install_text(install_line()))
        self.assertTrue(install_text("np" + "m install -g @example/tool"))
        self.assertFalse(install_text("The agent loop runs until the task is done."))

    def test_verbatim_install_lines_fail(self):
        samples = [install_line(), "np" + "m install -g @example/tool", "pi" + "p install example"]
        for sample in samples:
            with self.subTest(sample[:8]):
                fx = self.fresh()
                fx.evidence(CC, 4, quote=sample)
                self.assertRejected(fx, self.R, where=eid(CC, 4))

    def test_install_lines_stored_as_described_spans_pass(self):
        fx = self.fresh()
        span = {
            "description": INSTALL_DESCRIPTION,
            "raw_line_start": 3,
            "raw_line_end": 3,
            "span_sha256": SPAN_SHA,
        }
        fx.evidence(CC, 4, quote="", described_span=span)
        self.assertClean(fx)
        fx.evidence(CC, 4, quote="A prose sentence about installing the tool.", described_span=None)
        self.assertClean(fx)


class NumericConfidenceTests(ValidatorCase):
    R = "R07-numeric-confidence"

    def test_numeric_confidence_keys_fail_in_cells_levers_and_evidence(self):
        s = validate.R_STRUCTURE
        table = []
        for key in ("confidence", "probability", "certainty", "likelihood"):
            table.append((f"cell {key}", lambda fx, k=key: fx.cell(CC, LOOP, **{k: 0.9}), (s,)))
            table.append((f"lever {key}", lambda fx, k=key: fx.lever(0, **{k: 0.9}), (s,)))
            table.append(
                (f"evidence {key}", lambda fx, k=key: fx.evidence(CC, 4, **{k: 0.9}), (s,))
            )
        table += [
            ("upper-case key", lambda fx: fx.cell(CC, LOOP, Confidence=0.9), (s,)),
            (
                "nested key",
                lambda fx: fx.evidence(
                    CC, 4, locator={"raw_line_start": 1, "raw_line_end": 1, "confidence": 1}
                ),
                (s,),
            ),
            (
                "nested in a list",
                lambda fx: fx.lever(
                    0,
                    values_by_model={"m": ["a"]},
                    evidence=[eid(CC, 1)],
                    **{"values": ["x"], "confidence": 1},
                ),
                (s,),
            ),
        ]
        self.cases(self.R, table)

    def test_register_entries_may_carry_a_score(self):
        fx = self.fresh()
        fx.entry(0, score=3.25)
        self.assertClean(fx)

    def test_the_rule_does_not_reach_register_entries(self):
        fx = self.fresh()
        fx.entry(0, confidence=0.5)
        self.assertRejected(fx, validate.R_STRUCTURE)


class LeverTests(ValidatorCase):
    R = "R08-lever"

    def test_lever_violations_each_name_the_rule(self):
        table = [
            ("verified lever with no evidence", lambda fx: fx.lever(0, evidence=[]), ()),
            (
                "verified lever on tier S evidence",
                lambda fx: fx.evidence(CC, 6, tier="S"),
                (),
            ),
            (
                "lever value on tier S evidence only",
                lambda fx: (
                    fx.evidence(CC, 4, tier="S"),
                    fx.lever(0, values=["low", "high"], evidence=[eid(CC, 4)]),
                ),
                (),
            ),
            (
                "lever value with no evidence at all",
                lambda fx: fx.lever(0, values=["low", "high"], evidence=[]),
                (),
            ),
            (
                "vendor_managed without a positive quote",
                lambda fx: fx.lever(1, verification="unverified", evidence=[]),
                (),
            ),
            (
                "not_applicable without a positive quote",
                lambda fx: fx.lever(
                    1,
                    location_kind="not_applicable",
                    state="not-applicable",
                    verification="unverified",
                    evidence=[],
                ),
                (),
            ),
            (
                "vendor_managed on an unverified quote",
                lambda fx: fx.evidence(GB, 6, quote_verified=None),
                (),
            ),
            (
                "model_conditional without values_by_model",
                lambda fx: fx.lever(0, model_conditional=True),
                (),
            ),
            (
                "model_conditional with empty values_by_model",
                lambda fx: fx.lever(0, model_conditional=True, values_by_model={}),
                (),
            ),
            (
                "unread_models on a verified record",
                lambda fx: fx.lever(0, unread_models=["m-1"]),
                (),
            ),
        ]
        self.cases(self.R, table)

    def test_lever_records_that_meet_the_rules_pass(self):
        table = [
            (
                "model_conditional with values_by_model",
                lambda fx: fx.lever(
                    0, model_conditional=True, values_by_model={"m-1": ["low", "high"]}
                ),
            ),
            (
                "unread_models on an unverified record",
                lambda fx: fx.lever(0, unread_models=["m-1"], verification="unverified"),
            ),
            (
                "unverified lever with no evidence",
                lambda fx: fx.lever(0, verification="unverified", evidence=[]),
            ),
            (
                "undocumented location needs no quote",
                lambda fx: fx.lever(
                    0,
                    location_kind="undocumented",
                    state="undocumented",
                    verification="unverified",
                    evidence=[],
                ),
            ),
        ]
        self.passes(table)


class TaskShapeTests(ValidatorCase):
    R = "R09-task-shape"

    def test_task_shape_violations_each_name_the_rule(self):
        pointer = {"file": "agent-routing-matrix.json", "path": "$.rules[0]"}
        table = [
            (
                "neither pointer nor pending label",
                lambda fx: fx.task_row(0, pointer=None, pending_label=None),
                (),
            ),
            (
                "neither, with a blank label",
                lambda fx: fx.task_row(0, pointer=None, pending_label="  "),
                (),
            ),
            (
                "pending label while the matrix is not pending",
                lambda fx: fx.task_row(0, pointer=None, pending_label="pending the matrix"),
                (),
            ),
            (
                "pending label with matrix_pending false",
                lambda fx: (
                    fx.snapshot(matrix_pending=False),
                    fx.task_row(0, pointer=None, pending_label="pending the matrix"),
                )[1],
                (),
            ),
            ("pointer without snapshot matrix_sha", lambda fx: fx.snapshot(matrix_sha=DROP), ()),
            ("basis outside the enum", lambda fx: fx.task_row(0, basis="gut-feel"), ()),
            ("basis absent", lambda fx: fx.task_row(0, basis=DROP), ()),
            ("task_class absent", lambda fx: fx.task_row(0, task_class=DROP), ()),
            ("pointer without a path", lambda fx: fx.task_row(0, pointer={"file": "m.json"}), ()),
            (
                "pointer with an empty file",
                lambda fx: fx.task_row(0, pointer={**pointer, "file": ""}),
                (),
            ),
            ("pointer of the wrong type", lambda fx: fx.task_row(0, pointer="m.json"), ()),
            ("lever_settings not a list", lambda fx: fx.task_row(0, lever_settings={}), ()),
        ]
        self.cases(self.R, table)

    def test_task_shape_rows_that_meet_the_rules_pass(self):
        def pending(fx):
            fx.snapshot(matrix_pending=True, matrix_sha=DROP)
            fx.task_row(0, pointer=None, pending_label="pending the matrix")

        table = [("pending label while matrix_pending is true", pending)]
        for basis in validate.TASK_BASES:
            table.append((f"basis {basis}", lambda fx, b=basis: fx.task_row(0, basis=b)))
        self.passes(table)


class RegisterTests(ValidatorCase):
    R = "R10-register"

    def test_register_violations_each_name_the_rule(self):
        verified = "claude-code/U00"
        unverified = "claude-code/F19.plan-mode"
        table = [
            ("non-probe on an unverified cell", lambda fx: fx.entry(1, type="improve"), ()),
            (
                "non-probe on a missing cell",
                lambda fx: fx.entry(
                    0, type="improve", cells=["claude-code/F01.nope"], repo_files=DROP
                ),
                (validate.R_REFERENCE,),
            ),
            (
                "mixed cells, one unverified",
                lambda fx: fx.entry(
                    0, type="improve", cells=[verified, unverified], repo_files=DROP
                ),
                (),
            ),
            ("correct without repo_claim", lambda fx: fx.entry(2, repo_claim=DROP), ()),
            (
                "reconcile without repo_claim",
                lambda fx: fx.entry(2, type="reconcile", repo_claim=DROP),
                (),
            ),
            ("proposal over 120 words", lambda fx: fx.entry(0, proposal=" ".join(["w"] * 121)), ()),
            ("duplicate rank", lambda fx: fx.entry(1, rank=1), ()),
            (
                "status not proposed",
                lambda fx: fx.entry(0, status="adopted"),
                (validate.R_STRUCTURE,),
            ),
            ("missing file on an improve entry", lambda fx: fx.entry(0, type="improve"), ()),
            (
                "missing file on a correct entry",
                lambda fx: fx.entry(2, repo_files=[{"path": "gone.md", "exists": False}]),
                (),
            ),
            (
                "missing file on a probe entry",
                lambda fx: fx.entry(1, repo_files=[{"path": "gone.md", "exists": False}]),
                (),
            ),
        ]
        self.cases(self.R, table)

    def test_register_entries_that_meet_the_rules_pass(self):
        claim = {"blob_sha": "d" * 40, "path": "README.md", "line": 3, "quote": "a repo statement"}
        table = [
            (
                "proposal of exactly 120 words",
                lambda fx: fx.entry(0, proposal=" ".join(["w"] * 120)),
            ),
            ("new-lane may name a new file", lambda fx: fx.entry(0, type="new-lane")),
            ("extend may name a new file", lambda fx: fx.entry(0, type="extend")),
            (
                "existing files on any type",
                lambda fx: fx.entry(2, repo_files=[{"path": "README.md", "exists": True}]),
            ),
            (
                "reconcile with repo_claim",
                lambda fx: fx.entry(2, type="reconcile", repo_claim=claim),
            ),
            (
                "a probe may cite verified cells",
                lambda fx: fx.entry(1, cells=["claude-code/U00"]),
            ),
            (
                "an entry that cites no cell",
                lambda fx: fx.entry(0, type="improve", cells=[], repo_files=DROP),
            ),
            (
                "entries without a rank",
                lambda fx: (fx.entry(0, rank=DROP), fx.entry(1, rank=DROP))[1],
            ),
        ]
        self.passes(table)

    def test_the_duplicate_rank_finding_names_the_rank(self):
        fx = self.fresh()
        fx.entry(1, rank=1)
        _, out = self.run_validator(fx)
        self.assertIn("rank 1 is not unique", out)


class CompletenessTests(ValidatorCase):
    R = "R11-completeness"

    def test_a_missing_cell_is_reported_per_surface_only_when_complete_is_required(self):
        fx = self.fresh()
        fx.edit(f"cells/{GB}.json", lambda d: d["cells"].pop(0))
        self.assertClean(fx)
        out = self.assertRejected(fx, self.R, "--require-complete", where=f"cells/{GB}.json")
        self.assertIn("1 of 6 frozen rows have no cell", out)
        self.assertIn(LOOP, out)
        self.assertNotIn(f"cells/{CC}.json: 1 of", out)
        self.assertRegex(out, rf"info summary {GB}: .*missing=1")
        self.assertRegex(out, rf"info summary {CC}: .*missing=0")

    def test_missing_counts_are_per_surface(self):
        fx = self.fresh()
        fx.edit(f"cells/{CC}.json", lambda d: d.update(cells=d["cells"][2:]))
        fx.edit(f"cells/{GB}.json", lambda d: d.update(cells=d["cells"][1:]))
        out = self.assertRejected(fx, self.R, "--require-complete")
        self.assertRegex(out, rf"cells/{CC}.json: 2 of 6 frozen rows")
        self.assertRegex(out, rf"cells/{GB}.json: 1 of 6 frozen rows")

    def test_a_row_with_two_cells_is_not_complete(self):
        fx = self.fresh()
        fx.edit(f"cells/{GB}.json", lambda d: d["cells"].append(copy.deepcopy(d["cells"][0])))
        self.assertRejected(
            fx, self.R, "--require-complete", also=(validate.R_REFERENCE,), where="more than one"
        )

    def test_missing_files_render_as_missing_findings_only_when_complete_is_required(self):
        for rel in (
            "levers.json",
            "register.json",
            "snapshot.json",
            f"cells/{GB}.json",
            f"evidence/{CC}.json",
        ):
            with self.subTest(rel):
                fx = self.fresh()
                fx.path(rel).unlink()
                code, out = self.run_validator(fx)
                missing = [ln for ln in self.error_lines(out) if "file is missing" in ln]
                self.assertEqual(missing, [], out)
                code, out = self.run_validator(fx, "--require-complete")
                self.assertNotEqual(code, 0, out)
                self.assertIn(f"error {self.R} {rel}: file is missing", out)

    def test_not_researched_on_a_core_row_fails_completeness_too(self):
        fx = self.fresh()
        fx.cell(
            GB,
            LOOP,
            state="not-researched",
            verification="unverified",
            evidence=[],
            settles_by="probe: read the page",
        )
        out = self.assertRejected(
            fx, self.R, "--require-complete", also=(validate.R_STATE,), where=f"{GB}/{LOOP}"
        )
        self.assertIn("optional facet rows", out)


class SizeTests(ValidatorCase):
    R = "R12-size"

    def test_data_file_over_two_megabytes_fails(self):
        fx = self.fresh()
        fx.snapshot(params={"pad": "x" * 2_000_001})
        self.assertRejected(fx, self.R, where="snapshot.json")

    def test_data_file_under_the_limit_passes(self):
        fx = self.fresh()
        fx.snapshot(params={"pad": "x" * 1_900_000})
        self.assertClean(fx)

    def test_html_page_over_the_budget_fails(self):
        fx = self.fresh()
        fx.html("big.html", "x" * 1_500_001)
        fx.html("ok.html", "<p>fine</p>")
        out = self.assertRejected(fx, self.R, *fx.html_flags, where="big.html")
        self.assertNotIn("ok.html", out)

    def test_html_page_exactly_at_the_budget_passes(self):
        fx = self.fresh()
        fx.html("edge.html", "x" * 1_500_000)
        self.assertClean(fx, *fx.html_flags)

    def test_html_total_over_twelve_megabytes_fails_though_each_page_is_small(self):
        fx = self.fresh()
        for number in range(9):
            fx.html(f"p{number}.html", "x" * 1_400_000)
        out = self.assertRejected(fx, self.R, *fx.html_flags, where=str(fx.root / "html"))
        self.assertIn("bytes of HTML exceeds", out)

    def test_html_total_under_the_budget_passes(self):
        fx = self.fresh()
        for number in range(8):
            fx.html(f"p{number}.html", "x" * 1_400_000)
        self.assertClean(fx, *fx.html_flags)

    def test_sizes_are_not_checked_without_an_html_dir(self):
        fx = self.fresh()
        fx.html("big.html", "x" * 1_500_001)
        self.assertClean(fx)


class HtmlTests(ValidatorCase):
    R = "R13-html"

    def test_good_links_pass(self):
        fx = self.fresh()
        fx.html(
            "index.html",
            '<html><body><a href="other.html">x</a><a href="../up/page.html?q=1#f">u</a>'
            '<a href="#top">t</a><A HREF="b.html">B</A><img src="img/a.png">'
            '<a href="https://docs.x.ai/a">d</a><a href="https://cursor.com/docs/a">c</a>'
            '<a href="https://code.claude.com/docs/en/x">cc</a>'
            '<a href="https://github.com/org/repo">g</a><a href="">same page</a></body></html>',
        )
        self.assertClean(fx, *fx.html_flags)

    def test_bad_links_and_unescaped_markup_each_name_the_rule(self):
        script = "<scr" + "ipt>alert(1)</scr" + "ipt>"
        pages = {
            "http link": '<a href="http://docs.x.ai/a">x</a>',
            "off-list https host": '<a href="https://evil.example/a">x</a>',
            "protocol-relative": '<a href="//evil.example/a">x</a>',
            "backslash protocol-relative": '<a href="\\\\evil.example/a">x</a>',
            "javascript scheme": '<a href="javascript:void(0)">x</a>',
            "javascript with embedded tab": '<a href="java&#9;script:void(0)">x</a>',
            "javascript via character reference": '<a href="&#106;avascript:void(0)">x</a>',
            "data scheme": '<img src="data:text/html;base64,AAAA">',
            "mailto": '<a href="mailto:a@b.example">x</a>',
            "src off-list": '<img src="https://evil.example/a.png">',
            "script src off-list": '<script src="https://evil.example/a.js"></script>',
            "userinfo trick": '<a href="https://docs.x.ai@evil.example/a">x</a>',
            "suffix trick": '<a href="https://docs.x.ai.evil.example/a">x</a>',
            "scheme in upper case, host off-list": '<a href="HTTPS://evil.example/a">x</a>',
            "unescaped script literal": f"<p>{script}</p>",
            "unescaped script literal in other case": "<p><SCRIPT>ALERT(1)</SCRIPT></p>",
        }
        for name, body in pages.items():
            with self.subTest(name):
                fx = self.fresh()
                fx.html("page.html", f"<html><body>{body}</body></html>")
                self.assertRejected(fx, self.R, *fx.html_flags, where="page.html")

    def test_escaped_data_passes(self):
        fx = self.fresh()
        fx.html(
            "page.html", "<p>&lt;script&gt;alert(1)&lt;/script&gt; and <code>a &amp; b</code></p>"
        )
        self.assertClean(fx, *fx.html_flags)

    def test_a_bad_page_in_a_subdirectory_is_found_and_named(self):
        fx = self.fresh()
        fx.html("sub/dir/page.html", '<a href="http://evil.example/">x</a>')
        self.assertRejected(fx, self.R, *fx.html_flags, where="sub/dir/page.html")

    def test_html_is_not_scanned_without_an_html_dir(self):
        fx = self.fresh()
        fx.html("page.html", '<a href="http://evil.example/">x</a>')
        self.assertClean(fx)

    def test_missing_html_dir_is_an_error(self):
        fx = self.fresh()
        self.assertRejected(fx, self.R, "--html-dir", str(fx.root / "no-such-dir"))

    def test_allow_list_is_the_union_of_every_surfaces_docs_hosts_plus_github(self):
        fx = self.fresh()
        union = {h for s in make_surfaces()["surfaces"] for h in s["docs_hosts"]}
        self.assertEqual(union, {"code.claude.com", "docs.x.ai", "cursor.com"})
        fx.html("page.html", '<a href="https://developers.openai.com/codex">x</a>')
        self.assertRejected(fx, self.R, *fx.html_flags)


class CrossSurfaceTests(ValidatorCase):
    """Finding 1: a cell, a lever or a register entry only counts evidence of its own surface."""

    R = "R02-referential-integrity"

    def test_evidence_of_another_surface_is_rejected_and_never_counts(self):
        r03, r08 = validate.R_STATE, validate.R_LEVER
        table = [
            (
                "cell evidence cites another surface",
                lambda fx: fx.cell(GB, LOOP, evidence=[eid(CC, 1)]),
                (r03,),
            ),
            (
                "vendor_statement cites another surface",
                lambda fx: fx.cell(GB, PICKER, vendor_statement=eid(CC, 2)),
                (r03,),
            ),
            (
                "na_quote cites another surface",
                lambda fx: fx.cell(GB, EFFORT, na_quote=eid(CC, 3)),
                (r03,),
            ),
            (
                "reference_page_evidence cites another surface",
                lambda fx: fx.cell(
                    GB,
                    PICKER,
                    vendor_statement=DROP,
                    reference_page_evidence=eid(CC, 3),
                    evidence=[eid(GB, 1)],
                ),
                (r03,),
            ),
            (
                "lever evidence cites another surface",
                lambda fx: fx.lever(1, evidence=[eid(CC, 6)]),
                (r08,),
            ),
            (
                "an unverified cell may not borrow either",
                lambda fx: fx.cell(GB, PLAN, evidence=[eid(CC, 1)]),
                (r03,),
            ),
        ]
        self.cases(self.R, table)

    def test_a_cross_surface_id_beside_an_own_surface_record_is_still_an_error(self):
        fx = self.fresh()
        fx.cell(GB, LOOP, evidence=[eid(GB, 1), eid(CC, 1)])
        out = self.assertRejected(fx, self.R, where=f"{GB}/{LOOP}")
        self.assertIn(eid(CC, 1), out)

    def test_the_finding_names_the_two_surfaces(self):
        fx = self.fresh()
        fx.cell(GB, LOOP, evidence=[eid(CC, 1)])
        _, out = self.run_validator(fx)
        hit = [ln for ln in self.error_lines(out) if "R02" in ln and eid(CC, 1) in ln]
        self.assertTrue(hit, out)
        self.assertIn(GB, hit[0])
        self.assertIn(CC, hit[0])

    def test_a_register_entry_does_not_treat_a_cross_surface_cell_as_verified(self):
        fx = self.fresh()
        fx.cell(GB, LOOP, evidence=[eid(CC, 1)])
        fx.entry(0, type="improve", cells=[f"{GB}/{LOOP}"], repo_files=DROP)
        code, out = self.run_validator(fx)
        self.assertNotEqual(code, 0, out)
        self.assertIn(validate.R_REGISTER, self.error_rules(out), out)
        self.assertIn(self.R, self.error_rules(out), out)

    def test_own_surface_references_pass(self):
        self.assertClean(self.fresh())


class RoleEvidenceQualityTests(ValidatorCase):
    """Finding 2: the record named by a role must itself be E1-E4 and not quote_verified false."""

    R = "R03-state-obligation"

    @staticmethod
    def unverify(fx, surface, row, **extra):
        fx.cell(surface, row, verification="unverified", settles_by="probe: read it", **extra)

    def test_role_records_of_the_wrong_quality_fail_for_both_verifications(self):
        s = validate.R_EVIDENCE
        e1 = eid(CC, 1)

        def unverified_vendor(tier, flag):
            def mutate(fx):
                self.unverify(fx, CC, PICKER)
                fx.evidence(CC, 2, tier=tier, quote_verified=flag)

            return mutate

        def unverified_na(tier, flag):
            def mutate(fx):
                self.unverify(fx, CC, EFFORT)
                fx.evidence(CC, 3, tier=tier, quote_verified=flag)

            return mutate

        def reference_path(tier_ref, tier_ordinary, verified):
            def mutate(fx):
                fx.cell(
                    CC,
                    PICKER,
                    vendor_statement=DROP,
                    reference_page_evidence=eid(CC, 3),
                    evidence=[e1],
                )
                if not verified:
                    self.unverify(fx, CC, PICKER)
                fx.evidence(CC, 3, tier=tier_ref)
                fx.evidence(CC, 1, tier=tier_ordinary)

            return mutate

        table = [
            ("unverified not-exposed, vendor tier U, null", unverified_vendor("U", None), ()),
            ("unverified not-exposed, vendor tier S, null", unverified_vendor("S", None), ()),
            ("unverified not-exposed, vendor tier R", unverified_vendor("R", None), ()),
            ("unverified not-exposed, vendor E1 but false", unverified_vendor("E1", False), (s,)),
            ("unverified not-applicable, tier S, null", unverified_na("S", None), ()),
            ("unverified not-applicable, tier U, null", unverified_na("U", None), ()),
            ("unverified not-applicable, E1 but false", unverified_na("E1", False), (s,)),
            (
                "verified not-applicable on E1 with null",
                lambda fx: fx.evidence(CC, 3, quote_verified=None),
                (),
            ),
            (
                "verified not-exposed, reference page tier U, ordinary E1",
                reference_path("U", "E1", True),
                (),
            ),
            (
                "verified not-exposed, reference page E1, ordinary tier U",
                reference_path("E1", "U", True),
                (),
            ),
            (
                "unverified not-exposed, reference page tier S",
                reference_path("S", "E1", False),
                (),
            ),
            (
                "unverified not-exposed, ordinary record tier S",
                reference_path("E1", "S", False),
                (),
            ),
        ]
        self.cases(self.R, table)

    def test_a_reference_page_of_tier_u_is_not_rescued_by_an_unrelated_record(self):
        fx = self.fresh()
        fx.cell(
            CC,
            PICKER,
            vendor_statement=DROP,
            reference_page_evidence=eid(CC, 3),
            evidence=[eid(CC, 1)],
        )
        fx.evidence(CC, 3, tier="U")
        self.assertRejected(fx, self.R, where=f"{CC}/{PICKER}")

    def test_role_records_that_meet_the_rule_pass(self):
        def unverified(fx):
            self.unverify(fx, CC, PICKER)
            fx.evidence(CC, 2, quote_verified=None)

        def unverified_na(fx):
            self.unverify(fx, CC, EFFORT)
            fx.evidence(CC, 3, tier="E2", quote_verified=None)

        def reference(fx):
            fx.cell(
                CC,
                PICKER,
                vendor_statement=DROP,
                reference_page_evidence=eid(CC, 3),
                evidence=[eid(CC, 1)],
            )

        table = [
            ("unverified not-exposed on E1 with null", unverified),
            ("unverified not-applicable on E2 with null", unverified_na),
            ("verified not-exposed through a reference page", reference),
            ("verified roles on every tier E1-E4", lambda fx: fx.evidence(CC, 2, tier="E4")),
        ]
        self.passes(table)


class TaskRowStrictnessTests(ValidatorCase):
    """Finding 3: task rows, their pointers and the file wrappers have a key allow-list."""

    def test_numeric_keys_and_unknown_keys_on_task_rows_are_rejected(self):
        r07, r09 = validate.R_NUMERIC, validate.R_TASK
        pointer = {"file": "agent-routing-matrix.json", "path": "$.rules[0]"}
        self.cases(
            r07,
            [
                ("confidence on a row", lambda fx: fx.task_row(0, confidence=0.8), (r09,)),
                ("probability on a row", lambda fx: fx.task_row(0, probability=0.1), (r09,)),
                (
                    "numeric key inside the pointer",
                    lambda fx: fx.task_row(0, pointer={**pointer, "certainty": 1}),
                    (r09,),
                ),
                (
                    "upper-case key on a row",
                    lambda fx: fx.task_row(0, Likelihood=3),
                    (r09,),
                ),
            ],
        )
        self.cases(
            r09,
            [
                ("unknown key on a row", lambda fx: fx.task_row(0, zzz=1), ()),
                (
                    "unknown key on a pointer",
                    lambda fx: fx.task_row(0, pointer={**pointer, "zzz": 1}),
                    (),
                ),
            ],
        )

    def test_unknown_keys_on_the_file_wrappers_are_rejected(self):
        r01 = validate.R_STRUCTURE
        table = [
            (
                "cells wrapper",
                lambda fx: fx.edit(f"cells/{CC}.json", lambda d: d.update(zzz=1)),
                (),
            ),
            (
                "evidence wrapper",
                lambda fx: fx.edit(f"evidence/{GB}.json", lambda d: d.update(zzz=1)),
                (),
            ),
            ("levers wrapper", lambda fx: fx.edit("levers.json", lambda d: d.update(zzz=1)), ()),
        ]
        self.cases(r01, table)

    def test_every_documented_key_is_accepted(self):
        def all_keys(fx):
            fx.task_row(
                0, pending_label=None, lever_settings=[f"{CC}|model|"], basis="capability-fact"
            )

        self.passes([("all six row keys and both pointer keys", all_keys)])


class ReferenceResolutionTests(ValidatorCase):
    """Findings 5 and 10: register, snapshot, task-row pointers and lever settings resolve."""

    R = "R02-referential-integrity"

    def test_unresolved_register_and_snapshot_references_are_rejected(self):
        def bad_column(fx):
            fx.snapshot(
                columns=[
                    {
                        "surface": "bogus",
                        "retrieved": "2026-10-04",
                        "version": None,
                        "version_source": None,
                    }
                ]
            )

        table = [
            ("register surface", lambda fx: fx.entry(0, surfaces=["bogus"]), ()),
            ("register surface among good ones", lambda fx: fx.entry(0, surfaces=[CC, "x"]), ()),
            ("register row", lambda fx: fx.entry(0, rows=["F99.nope"]), ()),
            (
                "register ceiling cell",
                lambda fx: fx.entry(0, ceiling={"cell": "nope", "quote": "q"}),
                (),
            ),
            ("snapshot column surface", bad_column, ()),
        ]
        self.cases(self.R, table)

    def test_resolved_register_and_snapshot_references_pass(self):
        table = [
            ("register rows", lambda fx: fx.entry(0, rows=[LOOP, PICKER])),
            ("register unmapped row", lambda fx: fx.entry(0, rows=["U00"])),
            (
                "register ceiling cell",
                lambda fx: fx.entry(0, ceiling={"cell": f"{CC}/{LOOP}", "quote": "q"}),
            ),
            ("register surfaces", lambda fx: fx.entry(0, surfaces=[CC, GB])),
        ]
        self.passes(table)

    def test_lever_settings_must_name_a_lever_record(self):
        table = [
            ("no such lever", lambda fx: fx.task_row(0, lever_settings=["nope|nope|"]), ()),
            (
                "right lever, other model",
                lambda fx: fx.task_row(0, lever_settings=[f"{CC}|model|o"]),
                (),
            ),
            (
                "a good one beside a bad one",
                lambda fx: fx.task_row(0, lever_settings=[f"{CC}|model|", "x|y|"]),
                (),
            ),
        ]
        self.cases(self.R, table)

    def test_lever_settings_must_be_strings_of_the_form(self):
        r09 = validate.R_TASK
        table = [
            ("not a string", lambda fx: fx.task_row(0, lever_settings=[1]), ()),
            ("two parts only", lambda fx: fx.task_row(0, lever_settings=[f"{CC}|model"]), ()),
            ("four parts", lambda fx: fx.task_row(0, lever_settings=[f"{CC}|model||x"]), ()),
            ("null entry", lambda fx: fx.task_row(0, lever_settings=[None]), ()),
        ]
        self.cases(r09, table)

    def test_lever_settings_normalise_the_null_model_as_the_renderer_does(self):
        def conditional(fx):
            fx.lever(0, model="opus")
            fx.task_row(0, lever_settings=[f"{CC}|model|opus"])

        table = [
            ("empty model", lambda fx: fx.task_row(0, lever_settings=[f"{CC}|model|"])),
            ("null spelled out", lambda fx: fx.task_row(0, lever_settings=[f"{CC}|model|null"])),
            ("all", lambda fx: fx.task_row(0, lever_settings=[f"{CC}|model|ALL"])),
            ("star", lambda fx: fx.task_row(0, lever_settings=[f"{CC}|model|*"])),
            ("a named model", conditional),
        ]
        self.passes(table)

    def test_a_lever_setting_that_matches_only_another_models_record_fails(self):
        fx = self.fresh()
        fx.lever(0, model="opus")
        fx.task_row(0, lever_settings=[f"{CC}|model|"])
        self.assertRejected(fx, self.R, where="task_shape_rows[0]")

    def test_the_comparison_uses_the_renderer_key(self):
        self.assertEqual(render.ref_key(f"{CC}|model|NULL"), render.lever_key(CC, "model", None))


class PointerFileTests(ValidatorCase):
    """Finding 10: a task-row pointer file is a repo-relative path that must exist."""

    R = "R02-referential-integrity"

    def repo_fixture(self, with_matrix=True, dot_git=True):
        self._count += 1
        repo = Path(self._tmp.name) / f"repo{self._count}"
        if dot_git:
            (repo / ".git").mkdir(parents=True)
        fx = Fixture(repo / "data")
        if with_matrix:
            (repo / "agent-routing-matrix.json").write_text("{}", encoding="utf-8")
        return fx

    def test_an_existing_repo_relative_file_passes(self):
        fx = self.repo_fixture()
        code, out = self.run_validator(fx, repo_paths=True)
        self.assertEqual(self.error_lines(out), [], out)
        self.assertEqual(code, 0, out)

    def test_a_missing_file_is_an_error_unless_repo_paths_are_skipped(self):
        fx = self.repo_fixture(with_matrix=False)
        code, out = self.run_validator(fx, repo_paths=True)
        self.assertNotEqual(code, 0, out)
        self.assertEqual(self.error_rules(out), {self.R}, out)
        self.assertIn("agent-routing-matrix.json", out)
        self.assertClean(fx)

    def test_the_file_path_is_resolved_against_the_repository_root_not_the_data_dir(self):
        fx = self.repo_fixture(with_matrix=False)
        (fx.root / "agent-routing-matrix.json").write_text("{}", encoding="utf-8")
        code, out = self.run_validator(fx, repo_paths=True)
        self.assertNotEqual(code, 0, out)

    def test_paths_that_leave_the_repository_are_rejected(self):
        for name in ("../outside.json", "/etc/hostname", "a/../../outside.json"):
            with self.subTest(name):
                fx = self.repo_fixture()
                fx.task_row(0, pointer={"file": name, "path": "$.x"})
                code, out = self.run_validator(fx, repo_paths=True)
                self.assertNotEqual(code, 0, out)
                self.assertIn(self.R, self.error_rules(out), out)

    def test_a_directory_is_not_a_file(self):
        fx = self.repo_fixture()
        (fx.root.parent / "docs").mkdir()
        fx.task_row(0, pointer={"file": "docs", "path": "$.x"})
        code, out = self.run_validator(fx, repo_paths=True)
        self.assertNotEqual(code, 0, out)

    def test_no_repository_root_is_an_error_not_a_pass(self):
        fx = self.repo_fixture(dot_git=False)
        code, out = self.run_validator(fx, repo_paths=True)
        self.assertNotEqual(code, 0, out)
        self.assertIn("--no-repo-paths", out)

    def test_pending_rows_have_no_file_to_resolve(self):
        fx = self.repo_fixture(with_matrix=False)
        fx.snapshot(matrix_pending=True, matrix_sha=DROP)
        fx.task_row(0, pointer=None, pending_label="pending the matrix")
        code, out = self.run_validator(fx, repo_paths=True)
        self.assertEqual(self.error_lines(out), [], out)

    def test_the_flag_is_part_of_the_cli(self):
        script = str(TOOLS / "validate.py")
        fx = self.repo_fixture(with_matrix=False)
        env = dict(os.environ, ATLAS_TEST_ALLOW_ANY_TREE="1")
        for flags, expect in (([], 1), (["--no-repo-paths"], 0)):
            run = subprocess.run(
                [sys.executable, script, "--data-dir", str(fx.root), *flags],
                capture_output=True,
                text=True,
                env=env,
                check=False,
            )
            self.assertEqual(run.returncode, expect, run.stdout + run.stderr)


class EmptyQuoteTests(ValidatorCase):
    """Finding 6: a record with neither a quote nor a described span proves nothing."""

    R = "R05-evidence-quality"

    def test_empty_quote_without_a_described_span_is_rejected(self):
        table = [
            ("empty quote", lambda fx: fx.evidence(CC, 4, quote=""), ()),
            ("blank quote", lambda fx: fx.evidence(CC, 4, quote="  \n "), ()),
            (
                "empty quote and a null span",
                lambda fx: fx.evidence(CC, 4, quote="", described_span=None),
                (),
            ),
        ]
        self.cases(self.R, table)

    def test_a_verified_cell_resting_on_an_empty_quote_is_not_verified(self):
        fx = self.fresh()
        fx.evidence(CC, 1, quote="")
        code, out = self.run_validator(fx)
        self.assertNotEqual(code, 0, out)
        self.assertEqual(self.error_rules(out), {self.R, validate.R_STATE}, out)
        for row in (LOOP, PLAN):
            self.assertIn(f"{CC}/{row}", out)

    def test_a_described_span_stands_in_for_the_quote(self):
        span = {
            "description": INSTALL_DESCRIPTION,
            "raw_line_start": 1,
            "raw_line_end": 1,
            "span_sha256": SPAN_SHA,
        }
        fx = self.fresh()
        fx.evidence(CC, 1, quote="", described_span=span)
        self.assertClean(fx)

    def test_is_verified_evidence_reads_the_quote_and_the_span(self):
        v = validate.Validator(Path("."))
        base = make_evidence(CC, 1)
        span = {"description": INSTALL_DESCRIPTION, "raw_line_start": 1}
        for rec, expect in (
            (base, True),
            ({**base, "quote": ""}, False),
            ({**base, "quote": "  "}, False),
            ({**base, "quote": "", "described_span": span}, True),
            ({**base, "quote": "", "described_span": None}, False),
            ({**base, "quote": "", "described_span": {}}, False),
        ):
            v.evidence_by_id = {base["id"]: rec}
            self.assertIs(v._is_verified_evidence(base["id"]), expect, rec)


class UrlStrictnessTests(ValidatorCase):
    """Finding 7: no userinfo and no port, the renderer's own test."""

    R = "R05-evidence-quality"

    def test_userinfo_and_ports_are_rejected_in_both_url_fields(self):
        bad = [
            "https://user:" + "pw" + "@code.claude.com/a",  # parts: not a scannable credential URL
            "https://user@code.claude.com/a",
            "https://code.claude.com:8443/a",
            "https://code.claude.com:443/a",
            "https://code.claude.com:/a",
        ]
        table = []
        for url in bad:
            table.append((f"url {url}", lambda fx, u=url: fx.evidence(CC, 4, url=u), ()))
            table.append(
                (f"url_effective {url}", lambda fx, u=url: fx.evidence(CC, 4, url_effective=u), ())
            )
        self.cases(self.R, table)

    def test_the_two_tests_agree_with_the_renderer(self):
        hosts = ["code.claude.com"]
        for url in (
            "https://code.claude.com/a",
            "https://CODE.claude.com/a",
            "https://code.claude.com:8443/a",
            "https://u:" + "p" + "@code.claude.com/a",
            "https://code.claude.com@evil.example/a",
        ):
            with self.subTest(url):
                self.assertEqual(
                    validate._evidence_url_problem(url, hosts) is None,
                    render.safe_external(url, tuple(hosts)),
                )


class NonFiniteNumberTests(ValidatorCase):
    """Finding 8: NaN and the infinities are not JSON; a file holding one is an R01 error."""

    R = "R01-structure"

    def test_non_finite_numbers_in_any_data_file_are_errors_naming_the_file(self):
        spots = {
            "snapshot.json": lambda fx, v: fx.snapshot(params={"x": v}),
            "register.json": lambda fx, v: fx.entry(0, score=v),
            "levers.json": lambda fx, v: fx.edit(
                "levers.json", lambda d: d["levers"][0].update(note=v)
            ),
            f"cells/{CC}.json": lambda fx, v: fx.edit(
                f"cells/{CC}.json", lambda d: d["cells"][0].update(note=v)
            ),
        }
        for rel, put in spots.items():
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(rel, value=repr(value)):
                    fx = self.fresh()
                    put(fx, value)
                    code, out = self.run_validator(fx)
                    self.assertNotEqual(code, 0, out)
                    hit = [
                        ln
                        for ln in self.error_lines(out)
                        if ln.split()[1] == self.R and ln.split()[2] == f"{rel}:"
                    ]
                    self.assertEqual(len(hit), 1, out)
                    self.assertIn("non-finite", hit[0])

    def test_an_overflowing_literal_is_rejected_too(self):
        fx = self.fresh()
        text = fx.path("register.json").read_text(encoding="utf-8")
        fx.path("register.json").write_text(text.replace('"rank": 1', '"rank": 1e999', 1))
        self.assertRejected(fx, self.R, where="register.json")

    def test_load_json_raises_a_value_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            for text in ("NaN", "Infinity", "-Infinity", '{"a": [NaN]}', "1e999"):
                path.write_text(text, encoding="utf-8")
                with self.subTest(text), self.assertRaises(ValueError):
                    validate.load_json(path)
            path.write_text('{"a": [1, 2.5, -0.0, 1e3]}', encoding="utf-8")
            self.assertEqual(validate.load_json(path), {"a": [1, 2.5, -0.0, 1e3]})


class FacetsFileTests(ValidatorCase):
    """Finding 9: facets.json itself is checked."""

    R = "R01-structure"

    @staticmethod
    def facets(fx, fn):
        fx.edit("facets.json", fn)

    def facet(self, doc, facet_id):
        return next(f for f in doc["facets"] if f["id"] == facet_id)

    def test_facets_file_violations_are_rejected(self):
        def move_row(doc):
            row = next(r for r in self.facet(doc, "F17")["rows"] if r["id"] == PICKER)
            self.facet(doc, "F17")["rows"].remove(row)
            self.facet(doc, "F01")["rows"].append(row)

        def duplicate_row(doc):
            rows = self.facet(doc, "F01")["rows"]
            rows.append(copy.deepcopy(rows[0]))

        def duplicate_facet(doc):
            doc["facets"].append(copy.deepcopy(self.facet(doc, "F19")))

        def row_in_optional_and_core(doc):
            doc["optional_facets"][0]["rows"][0]["id"] = LOOP

        def duplicate_optional_facet(doc):
            doc["optional_facets"].append(copy.deepcopy(doc["optional_facets"][0]))

        def optional_facet_reuses_core_id(doc):
            doc["optional_facets"][0]["id"] = "F01"

        def facet_without_id(doc):
            del self.facet(doc, "F19")["id"]

        table = [
            ("row under another facet's prefix", move_row),
            ("duplicate row id inside a facet", duplicate_row),
            ("duplicate facet id", duplicate_facet),
            ("a row id in both a core and an optional facet", row_in_optional_and_core),
            ("duplicate optional facet id", duplicate_optional_facet),
            ("an optional facet reusing a core facet id", optional_facet_reuses_core_id),
            ("a facet without an id", facet_without_id),
            ("a facet that is not an object", lambda doc: doc["facets"].append("F99")),
        ]
        for name, mutate in table:
            with self.subTest(name):
                fx = self.fresh()
                self.facets(fx, mutate)
                code, out = self.run_validator(fx)
                self.assertNotEqual(code, 0, out)
                self.assertIn(self.R, self.error_rules(out), out)
                hit = [ln for ln in self.error_lines(out) if "facets.json" in ln]
                self.assertTrue(hit, out)

    def test_the_finding_names_the_facet_and_the_row(self):
        fx = self.fresh()

        def move_row(doc):
            row = next(r for r in self.facet(doc, "F17")["rows"] if r["id"] == PICKER)
            self.facet(doc, "F17")["rows"].remove(row)
            self.facet(doc, "F01")["rows"].append(row)

        self.facets(fx, move_row)
        _, out = self.run_validator(fx)
        hit = [ln for ln in self.error_lines(out) if PICKER in ln and "F01" in ln]
        self.assertTrue(hit, out)

    def test_a_clean_facets_file_passes(self):
        self.assertClean(self.fresh())

    def test_the_real_facets_file_has_no_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("facets.json", "surfaces.json"):
                (Path(tmp) / name).write_bytes((DATA_DIR / name).read_bytes())
            findings, _ = validate.validate(tmp, check_repo_paths=False)
        self.assertEqual([f.line() for f in findings if f.level == "error"], [])


class InstallTextTests(ValidatorCase):
    """Carry-over from review 2: continuations, context windows, headings, span descriptions."""

    R = "R06-install-line"

    @staticmethod
    def continued():
        """A piped installer split over two lines by a trailing backslash."""
        return "cu" + "rl -fsSL https://example.com/get | \\\n" + "s" + "h"

    def test_the_samples_are_install_text_only_as_a_whole(self):
        first, second = self.continued().split("\n")
        self.assertTrue(install_text(self.continued()))
        self.assertFalse(install_text(first))
        self.assertFalse(install_text(second))
        self.assertTrue(install_text(first + "\n" + second))

    def test_install_text_in_any_stored_text_field_fails(self):
        first, second = self.continued().split("\n")
        single = install_line()
        table = [
            (
                "quote with a continuation",
                lambda fx: fx.evidence(CC, 4, quote=self.continued()),
                (),
            ),
            ("context_before line", lambda fx: fx.evidence(CC, 4, context_before=[single]), ()),
            ("context_after line", lambda fx: fx.evidence(CC, 4, context_after=[single]), ()),
            (
                "context_before pair joined by a continuation",
                lambda fx: fx.evidence(CC, 4, context_before=[first, second]),
                (),
            ),
            (
                "context_after pair joined by a continuation",
                lambda fx: fx.evidence(CC, 4, context_after=[first, second]),
                (),
            ),
            (
                "install word split over two context lines",
                lambda fx: fx.evidence(CC, 4, context_after=["pi" + "p", "install example"]),
                (),
            ),
            (
                "heading",
                lambda fx: fx.evidence(
                    CC, 4, locator={"heading": single, "raw_line_start": 1, "raw_line_end": 2}
                ),
                (),
            ),
            (
                "heading with a continuation",
                lambda fx: fx.evidence(
                    CC,
                    4,
                    locator={
                        "heading": self.continued(),
                        "raw_line_start": 1,
                        "raw_line_end": 2,
                    },
                ),
                (),
            ),
        ]
        self.cases(self.R, table)

    def test_the_span_description_must_be_the_fixed_text(self):
        def span(description):
            return {
                "description": description,
                "raw_line_start": 1,
                "raw_line_end": 1,
                "span_sha256": SPAN_SHA,
            }

        for description in ("an install step", install_line(), "", INSTALL_DESCRIPTION + "."):
            with self.subTest(description[:12]):
                fx = self.fresh()
                fx.evidence(CC, 4, quote="", described_span=span(description))
                self.assertRejected(fx, self.R, where=eid(CC, 4))
        fx = self.fresh()
        fx.evidence(CC, 4, quote="", described_span=span(INSTALL_DESCRIPTION))
        self.assertClean(fx)

    def test_the_scrub_placeholder_and_prose_pass(self):
        table = [
            (
                "placeholder context lines",
                lambda fx: fx.evidence(CC, 4, context_before=[CONTEXT_SCRUBBED, CONTEXT_SCRUBBED]),
            ),
            (
                "placeholder after",
                lambda fx: fx.evidence(CC, 4, context_after=[CONTEXT_SCRUBBED, "plain prose"]),
            ),
            (
                "placeholder heading",
                lambda fx: fx.evidence(
                    CC,
                    4,
                    locator={
                        "heading": CONTEXT_SCRUBBED,
                        "raw_line_start": 1,
                        "raw_line_end": 2,
                    },
                ),
            ),
            (
                "ordinary context",
                lambda fx: fx.evidence(
                    CC, 4, context_before=["Install the editor plugin.", "Then restart."]
                ),
            ),
        ]
        self.passes(table)

    def test_the_finding_names_the_field(self):
        fx = self.fresh()
        fx.evidence(CC, 4, context_after=[install_line()])
        _, out = self.run_validator(fx)
        hit = [ln for ln in self.error_lines(out) if "R06" in ln]
        self.assertTrue(hit, out)
        self.assertIn("context_after", hit[0])


class HtmlStrictnessTests(ValidatorCase):
    """Finding 11: the page scan is a real parse, not a look for one literal."""

    R = "R13-html"

    @staticmethod
    def csp(*sources):
        policy = "default-src 'none'; style-src 'unsafe-inline'; " + (
            f"script-src {' '.join(sources)}; " if sources else ""
        )
        return (
            '<meta http-equiv="Content-Security-Policy" '
            f"content=\"{policy}img-src data:; base-uri 'none'; form-action 'none'\">"
        )

    @staticmethod
    def digest(body):
        return (
            "'sha256-"
            + base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode()
            + "'"
        )

    def page(self, body, head=""):
        return f"<!DOCTYPE html><html><head>{head}</head><body>{body}</body></html>"

    def rejected(self, pages):
        for name, text in pages.items():
            with self.subTest(name):
                fx = self.fresh()
                fx.html("page.html", text)
                self.assertRejected(fx, self.R, *fx.html_flags, where="page.html")

    def passing(self, pages):
        for name, text in pages.items():
            with self.subTest(name):
                fx = self.fresh()
                fx.html("page.html", text)
                self.assertClean(fx, *fx.html_flags)

    def test_script_rules(self):
        body = "var a=1;"
        good = self.digest(body)
        self.rejected(
            {
                "script with an attribute": self.page(
                    f"<script type='module'>{body}</script>", self.csp(good)
                ),
                "script with a nonce": self.page(
                    f"<script nonce='x'>{body}</script>", self.csp(good)
                ),
                "script with src": self.page("<script src='a.js'></script>", self.csp(good)),
                "upper-case script, no policy": self.page("<SCRIPT>alert(1)</SCRIPT>"),
                "mixed-case script, wrong hash": self.page(
                    f"<ScRiPt>{body}</ScRiPt>", self.csp("'sha256-AAAA'")
                ),
                "script, policy without script-src": self.page(
                    f"<script>{body}</script>", self.csp()
                ),
                "script, hash of different text": self.page(
                    f"<script>{body}x</script>", self.csp(good)
                ),
                "script hash in a style-src only": self.page(
                    f"<script>{body}</script>",
                    '<meta http-equiv="Content-Security-Policy" '
                    f"content=\"style-src {good}; script-src 'self'\">",
                ),
                "second script is not covered": self.page(
                    f"<script>{body}</script><script>other()</script>", self.csp(good)
                ),
                "self-closing script": self.page("<script/><b>x</b>", self.csp(good)),
                "unterminated script": self.page(f"<script>{body}", self.csp(good)),
                "one of two policies lacks the hash": self.page(
                    f"<script>{body}</script>", self.csp(good) + self.csp("'sha256-AAAA'")
                ),
                "script before the policy that would allow it": self.page(
                    f"<script>{body}</script>" + self.csp(good)
                ),
            }
        )
        self.passing(
            {
                "script whose hash is in script-src": self.page(
                    f"<script>{body}</script>", self.csp(good)
                ),
                "upper-case tag with the right hash": self.page(
                    f"<SCRIPT>{body}</SCRIPT>", self.csp(good)
                ),
                "hash among other sources": self.page(
                    f"<script>{body}</script>", self.csp("'self'", good, "'sha256-AAAA'")
                ),
                "no script at all": self.page("<p>x</p>", self.csp()),
            }
        )

    def test_a_script_body_with_a_less_than_sign_is_hashed_whole(self):
        body = "var a=1<2;if(a<=3){b=4}"
        self.passing(
            {"whole body": self.page(f"<script>{body}</script>", self.csp(self.digest(body)))}
        )

    def test_event_handler_attributes(self):
        self.rejected(
            {
                "onclick": self.page("<a href='#' onclick='x()'>a</a>"),
                "upper-case ONCLICK": self.page("<a href='#' ONCLICK='x()'>a</a>"),
                "onerror on an image": self.page("<img src='a.png' onerror='x()'>"),
                "onload on the body": "<body onload='x()'>x</body>",
                "onmouseover without a value": self.page("<p onmouseover>x</p>"),
                "on-something unknown": self.page("<p onfuturething='x'>x</p>"),
            }
        )

    def test_navigation_attributes(self):
        self.rejected(
            {
                "srcset": self.page(
                    "<img src='a.png' srcset='a.png 1x, https://evil.example/b.png 2x'>"
                ),
                "srcset onerror text": self.page("<img srcset='a 1x, b onerror=x 2x'>"),
                "upper-case SRCSET": self.page("<img SRCSET='a.png 1x'>"),
                "form action": self.page("<form action='https://evil.example/'><input></form>"),
                "form with an empty action": self.page("<form action=''></form>"),
                "formaction": self.page("<button formaction='https://evil.example/'>x</button>"),
                "meta refresh": self.page(
                    "", "<meta http-equiv='refresh' content='0;url=https://evil.example/'>"
                ),
                "meta refresh upper-case": self.page("", "<META HTTP-EQUIV='Refresh' content='5'>"),
                "meta refresh with spaces": self.page(
                    "", "<meta http-equiv=' refresh ' content='5'>"
                ),
            }
        )

    def test_embedding_tags(self):
        pages = {}
        for tag, attrs in (
            ("link", "rel='stylesheet' href='a.css'"),
            ("LINK", "rel='stylesheet' href='a.css'"),
            ("iframe", "src='a.html'"),
            ("IFRAME", "src='a.html'"),
            ("object", "data='a.swf'"),
            ("embed", "src='a.swf'"),
            ("Embed", "src='a.swf'"),
            ("base", "href='https://docs.x.ai/'"),
            ("BASE", "href='a/'"),
        ):
            pages[f"<{tag}>"] = self.page(f"<{tag} {attrs}>")
        self.rejected(pages)

    def test_css_urls(self):
        self.rejected(
            {
                "style attribute, https": self.page(
                    '<p style="background:url(https://evil.example/x.png)">x</p>'
                ),
                "style attribute, upper-case URL and quotes": self.page(
                    "<p style=\"background:URL( 'https://evil.example/x.png' )\">x</p>"
                ),
                "style attribute, protocol-relative": self.page(
                    '<p style="background:url(//evil.example/x.png)">x</p>'
                ),
                "style attribute, relative path": self.page(
                    '<p style="background:url(a.png)">x</p>'
                ),
                "style block": self.page(
                    "<style>body{background:url(https://evil.example/x)}</style>"
                ),
                "style block, second url": self.page(
                    "<style>a{background:url(data:image/png;base64,AA)}"
                    "b{background:url(https://evil.example/x)}</style>"
                ),
                "upper-case STYLE block": self.page("<STYLE>a{background:url(b.png)}</STYLE>"),
                "style block import": self.page("<style>@import 'a.css';</style>"),
                "style block import with url": self.page(
                    "<style>@import url(https://evil.example/a.css);</style>"
                ),
                "css escape hiding a url": self.page(
                    '<p style="background:\\75rl(https://evil.example/x)">x</p>'
                ),
            }
        )
        self.passing(
            {
                "data url in a style attribute": self.page(
                    '<p style="background:url(data:image/png;base64,AAAA)">x</p>'
                ),
                "fragment url": self.page('<p style="fill:url(#grad)">x</p>'),
                "quoted fragment url": self.page("<p style=\"fill:url('#grad')\">x</p>"),
                "style block without urls": self.page("<style>body{margin:0}a{color:red}</style>"),
                "style block with a data url": self.page(
                    '<style>a{background:URL("data:image/png;base64,AA")}</style>'
                ),
            }
        )

    def test_the_link_checks_still_apply_and_get_stricter(self):
        self.rejected(
            {
                "port on an allow-listed host": self.page(
                    "<a href='https://docs.x.ai:8443/a'>x</a>"
                ),
                "userinfo on an allow-listed host": self.page(
                    "<a href='https://user@docs.x.ai/a'>x</a>"
                ),
            }
        )

    def test_a_real_render_of_the_fixture_data_passes_every_check(self):
        fx = self.fresh()
        pages = render.render_all(fx.root)
        self.assertTrue(any("<script>" in text for text in pages.values()))
        for path, text in pages.items():
            fx.html(path, text)
        self.assertClean(fx, *fx.html_flags)
        scripts = [p for p, t in pages.items() if "<script>" in t]
        self.assertTrue(scripts)

    def test_a_real_page_with_a_changed_script_is_caught(self):
        fx = self.fresh()
        pages = render.render_all(fx.root)
        name = next(p for p, t in pages.items() if "<script>" in t)
        for path, text in pages.items():
            fx.html(path, text)
        fx.html(name, pages[name].replace(render.AGE_SCRIPT, render.AGE_SCRIPT + "alert(1);"))
        self.assertRejected(fx, self.R, *fx.html_flags, where=name)


class SchemaSubsetTests(unittest.TestCase):
    SCHEMA = {
        "type": "object",
        "additionalProperties": False,
        "required": ["a"],
        "properties": {
            "a": {"type": "string", "pattern": "^x[0-9]$", "maxLength": 2},
            "n": {"type": "integer", "minimum": 1},
            "e": {"enum": [1, "two"]},
            "l": {"type": "array", "minItems": 1, "maxItems": 2, "items": {"type": "integer"}},
            "u": {"type": ["string", "null"]},
            "m": {"type": "object", "additionalProperties": {"type": "integer"}},
        },
    }

    def problems(self, value):
        return validate.check_schema(value, self.SCHEMA)

    def test_a_valid_value_has_no_problems(self):
        ok = {"a": "x1", "n": 1, "e": "two", "l": [1, 2], "u": None, "m": {"k": 3}}
        self.assertEqual(self.problems(ok), [])

    def test_each_keyword_reports_its_violation(self):
        cases = {
            "required": {},
            "additionalProperties false": {"a": "x1", "z": 1},
            "pattern": {"a": "y1"},
            "maxLength": {"a": "x12"},
            "minimum": {"a": "x1", "n": 0},
            "type integer rejects a bool": {"a": "x1", "n": True},
            "type integer rejects a float": {"a": "x1", "n": 1.5},
            "enum": {"a": "x1", "e": 3},
            "enum does not equate True with 1": {"a": "x1", "e": True},
            "minItems": {"a": "x1", "l": []},
            "maxItems": {"a": "x1", "l": [1, 2, 3]},
            "items": {"a": "x1", "l": ["s"]},
            "type list": {"a": "x1", "u": 5},
            "additionalProperties schema": {"a": "x1", "m": {"k": "s"}},
            "root type": ["not", "an", "object"],
        }
        for name, value in cases.items():
            with self.subTest(name):
                self.assertTrue(self.problems(value), value)

    def test_a_pattern_ending_in_a_dollar_does_not_accept_a_trailing_newline(self):
        schema = {"type": "string", "pattern": "^x[0-9]$"}
        self.assertEqual(validate.check_schema("x1", schema), [])
        self.assertTrue(validate.check_schema("x1\n", schema))

    def test_annotation_keywords_are_ignored_and_unknown_ones_raise(self):
        schema = {"$schema": "x", "$id": "y", "title": "t", "description": "d", "type": "string"}
        self.assertEqual(validate.check_schema("s", schema), [])
        for keyword in ("oneOf", "anyOf", "$ref", "format", "const", "maxProperties"):
            with self.subTest(keyword), self.assertRaises(validate.SchemaError):
                validate.check_schema("s", {keyword: []})
        with self.assertRaises(validate.SchemaError):
            validate.check_schema({"k": 1}, {"properties": {"k": {"oneOf": []}}})
        with self.assertRaises(validate.SchemaError):
            validate.check_schema(1, {"type": "complex"})

    def test_every_keyword_the_real_schemas_use_is_supported(self):
        used = set()

        def walk(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == "properties":
                        for sub in value.values():
                            walk(sub)
                    else:
                        used.add(key)
                        walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        for name in validate.SCHEMA_NAMES:
            schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
            walk(schema)
            validate.check_schema({}, schema)  # raises SchemaError on an unsupported keyword
        self.assertLessEqual(used - {"enum", "items"}, validate._SUPPORTED_KEYWORDS)


if __name__ == "__main__":
    unittest.main()
