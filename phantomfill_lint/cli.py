"""Command-line entry point for phantomfill-lint."""

from __future__ import annotations

import argparse
import glob
import json
import sys

from .lint import lint_file
from .rules import SEVERITY_ORDER

BOLD, DIM, RESET = "\033[1m", "\033[2m", "\033[0m"
COLOR = {"high": "\033[31m", "medium": "\033[33m", "low": "\033[36m"}


def _supports_color(stream) -> bool:
    return hasattr(stream, "isatty") and stream.isatty()


def _render_text(findings, color: bool) -> str:
    if not findings:
        return "phantomfill-lint: no coercive fields found."
    lines = []
    for f in findings:
        c = COLOR.get(f.severity, "") if color else ""
        r = RESET if color else ""
        b = BOLD if color else ""
        d = DIM if color else ""
        where = f"{f.schema_name}:{f.path}" if f.schema_name else f.path
        lines.append(f"{c}{f.severity.upper():<6}{r} {b}{where}{r}  {d}[{f.rule}]{r}")
        lines.append(f"       {f.message}")
        lines.append(f"       {d}fix:{r} {f.fix}")
        lines.append("")
    counts = {}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    summary = ", ".join(f"{counts[s]} {s}" for s in ("high", "medium", "low") if s in counts)
    lines.append(f"{len(findings)} finding(s): {summary}")
    return "\n".join(lines)


def _render_github(findings) -> str:
    out = []
    for f in findings:
        level = "error" if f.severity == "high" else "warning"
        where = f"{f.schema_name}:{f.path}" if f.schema_name else f.path
        msg = f"{where} [{f.rule}] {f.message} Fix: {f.fix}".replace("\n", " ")
        out.append(f"::{level} title=phantomfill-lint::{msg}")
    return "\n".join(out)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="phantomfill-lint",
        description=(
            "Flag JSON Schema fields that leave a model no way to report missing "
            "evidence. Such fields coerce fabrication: see PhantomFill."
        ),
    )
    p.add_argument("paths", nargs="+", help="JSON Schema or tool-definition files (globs ok)")
    p.add_argument("--format", choices=["text", "json", "github"], default="text")
    p.add_argument("--min-severity", choices=["low", "medium", "high"], default="low")
    p.add_argument(
        "--fail-on",
        choices=["never", "low", "medium", "high"],
        default="high",
        help="exit non-zero when a finding at or above this severity appears (default: high)",
    )
    p.add_argument("--no-color", action="store_true")
    args = p.parse_args(argv)

    files = []
    for pattern in args.paths:
        hits = sorted(glob.glob(pattern, recursive=True))
        files.extend(hits or [pattern])

    findings, errors = [], []
    for path in files:
        try:
            findings.extend(lint_file(path, min_severity=args.min_severity))
        except FileNotFoundError:
            errors.append(f"phantomfill-lint: no such file: {path}")
        except json.JSONDecodeError as e:
            errors.append(f"phantomfill-lint: {path}: invalid JSON: {e}")

    for e in errors:
        print(e, file=sys.stderr)

    if args.format == "json":
        print(json.dumps([f.as_dict() for f in findings], indent=2))
    elif args.format == "github":
        print(_render_github(findings))
    else:
        color = not args.no_color and _supports_color(sys.stdout)
        print(_render_text(findings, color))

    if errors:
        return 2
    if args.fail_on != "never":
        floor = SEVERITY_ORDER[args.fail_on]
        if any(SEVERITY_ORDER[f.severity] >= floor for f in findings):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
