"""phantomfill-lint: find JSON Schema fields that coerce fabrication.

A field is coercive when it is required and offers no way to say "the evidence
for this is not in the input". Under such a field, models that answer honestly
in prose invent a value instead. See https://github.com/ranausmanai/phantomfill

    from phantomfill_lint import lint
    findings = lint({"type": "object",
                     "properties": {"sentiment": {"enum": ["positive", "negative"]}},
                     "required": ["sentiment"]})
"""

from .lint import Finding, extract_schemas, lint, lint_file
from .rules import ESCAPE_VOCAB, has_escape

__version__ = "0.1.0"
__all__ = [
    "Finding",
    "lint",
    "lint_file",
    "extract_schemas",
    "has_escape",
    "ESCAPE_VOCAB",
    "__version__",
]
