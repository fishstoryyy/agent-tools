#!/usr/bin/env python3
"""Reconstruct the active, human-readable branch of an agent session.

Claude Code and oh-my-pi (OMP) JSONL sessions are detected automatically.
Ordinary tool chatter, meta records, abandoned rewind branches, and thinking
(by default) are omitted. Interactive questions and their answers are kept.

Usage:
    parse_session.py SESSION.jsonl [--cursor ID | --since N]
                                   [--format auto|claude|omp]
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
_CLAUDE_QUESTION_TOOL_NAMES = {"AskUserQuestion"}
_OMP_QUESTION_TOOL_NAMES = {"ask"}


def clean_user_text(text):
    """Return conversational Claude user text, or empty text for CLI noise."""
    if any(marker in text for marker in _META_MARKERS):
        return ""
    text = _DROP_WRAPPERS.sub("", text)
    text = _UNWRAP.sub("", text)
    text = _STRAY_TAGS.sub("", text)
    return text.strip()


def render_questions(questions, *, omp=False):
    """Render Claude or OMP interactive-question arguments."""
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
        recommended = item.get("recommended") if omp else None
        if isinstance(options, list):
            for number, option in enumerate(options, 1):
                if not isinstance(option, dict):
                    continue
                label = str(option.get("label") or "").strip()
                description = str(option.get("description") or "").strip()
                if not label:
                    continue
                if recommended == number - 1 and not label.endswith("(Recommended)"):
                    label += " (Recommended)"
                suffix = f" — {description}" if description else ""
                rendered.append(f"{number}. {label}{suffix}")

        if item.get("multiSelect") or item.get("multi"):
            rendered.append("(Multiple selections allowed.)")
        rendered.append("")

    return "\n".join(rendered).strip()


def render_claude_question_tool(block):
    """Render a Claude Code AskUserQuestion tool call."""
    tool_input = block.get("input") or {}
    return render_questions(tool_input.get("questions"))


def render_omp_question_tool(block):
    """Render an OMP ask tool call."""
    arguments = block.get("arguments")
    if not isinstance(arguments, dict):
        partial = block.get("partialArgs")
        if isinstance(partial, str):
            try:
                arguments = json.loads(partial)
            except json.JSONDecodeError:
                arguments = None
    if not isinstance(arguments, dict):
        return ""
    return render_questions(arguments.get("questions"), omp=True)


def render_claude_question_answers(obj, question_tool_ids):
    """Render an answer to AskUserQuestion when this record contains one."""
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


def render_content(content, include_thinking=False, question_format=None):
    """Join human-readable text, images, thinking, and question blocks."""
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""

    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text":
            text = block.get("text", "")
            if isinstance(text, str) and text.strip():
                parts.append(text)
        elif block_type == "image":
            parts.append("[Image attached]")
        elif block_type == "thinking" and include_thinking:
            thinking = block.get("thinking", "") or block.get("text", "")
            if isinstance(thinking, str) and thinking.strip():
                parts.append("[thinking] " + thinking)
        elif (
            block_type == "tool_use"
            and question_format == "claude"
            and block.get("name") in _CLAUDE_QUESTION_TOOL_NAMES
        ):
            question = render_claude_question_tool(block)
            if question:
                parts.append(question)
        elif (
            block_type == "toolCall"
            and question_format == "omp"
            and block.get("name") in _OMP_QUESTION_TOOL_NAMES
        ):
            question = render_omp_question_tool(block)
            if question:
                parts.append(question)
    return "\n".join(part for part in parts if part.strip()).strip()


def extract_claude_turn(obj, include_thinking, question_tool_ids):
    """Return (role label, text) for a Claude turn, or None."""
    if obj.get("type") not in ("user", "assistant") or obj.get("isMeta"):
        return None
    message = obj.get("message") or {}
    role = message.get("role")
    content = message.get("content")

    if role == "user":
        if isinstance(content, str):
            text = clean_user_text(content)
        elif isinstance(content, list):
            parts = [render_content(content)]
            parts.append(render_claude_question_answers(obj, question_tool_ids))
            text = "\n".join(part for part in parts if part).strip()
        else:
            text = ""
        label = "You"
    elif role == "assistant":
        text = render_content(
            content,
            include_thinking=include_thinking,
            question_format="claude",
        )
        label = "Agent"
    else:
        return None

    if not text:
        return None
    if obj.get("isSidechain"):
        label = f"[subagent] {label}"
    return label, text


def render_omp_ask_answers(message):
    """Render a persisted OMP ask result, preferring its canonical text."""
    text = render_content(message.get("content"))
    if text:
        return text

    details = message.get("details") or {}
    results = details.get("results")
    if not isinstance(results, list):
        results = [details] if details else []

    lines = []
    for result in results:
        if not isinstance(result, dict):
            continue
        question = str(result.get("question") or result.get("id") or "Question")
        custom = result.get("customInput")
        selected = result.get("selectedOptions")
        if custom is not None:
            answer = str(custom)
        elif isinstance(selected, list) and selected:
            answer = ", ".join(str(value) for value in selected)
        else:
            answer = "(cancelled)"
        if result.get("timedOut"):
            answer += " (auto-selected after timeout)"
        note = result.get("note")
        if note:
            answer += f" (note: {note})"
        lines.append(f"{question} → {answer}")
    return "\n".join(lines).strip()


def render_file_mentions(message):
    """Render user-mentioned file identities without replaying file contents."""
    files = message.get("files")
    if not isinstance(files, list):
        return ""
    lines = []
    for item in files:
        if not isinstance(item, dict):
            continue
        path = str(item.get("path") or "").strip()
        if not path:
            continue
        suffix = " [image]" if item.get("image") else ""
        lines.append(f"- {path}{suffix}")
    return "Files mentioned:\n" + "\n".join(lines) if lines else ""


def extract_omp_turn(obj, include_thinking, question_tool_ids):
    """Return (role label, text) for an OMP turn or context record."""
    entry_type = obj.get("type")

    if entry_type == "custom_message":
        if not obj.get("display"):
            return None
        text = render_content(obj.get("content"))
        if not text:
            return None
        custom_type = str(obj.get("customType") or "custom message")
        attribution = obj.get("attribution")
        suffix = " (user-invoked)" if attribution == "user" else ""
        return f"Context — {custom_type}{suffix}", text

    if entry_type == "branch_summary":
        summary = str(obj.get("summary") or "").strip()
        return ("Context — branch summary", summary) if summary else None

    if entry_type == "compaction":
        summary = str(obj.get("summary") or "").strip()
        if not summary:
            return None
        tokens = obj.get("tokensBefore")
        prefix = f"({tokens} tokens before compaction)\n" if tokens is not None else ""
        return "Context — compaction", prefix + summary

    if entry_type != "message":
        return None

    message = obj.get("message") or {}
    role = message.get("role")
    content = message.get("content")
    if role == "user":
        text = render_content(content)
        label = "You"
    elif role == "assistant":
        text = render_content(
            content,
            include_thinking=include_thinking,
            question_format="omp",
        )
        label = "Agent"
    elif role == "toolResult":
        tool_call_id = message.get("toolCallId")
        if (
            message.get("toolName") not in _OMP_QUESTION_TOOL_NAMES
            and tool_call_id not in question_tool_ids
        ):
            return None
        text = render_omp_ask_answers(message)
        label = "You [answer]"
    elif role in ("custom", "hookMessage"):
        if not message.get("display"):
            return None
        text = render_content(content)
        custom_type = str(message.get("customType") or role)
        label = f"Context — {custom_type}"
    elif role == "branchSummary":
        text = str(message.get("summary") or "").strip()
        label = "Context — branch summary"
    elif role == "compactionSummary":
        text = str(message.get("summary") or "").strip()
        label = "Context — compaction"
    elif role == "fileMention":
        text = render_file_mentions(message)
        label = "You [files]"
    else:
        return None

    return (label, text) if text else None


def active_claude_ids(objects):
    """Return UUIDs on the current Claude main-thread branch."""
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
    if latest_marker_position > latest_node_position and latest_marker in nodes:
        # Claude integrations may append this cursor after a rewind without a
        # new dialogue record. It is then the only persisted active-leaf signal.
        leaf = latest_marker

    active = set()
    while leaf and leaf not in active:
        active.add(leaf)
        node = nodes.get(leaf)
        if not node:
            break
        leaf = node.get("parentUuid")
    return active


def belongs_to_active_claude_sidechain(obj, all_nodes, active_ids):
    """Whether a Claude sidechain ultimately attaches to the active branch."""
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


def select_active_claude_objects(objects, include_sidechains):
    """Select Claude active-branch records, optionally retaining sidechains."""
    active_ids = active_claude_ids(objects)
    if not active_ids:
        return [
            obj for obj in objects
            if include_sidechains or not obj.get("isSidechain")
        ]

    all_nodes = {obj["uuid"]: obj for obj in objects if obj.get("uuid")}
    selected = []
    for obj in objects:
        node_uuid = obj.get("uuid")
        if node_uuid in active_ids:
            selected.append(obj)
        elif (
            include_sidechains
            and obj.get("isSidechain")
            and belongs_to_active_claude_sidechain(obj, all_nodes, active_ids)
        ):
            selected.append(obj)
    return selected


def select_active_omp_objects(objects):
    """Reproduce OMP's getBranch(): walk parentId from the last entry."""
    entries = [
        obj for obj in objects
        if obj.get("type") not in ("session", "title")
    ]
    nodes = {obj["id"]: obj for obj in entries if obj.get("id")}
    if not nodes:
        # OMP v1 sessions were linear and had no id/parentId fields.
        return entries

    leaf = next((obj for obj in reversed(entries) if obj.get("id")), None)
    if leaf is None:
        return entries

    path = []
    seen = set()
    current = leaf
    while current and current.get("id") not in seen:
        node_id = current.get("id")
        seen.add(node_id)
        path.append(current)
        parent_id = current.get("parentId")
        current = nodes.get(parent_id) if parent_id else None
    path.reverse()
    return path


