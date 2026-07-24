"""Tests for phantomfill-lint.

The anchor case is the schema from the PhantomFill paper: the required-field
rung that drove ten of thirteen models to 100% fabrication. The linter must
flag it, and must clear the escape-hatch rung that the frontier models handled.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from phantomfill_lint import lint, lint_file, extract_schemas  # noqa: E402
from phantomfill_lint.cli import main as cli_main  # noqa: E402

# The rung-3 schema from the paper.
JSON_REQ = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": ["positive", "negative", "mixed"]},
        "main_themes": {"type": "array", "items": {"type": "string"}, "minItems": 3},
        "representative_reaction": {"type": "string"},
        "controversy_level": {"type": "string", "enum": ["low", "medium", "high"]},
    },
    "required": [
        "sentiment", "main_themes", "representative_reaction", "controversy_level",
    ],
}

# The rung-2 schema: every field admits an escape.
JSON_ESC = {
    "type": "object",
    "properties": {
        "sentiment": {
            "type": "string",
            "enum": ["positive", "negative", "mixed", "insufficient_evidence"],
        },
        "main_themes": {"type": ["array", "null"], "items": {"type": "string"}},
        "representative_reaction": {"type": ["string", "null"]},
        "controversy_level": {
            "type": "string",
            "enum": ["low", "medium", "high", "insufficient_evidence"],
        },
    },
    "required": [
        "sentiment", "main_themes", "representative_reaction", "controversy_level",
    ],
}


def rules_for(findings):
    return {f.rule for f in findings}


def by_path(findings):
    return {f.path: f for f in findings}


class TestPaperSchemas:
    def test_required_rung_flags_both_enums_and_the_array(self):
        found = by_path(lint(JSON_REQ))
        assert found["sentiment"].rule == "required-enum-no-escape"
        assert found["sentiment"].severity == "high"
        assert found["controversy_level"].rule == "required-enum-no-escape"
        assert found["main_themes"].rule == "required-array-min-items"
        assert found["main_themes"].severity == "high"

    def test_required_rung_rates_the_free_string_lowest(self):
        """Matches the measured result: strings carry hedges, enums cannot."""
        found = by_path(lint(JSON_REQ))
        assert found["representative_reaction"].severity == "low"
        assert found["sentiment"].severity == "high"

    def test_escape_rung_is_clean(self):
        assert lint(JSON_ESC) == []

    def test_adding_one_enum_value_clears_the_high_finding(self):
        """The paper's proposed fix is one line of schema. Verify it works."""
        patched = json.loads(json.dumps(JSON_REQ))
        patched["properties"]["sentiment"]["enum"].append("insufficient_evidence")
        remaining = {f.path for f in lint(patched) if f.severity == "high"}
        assert "sentiment" not in remaining


class TestEscapeDetection:
    @pytest.mark.parametrize("value", [
        "insufficient_evidence", "Insufficient Evidence", "insufficient-evidence",
        "unknown", "N/A", "not_available", "UNDETERMINED", "no_data",
    ])
    def test_recognized_escape_values(self, value):
        schema = {
            "type": "object",
            "properties": {"f": {"enum": ["a", "b", value]}},
            "required": ["f"],
        }
        assert lint(schema) == []

    @pytest.mark.parametrize("value", ["neutral", "other", "mixed", "unclear_but_present"])
    def test_near_misses_are_not_escapes(self, value):
        """'neutral' and 'other' are answers, not abstentions."""
        schema = {
            "type": "object",
            "properties": {"f": {"enum": ["a", "b", value]}},
            "required": ["f"],
        }
        assert rules_for(lint(schema)) == {"required-enum-no-escape"}

    def test_nullable_variants(self):
        for prop in (
            {"type": ["string", "null"], "enum": ["a", "b"]},
            {"type": "string", "enum": ["a", "b"], "nullable": True},
            {"anyOf": [{"type": "string", "enum": ["a"]}, {"type": "null"}]},
        ):
            schema = {"type": "object", "properties": {"f": prop}, "required": ["f"]}
            assert lint(schema) == [], prop


class TestFieldTypes:
    def test_boolean_is_high(self):
        schema = {
            "type": "object",
            "properties": {"is_fraud": {"type": "boolean"}},
            "required": ["is_fraud"],
        }
        assert rules_for(lint(schema)) == {"required-boolean-no-escape"}

    def test_number_is_medium(self):
        schema = {
            "type": "object",
            "properties": {"score": {"type": "number"}},
            "required": ["score"],
        }
        f = lint(schema)[0]
        assert f.rule == "required-number-no-escape"
        assert f.severity == "medium"

    def test_const_is_a_closed_vocabulary(self):
        schema = {
            "type": "object",
            "properties": {"verdict": {"const": "guilty"}},
            "required": ["verdict"],
        }
        assert rules_for(lint(schema)) == {"required-enum-no-escape"}

    def test_array_without_min_items_is_low(self):
        schema = {
            "type": "object",
            "properties": {"tags": {"type": "array", "items": {"type": "string"}}},
            "required": ["tags"],
        }
        assert lint(schema)[0].severity == "low"

    def test_optional_fields_are_never_flagged(self):
        schema = {
            "type": "object",
            "properties": {"sentiment": {"enum": ["positive", "negative"]}},
        }
        assert lint(schema) == []


