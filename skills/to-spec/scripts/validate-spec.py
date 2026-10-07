#!/usr/bin/env python3
"""Validate the structural envelope of a to-spec/v1 artifact."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SCHEMA_LINE = "- **Schema:** `to-spec/v1`"
CONTRACT_PREAMBLE = [
    "> This file is the contract guiding the work. Do not edit or commit it.",
    "> Pausing should be rare. If strong evidence shows the agreed requirements must change, the user",
    '> explicitly requests `update_goal(status="paused")`. Explain the',
    "> evidence and proposed revision, then stop; the user decides and resumes the goal.",
]
REQUIRED_HEADINGS = ["## Outcome", "## Acceptance Criteria"]
OPTIONAL_HEADINGS = {
    "## Context",
    "## Scope",
    "## Non-goals",
    "## Settled Decisions",
    "## Constraints and Dependencies",
}
AC_RE = re.compile(r"^- `AC-(\d{3})`\s+(\S.*)$")
PLACEHOLDERS = {
    "# <Spec title>",
    "<The intended result.>",
    "<Observable pass/fail condition.>",
    "<Observable pass/fail condition>",
    "<Proportionate proof obligation.>",
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
        return [f"cannot read UTF-8 spec file: {exc}"]

    if path.name != "spec.md":
        errors.append("file must be named spec.md")
    if not text.endswith("\n"):
        errors.append("file must end with a newline")

    lines = text.splitlines()
    if not lines:
        return errors + ["file is empty"]

    visible, unclosed_fence = visible_markdown(lines)
    if unclosed_fence:
        errors.append("fenced code block is not closed")

    if not re.fullmatch(r"# \S(?:.*\S)?", visible[0]) or visible[0] == "# <Spec title>":
        errors.append("first line must be a concrete, non-empty H1 spec title")
    if sum(line.startswith("# ") for line in visible) != 1:
        errors.append("file must contain exactly one H1")

    sections = [(index, line) for index, line in enumerate(visible) if line.startswith("## ")]
    headings = [heading for _, heading in sections]
    for heading in REQUIRED_HEADINGS:
        if headings.count(heading) != 1:
            errors.append(f"heading must appear exactly once: {heading}")
    if any(headings.count(heading) != 1 for heading in REQUIRED_HEADINGS):
        return errors

    if headings[0] != "## Outcome" or headings[-1] != "## Acceptance Criteria":
        errors.append("Outcome must be first and Acceptance Criteria last")
    for heading in dict.fromkeys(headings):
        if heading not in REQUIRED_HEADINGS and heading not in OPTIONAL_HEADINGS:
            errors.append(f"unsupported section: {heading}")
        elif heading in OPTIONAL_HEADINGS and headings.count(heading) != 1:
            errors.append(f"optional heading must appear at most once: {heading}")

    first_section = sections[0][0]
    metadata = [line for line in visible[1:first_section] if line.strip()]
    if metadata != [SCHEMA_LINE, *CONTRACT_PREAMBLE]:
        errors.append(
            "metadata must contain exactly the to-spec/v1 schema line "
            "followed by the contract preamble"
        )
    ranges: dict[str, tuple[int, int]] = {}
    for index, (position, heading) in enumerate(sections):
        start = position + 1
        end = sections[index + 1][0] if index + 1 < len(sections) else len(lines)
        ranges[heading] = (start, end)
        if not meaningful(visible[start:end]):
            errors.append(f"{heading.removeprefix('## ')} must contain content")

    acceptance_start, acceptance_end = ranges["## Acceptance Criteria"]
    ids: list[int] = []
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

        ids.append(int(match.group(1)))

    if not ids:
        errors.append(
            "Acceptance Criteria must contain '- `AC-###` <condition>.' entries"
        )
    elif ids != list(range(1, len(ids) + 1)):
        errors.append("acceptance IDs must be unique and consecutive from AC-001")
    if any(placeholder in line for line in visible for placeholder in PLACEHOLDERS):
        errors.append("template placeholders remain")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate-spec.py <spec.md>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR {path}: {error}", file=sys.stderr)
        return 1

    print(f"PASS to-spec/v1 {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
