"""Walk a JSON Schema and report fields that coerce fabrication."""

from __future__ import annotations

import json
from dataclasses import dataclass, field as dc_field
from typing import Any

from .rules import (
    SEVERITY_ORDER,
    allows_null,
    enum_values,
    has_escape,
    is_escape_value,
)

__all__ = ["Finding", "lint", "lint_file", "extract_schemas"]


@dataclass
class Finding:
    path: str
    rule: str
    severity: str
    message: str
    fix: str
    schema_name: str = ""

    def as_dict(self) -> dict:
        return {
            "schema": self.schema_name,
            "path": self.path,
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "fix": self.fix,
        }


@dataclass
class _Ctx:
    root: dict
    findings: list = dc_field(default_factory=list)
    seen_refs: set = dc_field(default_factory=set)


def _resolve(ref: str, ctx: _Ctx):
    """Resolve a local JSON pointer. Remote refs are out of scope."""
    if not ref.startswith("#"):
        return None
    node: Any = ctx.root
    for token in ref.lstrip("#/").split("/"):
        if not token:
            continue
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            try:
                node = node[int(token)]
            except (ValueError, IndexError):
                return None
        elif isinstance(node, dict):
            if token not in node:
                return None
            node = node[token]
        else:
            return None
    return node if isinstance(node, dict) else None


def _deref(schema: dict, ctx: _Ctx) -> dict:
    seen = set()
    while isinstance(schema, dict) and "$ref" in schema:
        ref = schema["$ref"]
        if ref in seen:
            return {}
        seen.add(ref)
        target = _resolve(ref, ctx)
        if target is None:
            return {}
        merged = {k: v for k, v in schema.items() if k != "$ref"}
        schema = {**target, **merged}
    return schema if isinstance(schema, dict) else {}


def _describe(values) -> str:
    shown = [repr(v) for v in values[:6]]
    if len(values) > 6:
        shown.append("...")
    return ", ".join(shown)


def _check_field(name: str, schema: dict, path: str, required: bool, ctx: _Ctx):
    schema = _deref(schema, ctx)
    if not schema:
        return

    values = enum_values(schema)
    ftype = schema.get("type")
    if isinstance(ftype, list):
        ftype = next((t for t in ftype if t != "null"), None)

    # A field the model may omit entirely already has an exit.
    if not required:
        _recurse(schema, path, ctx)
        return

    if has_escape(schema):
        _recurse(schema, path, ctx)
        return

    if values is not None:
        ctx.findings.append(Finding(
            path=path,
            rule="required-enum-no-escape",
            severity="high",
            message=(
                f"Required closed vocabulary with no way to report missing "
                f"evidence. Permitted values: {_describe(values)}. If the input "
                f"lacks the evidence for this field, every legal value is a "
                f"claim the model cannot support."
            ),
            fix=(
                'Add "insufficient_evidence" to the enum, or allow null via '
                '"type": ["string", "null"].'
            ),
        ))
    elif ftype == "array":
        min_items = schema.get("minItems", 0)
        if min_items and min_items > 0:
            ctx.findings.append(Finding(
                path=path,
                rule="required-array-min-items",
                severity="high",
                message=(
                    f"Required array with minItems={min_items} and no null "
                    f"option. An empty result is not expressible, so absent "
                    f"evidence must be filled with invented entries."
                ),
                fix='Set "minItems": 0, or allow null.',
            ))
        else:
            ctx.findings.append(Finding(
                path=path,
                rule="required-array-not-nullable",
                severity="low",
                message=(
                    "Required array without a null option. An empty array can "
                    "express absence, so this is usually safe; flagged only "
                    "because a downstream consumer may treat [] as a parse "
                    "failure rather than a finding."
                ),
                fix='Allow null if [] and "not determined" must be distinguished.',
            ))
    elif ftype == "boolean":
        ctx.findings.append(Finding(
            path=path,
            rule="required-boolean-no-escape",
            severity="high",
            message=(
                "Required boolean with no null option. true and false are a "
                "two-value closed vocabulary; neither can express uncertainty, "
                "and a coin flip is recorded as a determination."
            ),
            fix='Allow null via "type": ["boolean", "null"].',
        ))
    elif ftype in {"number", "integer"}:
        ctx.findings.append(Finding(
            path=path,
            rule="required-number-no-escape",
            severity="medium",
            message=(
                "Required numeric field with no null option. A number carries "
                "no disclaimer, so an unknown quantity is emitted as a "
                "specific figure indistinguishable from a measured one."
            ),
            fix='Allow null via "type": ["number", "null"].',
        ))
    elif ftype == "string":
        ctx.findings.append(Finding(
            path=path,
            rule="required-string-no-escape",
            severity="low",
            message=(
                "Required string with no null option. Models usually hedge in "
                "free strings rather than fabricate (0/20 in the reference "
                "measurement), but the hedge lands in a field a consumer will "
                "read as a value."
            ),
            fix='Allow null so absence is machine-detectable, not prose.',
        ))
    elif ftype == "object":
        pass  # structure is checked by the recursion below

    _recurse(schema, path, ctx)


