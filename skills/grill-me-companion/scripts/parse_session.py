#!/usr/bin/env python3
"""Reconstruct the active, human-readable branch of a Claude Code session.

Tool chatter, meta records, abandoned rewind branches, and thinking (by default)
are omitted. AskUserQuestion prompts and their answers are preserved.

Usage:
    parse_session.py SESSION.jsonl [--cursor UUID | --since N]
                                   [--include-thinking]
                                   [--include-sidechains]

Use the emitted CURSOR value on the next refresh. If that cursor is no longer
on the active branch, the parser emits BRANCH_RESET=1 and reprints the active
transcript so the caller can discard the abandoned continuation.

The final stdout line is always: TURNS_TOTAL=<int>
"""

import argparse
import json
import re
import sys


_META_MARKERS = ("<local-command-stdout>", "<local-command-caveat>")
_DROP_WRAPPERS = re.compile(
    r"<(command-name|command-message)>.*?</\1>", re.DOTALL
)
_UNWRAP = re.compile(r"</?(command-args|command-contents)>")
_STRAY_TAGS = re.compile(r"</?(command-[a-z-]+|local-command-[a-z-]+)>")
_QUESTION_TOOL_NAMES = {"AskUserQuestion"}


def clean_user_text(text):
    """Return conversational user text, or an empty string for CLI noise."""
    if any(marker in text for marker in _META_MARKERS):
        return ""
    text = _DROP_WRAPPERS.sub("", text)
    text = _UNWRAP.sub("", text)
    text = _STRAY_TAGS.sub("", text)
    return text.strip()


def render_question_tool(block):
    """Render a Claude Code AskUserQuestion tool call as readable dialogue."""
    tool_input = block.get("input") or {}
    questions = tool_input.get("questions")
    if not isinstance(questions, list):
        return ""

    rendered = []
    for item in questions:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question") or "").strip()
        if not question:
            continue
        header = str(item.get("header") or "").strip()
        rendered.append(f"Question — {header}" if header else "Question")
        rendered.append(question)

        options = item.get("options")
        if isinstance(options, list):
            for number, option in enumerate(options, 1):
                if not isinstance(option, dict):
                    continue
                label = str(option.get("label") or "").strip()
                description = str(option.get("description") or "").strip()
                if not label:
                    continue
                suffix = f" — {description}" if description else ""
                rendered.append(f"{number}. {label}{suffix}")

        if item.get("multiSelect"):
            rendered.append("(Multiple selections allowed.)")

    return "\n".join(rendered).strip()


def render_question_answers(obj, question_tool_ids):
    """Render the user's answer to AskUserQuestion, if this record contains it."""
    result = obj.get("toolUseResult")
    if isinstance(result, dict) and isinstance(result.get("answers"), dict):
        lines = []
        for question, answer in result["answers"].items():
            question_text = str(question).strip()
            if isinstance(answer, list):
                answer_text = ", ".join(str(value) for value in answer)
            else:
                answer_text = str(answer).strip()
            if question_text and answer_text:
                lines.append(f"{question_text} → {answer_text}")
        if lines:
            return "\n".join(lines)

    content = (obj.get("message") or {}).get("content")
    if not isinstance(content, list):
        return ""
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_result":
            continue
        if block.get("tool_use_id") not in question_tool_ids:
            continue
        value = block.get("content")
        if isinstance(value, str):
            return value.strip()
    return ""


def blocks_text(content, include_thinking, include_questions=False):
    """Join human-readable blocks from a list-form message."""
    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text":
            text = block.get("text", "")
            if isinstance(text, str):
                parts.append(text)
        elif block_type == "thinking" and include_thinking:
            thinking = block.get("thinking", "") or block.get("text", "")
            if isinstance(thinking, str) and thinking.strip():
                parts.append("[thinking] " + thinking)
        elif (
            block_type == "tool_use"
            and include_questions
            and block.get("name") in _QUESTION_TOOL_NAMES
        ):
            parts.append(render_question_tool(block))
    return "\n".join(part for part in parts if part.strip()).strip()


def extract_turn(obj, include_thinking, question_tool_ids):
    """Return (role label, text) for a conversational turn, or None."""
    if obj.get("type") not in ("user", "assistant") or obj.get("isMeta"):
        return None
    message = obj.get("message") or {}
    role = message.get("role")
    content = message.get("content")

    if role == "user":
        if isinstance(content, str):
            text = clean_user_text(content)
        elif isinstance(content, list):
            parts = [blocks_text(content, include_thinking=False)]
            parts.append(render_question_answers(obj, question_tool_ids))
            text = "\n".join(part for part in parts if part).strip()
        else:
            text = ""
        label = "You"
    elif role == "assistant":
        if isinstance(content, list):
            text = blocks_text(
                content,
                include_thinking,
                include_questions=True,
            )
        elif isinstance(content, str):
            text = content.strip()
        else:
            text = ""
        label = "Agent"
    else:
        return None

    if not text:
        return None
    if obj.get("isSidechain"):
        label = f"[subagent] {label}"
    return label, text