class TestStructure:
    def test_nested_objects(self):
        schema = {
            "type": "object",
            "properties": {
                "analysis": {
                    "type": "object",
                    "properties": {"mood": {"enum": ["up", "down"]}},
                    "required": ["mood"],
                }
            },
            "required": ["analysis"],
        }
        assert by_path(lint(schema))["analysis.mood"].severity == "high"

    def test_objects_inside_arrays(self):
        schema = {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"grade": {"enum": ["A", "B"]}},
                        "required": ["grade"],
                    },
                }
            },
        }
        assert "items[].grade" in by_path(lint(schema))

    def test_ref_resolution(self):
        schema = {
            "$defs": {
                "Mood": {"type": "string", "enum": ["happy", "sad"]},
            },
            "type": "object",
            "properties": {"mood": {"$ref": "#/$defs/Mood"}},
            "required": ["mood"],
        }
        assert by_path(lint(schema))["mood"].rule == "required-enum-no-escape"

    def test_circular_ref_terminates(self):
        schema = {
            "$defs": {"Node": {"$ref": "#/$defs/Node"}},
            "type": "object",
            "properties": {"n": {"$ref": "#/$defs/Node"}},
            "required": ["n"],
        }
        lint(schema)  # must not hang or raise

    def test_unresolvable_ref_is_ignored(self):
        schema = {
            "type": "object",
            "properties": {"x": {"$ref": "https://example.com/s.json"}},
            "required": ["x"],
        }
        assert lint(schema) == []


class TestWrapperFormats:
    def test_openai_tool(self):
        doc = [{"type": "function", "function": {"name": "analyze", "parameters": JSON_REQ}}]
        names = {n for n, _ in extract_schemas(doc)}
        assert names == {"analyze"}

    def test_anthropic_tool(self):
        doc = [{"name": "analyze", "input_schema": JSON_REQ}]
        assert extract_schemas(doc)[0][0] == "analyze"

    def test_openai_structured_output(self):
        doc = {"json_schema": {"name": "thread", "schema": JSON_REQ}}
        assert extract_schemas(doc)[0][0] == "thread"

    def test_bare_schema(self):
        assert extract_schemas(JSON_REQ)[0][1] == JSON_REQ


class TestCLI:
    def _write(self, tmp_path, doc):
        p = tmp_path / "schema.json"
        p.write_text(json.dumps(doc))
        return str(p)

    def test_exit_1_on_high(self, tmp_path, capsys):
        assert cli_main([self._write(tmp_path, JSON_REQ), "--no-color"]) == 1
        assert "required-enum-no-escape" in capsys.readouterr().out

    def test_exit_0_on_clean(self, tmp_path):
        assert cli_main([self._write(tmp_path, JSON_ESC), "--no-color"]) == 0

    def test_fail_on_never(self, tmp_path):
        assert cli_main([self._write(tmp_path, JSON_REQ), "--fail-on", "never"]) == 0

    def test_json_output_is_valid(self, tmp_path, capsys):
        cli_main([self._write(tmp_path, JSON_REQ), "--format", "json"])
        payload = json.loads(capsys.readouterr().out)
        assert {f["rule"] for f in payload} >= {"required-enum-no-escape"}

    def test_github_annotations(self, tmp_path, capsys):
        cli_main([self._write(tmp_path, JSON_REQ), "--format", "github"])
        assert "::error title=phantomfill-lint::" in capsys.readouterr().out

    def test_min_severity_filters(self, tmp_path, capsys):
        cli_main([self._write(tmp_path, JSON_REQ), "--min-severity", "high", "--format", "json"])
        payload = json.loads(capsys.readouterr().out)
        assert all(f["severity"] == "high" for f in payload)

    def test_missing_file_exits_2(self, tmp_path, capsys):
        assert cli_main([str(tmp_path / "nope.json")]) == 2

    def test_invalid_json_exits_2(self, tmp_path, capsys):
        p = tmp_path / "bad.json"
        p.write_text("{not json")
        assert cli_main([str(p)]) == 2

    def test_module_entrypoint(self, tmp_path):
        path = self._write(tmp_path, JSON_ESC)
        r = subprocess.run(
            [sys.executable, "-m", "phantomfill_lint.cli", path, "--no-color"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).resolve().parents[1]),
        )
        assert r.returncode == 0, r.stderr
