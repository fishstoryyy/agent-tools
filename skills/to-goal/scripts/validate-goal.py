#!/usr/bin/env python3
"""Validate the structural envelope of a to-goal/v1 artifact."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SCHEMA_LINE = "- **Schema:** `to-goal/v1`"
CONTRACT_PREAMBLE = [
    "> This file is the contract guiding the work. Do not edit or commit it.",
    "> If a criterion seems wrong or unachievable as written, report it to the user rather than",
    "> technically satisfying it while violating its intended outcome.",
]
H2_HEADINGS = [
    "## Context",
    "## Intended Outcome",
    "## Scope",
    "## Non-goals",
    "## Settled Decisions",
    "## Constraints and Dependencies",
    "## Acceptance Criteria",
]
AC_RE = re.compile(r"^- `AC-(\d{3})`\s+(.+?)\s+\*\*Evidence:\*\*\s+(.+)$")
PLACEHOLDERS = {
    "# <Goal title>",
    "<Observable pass/fail condition>",
    "<Proportionate proof obligation>",
}


def visible_markdown(lines: list[str]) -> tuple[list[str], bool]:
    """Blank fenced-code content and report whether a fence remains open."""
    visible: list[str] = []
    fence: str | None = None
    for line in lines:
        stripped = line.lstrip()
        if fence is not None:
            visible.append("")
            if stripped.startswith(fence):
                fence = None
        elif stripped.startswith("```"):
            visible.append("")
            fence = "```"
        elif stripped.startswith("~~~"):
            visible.append("")
            fence = "~~~"
        else:
            visible.append(line)
    return visible, fence is not None


def meaningful(lines: list[str]) -> list[str]:
    return [line for line in lines if line.strip() and not line.lstrip().startswith("#")]


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"cannot read UTF-8 goal file: {exc}"]

    if path.name != "goal.md":
        errors.append("file must be named goal.md")
    if not text.endswith("\n"):
        errors.append("file must end with a newline")

    lines = text.splitlines()
    if not lines:
        return errors + ["file is empty"]

    visible, unclosed_fence = visible_markdown(lines)
    if unclosed_fence:
        errors.append("fenced code block is not closed")

    if not re.fullmatch(r"# \S(?:.*\S)?", visible[0]) or visible[0] == "# <Goal title>":
        errors.append("first line must be a concrete, non-empty H1 goal title")
    if sum(line.startswith("# ") for line in visible) != 1:
        errors.append("file must contain exactly one H1")

    h2_lines = [line for line in visible if line.startswith("## ")]
    if h2_lines != H2_HEADINGS:
        errors.append("H2 headings must exactly match the to-goal/v1 names and order")

    positions: dict[str, int] = {}
    for heading in H2_HEADINGS:
        matches = [index for index, line in enumerate(visible) if line == heading]
        if len(matches) == 1:
            positions[heading] = matches[0]
        else:
            errors.append(f"heading must appear exactly once: {heading}")
    if len(positions) != len(H2_HEADINGS):
        return errors

    first_section = positions[H2_HEADINGS[0]]
    metadata = [line for line in visible[1:first_section] if line.strip()]
    if metadata != [SCHEMA_LINE, *CONTRACT_PREAMBLE]:
        errors.append(
            "metadata must contain exactly the to-goal/v1 schema line "
            "followed by the contract preamble"
        )
    ranges: dict[str, tuple[int, int]] = {}
    for index, heading in enumerate(H2_HEADINGS):
        start = positions[heading] + 1
        end = positions[H2_HEADINGS[index + 1]] if index + 1 < len(H2_HEADINGS) else len(lines)
        ranges[heading] = (start, end)
        if not meaningful(visible[start:end]):
            errors.append(f"{heading.removeprefix('## ')} must contain content")

    acceptance_start, acceptance_end = ranges["## Acceptance Criteria"]
    ac_entries: list[tuple[int, str, str]] = []
    acceptance_lines = [
        line.rstrip()
        for line in visible[acceptance_start:acceptance_end]
        if line.strip()
    ]
    for line in acceptance_lines:
        match = AC_RE.fullmatch(line)
        if not match:
            errors.append(f"invalid acceptance criterion: {line!r}")
            continue

        condition = match.group(2).strip()
        evidence = match.group(3).strip()
        if not condition or not evidence:
            errors.append(f"acceptance criterion must contain a condition and evidence: {line!r}")
            continue
        ac_entries.append((int(match.group(1)), condition, evidence))

    if not ac_entries:
        errors.append(
            "Acceptance Criteria must contain '- `AC-###` <condition>. **Evidence:** <proof>.' entries"
        )
    else:
        ids = [entry[0] for entry in ac_entries]
        if ids != list(range(1, len(ids) + 1)):
            errors.append("acceptance IDs must be unique and consecutive from AC-001")
    if any(placeholder in line for line in visible for placeholder in PLACEHOLDERS):
        errors.append("template placeholders remain")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate-goal.py <goal.md>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR {path}: {error}", file=sys.stderr)
        return 1

    print(f"PASS to-goal/v1 {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