def active_main_ids(objects):
    """Return UUIDs on the current main-thread branch."""
    nodes = {}
    latest_node = None
    latest_node_position = -1
    latest_marker = None
    latest_marker_position = -1

    for position, obj in enumerate(objects):
        if obj.get("isSidechain"):
            continue
        node_uuid = obj.get("uuid")
        if node_uuid:
            nodes[node_uuid] = obj
            latest_node = node_uuid
            latest_node_position = position
        if obj.get("type") == "last-prompt" and obj.get("leafUuid"):
            latest_marker = obj.get("leafUuid")
            latest_marker_position = position

    if not latest_node:
        return set()

    leaf = latest_node
    if (
        latest_marker_position > latest_node_position
        and latest_marker in nodes
    ):
        # Orca/Claude may append this cursor after a rewind without adding a new
        # dialogue record. In that case it is the only persisted active-leaf signal.
        leaf = latest_marker

    active = set()
    while leaf and leaf not in active:
        active.add(leaf)
        node = nodes.get(leaf)
        if not node:
            break
        leaf = node.get("parentUuid")
    return active


def belongs_to_active_sidechain(obj, all_nodes, active_ids):
    """Whether a sidechain node ultimately attaches to the active main branch."""
    node_uuid = obj.get("uuid")
    seen = set()
    while node_uuid and node_uuid not in seen:
        if node_uuid in active_ids:
            return True
        seen.add(node_uuid)
        node = all_nodes.get(node_uuid)
        if not node:
            return False
        node_uuid = node.get("parentUuid")
    return False


def select_active_objects(objects, include_sidechains):
    """Filter raw records to the active branch, optionally retaining sidechains."""
    active_ids = active_main_ids(objects)
    if not active_ids:
        return [
            obj for obj in objects
            if include_sidechains or not obj.get("isSidechain")
        ]

    all_nodes = {
        obj["uuid"]: obj
        for obj in objects
        if obj.get("uuid")
    }
    selected = []
    for obj in objects:
        node_uuid = obj.get("uuid")
        if node_uuid in active_ids:
            selected.append(obj)
        elif (
            include_sidechains
            and obj.get("isSidechain")
            and belongs_to_active_sidechain(obj, all_nodes, active_ids)
        ):
            selected.append(obj)
    return selected


def load_objects(session_path):
    """Load complete JSON records, tolerating a live truncated final line."""
    try:
        with open(session_path, "r", encoding="utf-8") as session_file:
            raw_lines = session_file.readlines()
    except OSError as error:
        print(f"ERROR: cannot open session file: {error}", file=sys.stderr)
        return None

    objects = []
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        try:
            objects.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return objects


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("session", help="Path to the session .jsonl file")
    refresh_group = parser.add_mutually_exclusive_group()
    refresh_group.add_argument(
        "--cursor",
        help="Last CURSOR emitted; detects rewinds and branch replacement",
    )
    refresh_group.add_argument(
        "--since",
        type=int,
        help="Legacy turn-count refresh (not fully rewind-safe)",
    )
    parser.add_argument(
        "--include-thinking",
        action="store_true",
        help="Include persisted assistant thinking blocks",
    )
    parser.add_argument(
        "--include-sidechains",
        action="store_true",
        help="Include subagent (Task) turns attached to the active branch",
    )
    args = parser.parse_args()
    if args.since is not None and args.since < 0:
        parser.error("--since must be zero or greater")

    objects = load_objects(args.session)
    if objects is None:
        return 2
    active_objects = select_active_objects(objects, args.include_sidechains)

    question_tool_ids = set()
    for obj in active_objects:
        content = (obj.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") in _QUESTION_TOOL_NAMES
                and block.get("id")
            ):
                question_tool_ids.add(block["id"])

    turns = []
    for obj in active_objects:
        turn = extract_turn(obj, args.include_thinking, question_tool_ids)
        if turn is None:
            continue
        label, turn_text = turn
        turns.append(
            (
                len(turns) + 1,
                label,
                obj.get("timestamp", ""),
                turn_text,
                obj.get("uuid", ""),
            )
        )

    branch_reset = False
    if args.cursor:
        cursor_positions = [
            index for index, turn in enumerate(turns) if turn[4] == args.cursor
        ]
        if cursor_positions:
            shown = turns[cursor_positions[-1] + 1:]
        else:
            branch_reset = True
            shown = turns
    elif args.since is not None:
        if args.since > len(turns):
            branch_reset = True
            shown = turns
        else:
            shown = turns[args.since:]
    else:
        shown = turns

    if branch_reset:
        print("(active branch changed; full active transcript follows)")
    if not branch_reset and (args.cursor or args.since is not None) and not shown:
        print("(no new persisted turns on the active branch)")
    else:
        for index, label, timestamp, turn_text, _ in shown:
            if timestamp:
                timestamp = timestamp.replace("T", " ").replace("Z", "")[:19]
            header = f"[{index}] {label}" + (
                f"  {timestamp}" if timestamp else ""
            )
            print(header)
            print(turn_text)
            print()

    cursor = turns[-1][4] if turns else ""
    print(f"BRANCH_RESET={int(branch_reset)}")
    print(f"CURSOR={cursor}")
    print(f"TURNS_TOTAL={len(turns)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
