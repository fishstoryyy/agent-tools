#!/usr/bin/env python3
"""Validate the structural envelope of a goal/v1 contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SCHEMA_LINE = "- **Schema:** `goal/v1`"
STARTING_COMMIT_RE = re.compile(
    r"^- \*\*Starting commit:\*\* `(?:[0-9a-f]{40}|[0-9a-f]{64})`$"
)
H2_HEADINGS = [
    "## Desired Outcome",
    "## Scope",
    "## Settled Decisions and Constraints",
    "## Acceptance Criteria",
    "## Unresolved Unknowns",
    "## Implementation Notes",
]
SCOPE_HEADINGS = ["### In scope", "### Non-goals"]
AC_RE = re.compile(r"^\s*(?:(?:[-*+]|\d+\.)\s+|\|\s*)?`AC-(\d{3})`(?:\s|\||$)")
IN_RE = re.compile(r"^- `IN-(\d{3})`(?:\s|$)")
IN_FIELDS = [
    "**Affected decision:**",
    "**Why unavoidable:**",
    "**Alternatives attempted or ruled out:**",
    "**Minimal deviation:**",
    "**Protected terms:**",
    "**Verification evidence:**",
]
PLACEHOLDERS = {
    "# <Change Title>",
    "<What should become true and why the current state is insufficient.>",
    "<Included outcomes, behaviors, surfaces, or change boundaries.>",
    "<Explicitly excluded outcomes or boundaries.>",
    "<Only decisions, rationale, and constraints that materially bound an acceptable solution.>",
}


def meaningful(lines: list[str]) -> list[str]:
    return [line for line in lines if line.strip() and not line.lstrip().startswith("#")]


def markdown_mask(lines: list[str]) -> tuple[list[bool], bool]:
    """Mark lines outside fenced code blocks and report an unclosed fence."""
    visible: list[bool] = []
    fence: str | None = None
    for line in lines:
        stripped = line.lstrip()
        if fence is not None:
            visible.append(False)
            if stripped.startswith(fence):
                fence = None
        elif stripped.startswith("```"):
            visible.append(False)
            fence = "```"
        elif stripped.startswith("~~~"):
            visible.append(False)
            fence = "~~~"
        else:
            visible.append(True)
    return visible, fence is not None


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

    visible_mask, unclosed_fence = markdown_mask(lines)
    visible_lines = [line if is_visible else "" for line, is_visible in zip(lines, visible_mask)]
    if unclosed_fence:
        errors.append("fenced code block is not closed")

    if not re.fullmatch(r"# \S(?:.*\S)?", visible_lines[0]) or lines[0] == "# <Change Title>":
        errors.append("first line must be a concrete, non-empty H1 change title")
    if sum(line.startswith("# ") for line in visible_lines) != 1:
        errors.append("file must contain exactly one H1")

    h2_lines = [line for line in visible_lines if line.startswith("## ")]
    if h2_lines != H2_HEADINGS:
        errors.append("H2 headings must exactly match the goal/v1 names and order")

    positions: dict[str, int] = {}
    for heading in [*H2_HEADINGS, *SCOPE_HEADINGS]:
        matches = [index for index, line in enumerate(visible_lines) if line == heading]
        if len(matches) == 1:
            positions[heading] = matches[0]
        else:
            errors.append(f"heading must appear exactly once: {heading}")

    if len(positions) != len(H2_HEADINGS) + len(SCOPE_HEADINGS):
        return errors

    first_section = positions[H2_HEADINGS[0]]
    metadata = visible_lines[1:first_section]
    schema_matches = [index for index, line in enumerate(metadata) if line == SCHEMA_LINE]
    starting_matches = [index for index, line in enumerate(metadata) if STARTING_COMMIT_RE.fullmatch(line)]
    execution_matches = [index for index, line in enumerate(metadata) if line.startswith("> **Execution:**")]
    if len(schema_matches) != 1:
        errors.append(f"metadata must contain exactly one {SCHEMA_LINE!r}")
    if len(starting_matches) != 1:
        errors.append("metadata must contain exactly one full lowercase starting commit SHA")
    if len(execution_matches) != 1:
        errors.append("metadata must contain exactly one '> **Execution:**' notice")
    if schema_matches and starting_matches and execution_matches:
        if not schema_matches[0] < starting_matches[0] < execution_matches[0]:
            errors.append("schema, starting commit, and execution notice must appear in that order")

    if not (
        positions["## Scope"]
        < positions["### In scope"]
        < positions["### Non-goals"]
        < positions["## Settled Decisions and Constraints"]
    ):
        errors.append("Scope must contain In scope followed by Non-goals")

    ranges = {
        "Desired Outcome": (
            positions["## Desired Outcome"] + 1,
            positions["## Scope"],
        ),
        "In scope": (
            positions["### In scope"] + 1,
            positions["### Non-goals"],
        ),
        "Non-goals": (
            positions["### Non-goals"] + 1,
            positions["## Settled Decisions and Constraints"],
        ),
        "Settled Decisions and Constraints": (
            positions["## Settled Decisions and Constraints"] + 1,
            positions["## Acceptance Criteria"],
        ),
        "Acceptance Criteria": (
            positions["## Acceptance Criteria"] + 1,
            positions["## Unresolved Unknowns"],
        ),
        "Unresolved Unknowns": (
            positions["## Unresolved Unknowns"] + 1,
            positions["## Implementation Notes"],
        ),
        "Implementation Notes": (
            positions["## Implementation Notes"] + 1,
            len(lines),
        ),
    }
    for name, (start, end) in ranges.items():
        if not meaningful(lines[start:end]):
            errors.append(f"{name} must contain content")

    acceptance_start, acceptance_end = ranges["Acceptance Criteria"]
    ac_ids = [
        int(match.group(1))
        for line in visible_lines[acceptance_start:acceptance_end]
        if (match := AC_RE.match(line))
    ]
    if not ac_ids:
        errors.append("Acceptance Criteria must contain at least one AC-### entry")
    elif ac_ids != list(range(1, len(ac_ids) + 1)):
        errors.append("acceptance IDs must be unique and consecutive from AC-001")

    unknown_start, unknown_end = ranges["Unresolved Unknowns"]
    unknown_content = meaningful(visible_lines[unknown_start:unknown_end])
    if "- None." in unknown_content and unknown_content != ["- None."]:
        errors.append("'- None.' must be the only Unresolved Unknowns content when used")

    notes_start, notes_end = ranges["Implementation Notes"]
    notes = lines[notes_start:notes_end]
    visible_notes = visible_lines[notes_start:notes_end]
    none_positions = [index for index, line in enumerate(visible_notes) if line == "- None."]
    note_entries = [
        (index, int(match.group(1)))
        for index, line in enumerate(visible_notes)
        if (match := IN_RE.fullmatch(line))
    ]
    if none_positions and note_entries:
        errors.append("Implementation Notes cannot contain both '- None.' and IN-### records")
    elif len(none_positions) > 1:
        errors.append("Implementation Notes may contain only one '- None.' marker")
    elif not none_positions and not note_entries:
        errors.append("Implementation Notes must contain '- None.' or IN-### records")

    if note_entries:
        note_ids = [note_id for _, note_id in note_entries]
        if note_ids != list(range(1, len(note_ids) + 1)):
            errors.append("implementation-note IDs must be unique and consecutive from IN-001")
        for entry_index, (start, note_id) in enumerate(note_entries):
            end = note_entries[entry_index + 1][0] if entry_index + 1 < len(note_entries) else len(notes)
            block = "\n".join(visible_notes[start:end])
            missing = [field for field in IN_FIELDS if field not in block]
            if missing:
                errors.append(f"IN-{note_id:03d} is missing fields: {missing!r}")

    remaining_placeholders = sorted(
        placeholder for placeholder in PLACEHOLDERS if placeholder in visible_lines
    )
    if remaining_placeholders:
        errors.append(f"template placeholders remain: {remaining_placeholders!r}")

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

    print(f"PASS goal/v1 {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