def _recurse(schema: dict, path: str, ctx: _Ctx):
    schema = _deref(schema, ctx)
    if not schema:
        return

    props = schema.get("properties")
    if isinstance(props, dict):
        required = set(schema.get("required") or [])
        for name, sub in props.items():
            if isinstance(sub, dict):
                child = f"{path}.{name}" if path else name
                _check_field(name, sub, child, name in required, ctx)

    items = schema.get("items")
    if isinstance(items, dict):
        _recurse(items, f"{path}[]", ctx)
    elif isinstance(items, list):
        for i, sub in enumerate(items):
            if isinstance(sub, dict):
                _recurse(sub, f"{path}[{i}]", ctx)

    for key in ("anyOf", "oneOf", "allOf"):
        for i, branch in enumerate(schema.get(key) or []):
            if isinstance(branch, dict):
                _recurse(branch, f"{path}({key}[{i}])", ctx)


def extract_schemas(doc: Any) -> list:
    """Pull schemas out of the common tool-definition wrappers.

    Recognizes a bare JSON Schema, an OpenAI function/tool definition, an
    Anthropic tool definition, and lists of any of these.
    """
    out = []

    def visit(node, name_hint=""):
        if isinstance(node, list):
            for item in node:
                visit(item, name_hint)
            return
        if not isinstance(node, dict):
            return
        # OpenAI: {"type": "function", "function": {"name", "parameters"}}
        if isinstance(node.get("function"), dict):
            fn = node["function"]
            if isinstance(fn.get("parameters"), dict):
                out.append((fn.get("name", name_hint or "function"), fn["parameters"]))
                return
        # OpenAI flat / responses API: {"name", "parameters"}
        if isinstance(node.get("parameters"), dict) and "name" in node:
            out.append((node.get("name", name_hint), node["parameters"]))
            return
        # Anthropic: {"name", "input_schema"}
        if isinstance(node.get("input_schema"), dict):
            out.append((node.get("name", name_hint), node["input_schema"]))
            return
        # OpenAI structured outputs: {"json_schema": {"name", "schema"}}
        if isinstance(node.get("json_schema"), dict):
            js = node["json_schema"]
            if isinstance(js.get("schema"), dict):
                out.append((js.get("name", name_hint), js["schema"]))
                return
        # A bare schema.
        if "properties" in node or "$defs" in node or node.get("type") == "object":
            out.append((name_hint, node))
            return
        if isinstance(node.get("tools"), list):
            visit(node["tools"], name_hint)

    visit(doc)
    return out


def lint(schema: dict, name: str = "", min_severity: str = "low") -> list:
    """Lint one JSON Schema. Returns findings sorted most severe first."""
    ctx = _Ctx(root=schema)
    _recurse(schema, "", ctx)
    floor = SEVERITY_ORDER.get(min_severity, 1)
    for f in ctx.findings:
        f.schema_name = name
    findings = [f for f in ctx.findings if SEVERITY_ORDER[f.severity] >= floor]
    findings.sort(key=lambda f: (-SEVERITY_ORDER[f.severity], f.path))
    return findings


def lint_file(path: str, min_severity: str = "low") -> list:
    with open(path) as fh:
        doc = json.load(fh)
    findings = []
    for name, schema in extract_schemas(doc) or [("", doc)]:
        findings.extend(lint(schema, name=name, min_severity=min_severity))
    findings.sort(key=lambda f: (-SEVERITY_ORDER[f.severity], f.schema_name, f.path))
    return findings