def load_objects(session_path):
    """Load complete JSON records, tolerating a live truncated final line."""
    try:
        with open(session_path, "r", encoding="utf-8") as session_file:
            raw_lines = session_file.readlines()
    except OSError as error:
        print(f"ERROR: cannot open session file: {error}", file=sys.stderr)
        return None

    objects = []
    for line_number, line in enumerate(raw_lines, 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        obj["_parser_line"] = line_number
        objects.append(obj)
    return objects


def detect_format(objects):
    """Detect OMP's message-entry schema; otherwise use Claude's schema."""
    for obj in objects:
        message = obj.get("message")
        if (
            obj.get("type") == "message"
            and isinstance(message, dict)
            and message.get("role")
        ):
            return "omp"
    return "claude"


def record_id(obj, session_format):
    """Return a stable cursor for a persisted turn, including legacy files."""
    key = "id" if session_format == "omp" else "uuid"
    value = obj.get(key)
    if value:
        return str(value)
    return f"line:{obj.get('_parser_line', '')}"


def collect_question_tool_ids(objects, session_format):
    """Collect interactive tool-call IDs so only their results become turns."""
    ids = set()
    for obj in objects:
        content = (obj.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if session_format == "claude":
                is_question = (
                    block.get("type") == "tool_use"
                    and block.get("name") in _CLAUDE_QUESTION_TOOL_NAMES
                )
            else:
                is_question = (
                    block.get("type") == "toolCall"
                    and block.get("name") in _OMP_QUESTION_TOOL_NAMES
                )
            if is_question and block.get("id"):
                ids.add(block["id"])
    return ids


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
        "--format",
        choices=("auto", "claude", "omp"),
        default="auto",
        help="Session format override (default: auto-detect)",
    )
    parser.add_argument(
        "--include-thinking",
        action="store_true",
        help="Include persisted assistant thinking blocks",
    )
    parser.add_argument(
        "--include-sidechains",
        action="store_true",
        help="Include Claude subagent turns attached to the active branch",
    )
    args = parser.parse_args()
    if args.since is not None and args.since < 0:
        parser.error("--since must be zero or greater")

    objects = load_objects(args.session)
    if objects is None:
        return 2
    session_format = detect_format(objects) if args.format == "auto" else args.format

    if session_format == "omp":
        active_objects = select_active_omp_objects(objects)
        extractor = extract_omp_turn
    else:
        active_objects = select_active_claude_objects(
            objects,
            args.include_sidechains,
        )
        extractor = extract_claude_turn

    question_tool_ids = collect_question_tool_ids(active_objects, session_format)
    turns = []
    for obj in active_objects:
        turn = extractor(obj, args.include_thinking, question_tool_ids)
        if turn is None:
            continue
        label, turn_text = turn
        turns.append(
            (
                len(turns) + 1,
                label,
                obj.get("timestamp", ""),
                turn_text,
                record_id(obj, session_format),
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
                timestamp = str(timestamp).replace("T", " ").replace("Z", "")[:19]
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
