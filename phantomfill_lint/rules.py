"""Coercion rules for JSON Schema fields.

Each rule answers one question: if the evidence for this field is absent from the
input, can the model say so *inside the schema*? A field with no such affordance
is coercive, and coercive fields are where PhantomFill measures fabrication.

Severity is calibrated to the measured per-field fabrication rates in the paper
(GPT-5.5, Domain 2, required-field rung, n = 20 per field):

    required enum, no escape value        20/20 fabricated
    required array, minItems >= 1          3/20 fabricated
    required free string                   0/20 fabricated

Closed vocabularies are the danger. A string can carry "no data available" and
frequently does; an enum has no such token unless you put one there.
"""

from __future__ import annotations

# Values that count as "I could not determine this". Compared after normalizing
# case and collapsing separators, so "insufficient_evidence", "Insufficient
# Evidence" and "insufficient-evidence" are all recognized.
ESCAPE_VOCAB = frozenset({
    "insufficientevidence", "insufficientdata", "insufficientinformation",
    "notavailable", "unavailable", "notprovided", "notspecified", "notstated",
    "notdetermined", "undetermined", "indeterminate", "cannotdetermine",
    "unknown", "unspecified", "nodata", "noevidence", "noinformation",
    "na", "nan", "null", "none", "empty", "missing", "absent",
    "notapplicable", "declinedtoanswer", "abstain",
})

SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1}


def normalize(value) -> str:
    """Fold a candidate enum value to its comparison form."""
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def is_escape_value(value) -> bool:
    return normalize(value) in ESCAPE_VOCAB


def allows_null(schema: dict) -> bool:
    """True if the field may legally be null.

    Covers draft-07 union types, 2020-12 `type` arrays, OpenAPI's `nullable`,
    and a null branch inside anyOf/oneOf.
    """
    if schema.get("nullable") is True:
        return True
    t = schema.get("type")
    if t == "null" or (isinstance(t, list) and "null" in t):
        return True
    for key in ("anyOf", "oneOf"):
        for branch in schema.get(key) or []:
            if isinstance(branch, dict) and allows_null(branch):
                return True
    return False


def enum_values(schema: dict):
    """Collect the closed vocabulary of a field, or None if it is not closed.

    A `const` is a one-value vocabulary. anyOf/oneOf branches that are each
    closed compose into one closed vocabulary; if any branch is open, so is the
    field.
    """
    if "enum" in schema and isinstance(schema["enum"], list):
        return list(schema["enum"])
    if "const" in schema:
        return [schema["const"]]
    for key in ("anyOf", "oneOf"):
        branches = schema.get(key)
        if not branches:
            continue
        collected = []
        for branch in branches:
            if not isinstance(branch, dict):
                return None
            if branch.get("type") == "null":
                collected.append(None)
                continue
            sub = enum_values(branch)
            if sub is None:
                return None
            collected.extend(sub)
        if collected:
            return collected
    return None


def has_escape(schema: dict) -> bool:
    """Can this field express 'the evidence is not here'?"""
    if allows_null(schema):
        return True
    values = enum_values(schema)
    if values is not None:
        return any(is_escape_value(v) for v in values if v is not None)
    return False
