#!/usr/bin/env python3
"""Reconstruct the active human-readable branch of a Claude Code session.

Ordinary tool chatter, meta records, abandoned rewind branches, and thinking
(by default) are omitted. Interactive questions, recorded answers, text, and
image placeholders are preserved.

Usage:
    parse_session.py SESSION.jsonl [--since CURSOR] [--include-thinking]
                                   [--include-sidechains]

    --since CURSOR       Show active turns after the prior CURSOR. UUID cursors
                         detect rewinds; a plain turn number also works.
    --cursor CURSOR      Alias for --since.
    --include-thinking   Include persisted assistant thinking blocks.
    --include-sidechains Include embedded subagent turns attached to the active
                         branch. Separate subagent files are not loaded.

The final three stdout lines are always:
    BRANCH_RESET=0|1     whether prior branch state must be discarded
    TURNS_TOTAL=<int>    visible turns on the active branch
    CURSOR=<id>          pass back as --since on the next refresh

When an abandoned cursor still has a traceable active ancestor, a rewind prints
only the current turns after that divergence. If ancestry cannot be recovered,
the full active transcript is printed instead.
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
    """Return conversational user text, or empty text for CLI/system noise."""
    if any(marker in text for marker in _META_MARKERS):
        return ""
    text = _DROP_WRAPPERS.sub("", text)
    text = _UNWRAP.sub("", text)
    text = _STRAY_TAGS.sub("", text)
    return text.strip()


def render_questions(questions):
    """Render Claude Code AskUserQuestion arguments as readable dialogue."""
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
        rendered.append("")

    return "\n".join(rendered).strip()


def _tool_result_text(content):
    """Flatten a tool result's string or list of text blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def indent_note(note):
    """Normalize newlines so a multi-line note stays readable under its answer."""
    normalized = note.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.replace("\n", "\n  ")


def render_question_answers(obj, question_tool_ids):
    """Render a persisted answer to AskUserQuestion, without other results."""
    result = obj.get("toolUseResult")
    if isinstance(result, dict) and isinstance(result.get("answers"), dict):
        annotations = result.get("annotations")
        if not isinstance(annotations, dict):
            annotations = {}
        lines = []
        for question, answer in result["answers"].items():
            question_text = str(question).strip()
            if isinstance(answer, list):
                answer_text = ", ".join(str(value) for value in answer)
            else:
                answer_text = str(answer).strip()
            # Free-text the user typed instead of, or alongside, an option:
            # the answer itself can be a placeholder like "(notes only)".
            annotation = annotations.get(question)
            note = ""
            if isinstance(annotation, dict):
                note = str(annotation.get("notes") or "").strip()
            if not question_text or not (answer_text or note):
                continue
            lines.append(f"{question_text} → {answer_text}".rstrip())
            if note:
                lines.append(f"  notes: {indent_note(note)}")
        if lines:
            return "\n".join(lines)

    content = (obj.get("message") or {}).get("content")
    if not isinstance(content, list):
        return ""
    answers = []
    for block in content:
        if not isinstance(block, dict) or block.get("type") != "tool_result":
            continue
        if block.get("is_error") or block.get("tool_use_id") not in question_tool_ids:
            continue
        answer = _tool_result_text(block.get("content")).strip()
        if answer and "<tool_use_error>" not in answer:
            answers.append(answer)
    return "\n".join(answers)


def render_content(
        content, *, include_thinking=False, include_questions=False,
        clean_user=False):
    """Join readable text, images, thinking, and interactive questions."""
    if isinstance(content, str):
        return clean_user_text(content) if clean_user else content.strip()
    if not isinstance(content, list):
        return ""

    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text":
            text = block.get("text", "")
            if isinstance(text, str):
                text = clean_user_text(text) if clean_user else text.strip()
                if text:
                    parts.append(text)
        elif block_type == "image":
            parts.append("[Image attached]")
        elif block_type == "thinking" and include_thinking:
            thinking = block.get("thinking", "") or block.get("text", "")
            if isinstance(thinking, str) and thinking.strip():
                parts.append("[thinking] " + thinking)
        elif (
            block_type == "tool_use"
            and include_questions
            and block.get("name") in _QUESTION_TOOL_NAMES
        ):
            question = render_questions((block.get("input") or {}).get("questions"))
            if question:
                parts.append(question)
    return "\n".join(part for part in parts if part.strip()).strip()


def extract_turn(obj, include_thinking, question_tool_ids):
    """Return (role label, text) for a readable turn, or None."""
    if obj.get("type") not in ("user", "assistant") or obj.get("isMeta"):
        return None
    message = obj.get("message") or {}
    role = message.get("role")
    content = message.get("content")

    if role == "user":
        text = render_content(content, clean_user=True)
        answers = render_question_answers(obj, question_tool_ids)
        text = "\n".join(part for part in (text, answers) if part).strip()
        label = "You"
    elif role == "assistant":
        text = render_content(
            content,
            include_thinking=include_thinking,
            include_questions=True,
        )
        label = "Agent"
    else:
        return None

    if not text:
        return None
    if obj.get("isSidechain"):
        label = f"[subagent] {label}"
    return label, text


def load_objects(session_path):
    """Load complete JSON objects, tolerating a live truncated final line."""
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


def collect_question_tool_ids(objects):
    """Collect question tool IDs so only their results become user turns."""
    ids = set()
    for obj in objects:
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
                ids.add(block["id"])
    return ids


def active_branch_uuids(objects, by_uuid):
    """Return UUIDs on the live main-thread branch, or None if untraceable."""
    latest_node = None
    latest_node_position = -1
    latest_marker = None
    latest_marker_position = -1

    for position, obj in enumerate(objects):
        if obj.get("isSidechain"):
            continue
        node_uuid = obj.get("uuid")
        if node_uuid:
            latest_node = node_uuid
            latest_node_position = position
        if obj.get("type") == "last-prompt" and obj.get("leafUuid"):
            latest_marker = obj["leafUuid"]
            latest_marker_position = position

    if latest_node is None:
        return None
    leaf = latest_node
    if latest_marker_position > latest_node_position and latest_marker in by_uuid:
        leaf = latest_marker

    active = set()
    current = leaf
    while current and current in by_uuid and current not in active:
        active.add(current)
        current = by_uuid[current].get("parentUuid")
    return active


def belongs_to_active_sidechain(obj, by_uuid, active):
    """Whether an embedded sidechain ultimately attaches to the active branch."""
    current = obj.get("uuid")
    seen = set()
    while current and current not in seen:
        if current in active:
            return True
        seen.add(current)
        node = by_uuid.get(current)
        if node is None:
            return False
        current = node.get("parentUuid")
    return False


def select_active_objects(objects, by_uuid, active, include_sidechains):
    """Select active records, optionally including attached sidechain records."""
    if active is None:
        return [
            obj for obj in objects
            if include_sidechains or not obj.get("isSidechain")
        ]

    selected = []
    for obj in objects:
        node_uuid = obj.get("uuid")
        if node_uuid in active:
            selected.append(obj)
        elif (
            include_sidechains
            and obj.get("isSidechain")
            and belongs_to_active_sidechain(obj, by_uuid, active)
        ):
            selected.append(obj)
    return selected


def root_of(node_uuid, by_uuid):
    """Return the root UUID, or None when a parent chain is broken."""
    seen = set()
    current = node_uuid
    while current in by_uuid and current not in seen:
        parent = by_uuid[current].get("parentUuid")
        if parent is None:
            return current
        seen.add(current)
        current = parent
    return None


def record_id(obj):
    """Return a stable cursor for a visible record, including legacy files."""
    if obj.get("uuid"):
        return str(obj["uuid"])
    return f"line:{obj.get('_parser_line', '')}"


def warn_about_branch_gaps(
        objects, by_uuid, active, include_thinking, question_tool_ids):
    """Warn when branch tracing may hide context for non-rewind reasons."""
    if active is None:
        print("WARN: could not trace the active branch; showing all turns",
              file=sys.stderr)
        return

    roots = [
        node_uuid for node_uuid in active
        if node_uuid in by_uuid and by_uuid[node_uuid].get("parentUuid") is None
    ]
    if not roots:
        print("WARN: live branch does not reach the session root; "
              "earlier turns may be missing from this transcript",
              file=sys.stderr)
        return

    live_root = roots[0]
    other_turns = sum(
        1 for obj in objects
        if obj.get("type") in ("user", "assistant")
        and not obj.get("isMeta")
        and not obj.get("isSidechain")
        and obj.get("uuid")
        and obj["uuid"] not in active
        and root_of(obj["uuid"], by_uuid) != live_root
        and extract_turn(obj, include_thinking, question_tool_ids)
    )
    if other_turns:
        print(
            f"WARN: {other_turns} turn(s) from a separate thread in this "
            "file (different root) are not shown",
            file=sys.stderr,
        )


def build_turns(active_objects, include_thinking, question_tool_ids):
    """Return (visible turns, uuid -> position) for the selected records."""
    turns = []
    active_rank = {}
    for position, obj in enumerate(active_objects):
        if obj.get("uuid"):
            active_rank[obj["uuid"]] = position
        turn = extract_turn(obj, include_thinking, question_tool_ids)
        if turn is None:
            continue
        label, text = turn
        turns.append((
            len(turns) + 1,
            label,
            obj.get("timestamp", ""),
            text,
            record_id(obj),
            position,
        ))
    return turns, active_rank


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("session", help="Path to the session .jsonl file")
    parser.add_argument(
        "--since", "--cursor", dest="since", default=None, metavar="CURSOR",
        help="Show active turns after CURSOR (a UUID or plain turn number)",
    )
    parser.add_argument(
        "--include-thinking",
        action="store_true",
        help="Include persisted assistant thinking blocks",
    )
    parser.add_argument(
        "--include-sidechains",
        action="store_true",
        help="Include embedded subagent turns attached to the active branch",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    objects = load_objects(args.session)
    if objects is None:
        return 2

    by_uuid = {obj["uuid"]: obj for obj in objects if obj.get("uuid")}
    question_tool_ids = collect_question_tool_ids(objects)
    active = active_branch_uuids(objects, by_uuid)
    active_objects = select_active_objects(
        objects,
        by_uuid,
        active,
        args.include_sidechains,
    )
    warn_about_branch_gaps(
        objects,
        by_uuid,
        active,
        args.include_thinking,
        question_tool_ids,
    )

    turns, active_rank = build_turns(
        active_objects,
        args.include_thinking,
        question_tool_ids,
    )

    if active is not None and not turns:
        # A record whose parent is missing from the file traces to a branch
        # holding no dialogue. Show everything rather than a blank transcript.
        fallback_objects = select_active_objects(
            objects,
            by_uuid,
            None,
            args.include_sidechains,
        )
        fallback_turns, fallback_rank = build_turns(
            fallback_objects,
            args.include_thinking,
            question_tool_ids,
        )
        if fallback_turns:
            print("WARN: the traced branch holds no dialogue; showing all turns",
                  file=sys.stderr)
            active = None
            turns, active_rank = fallback_turns, fallback_rank

    branch_reset = False
    rewind_turn = None
    if args.since is None:
        shown = turns
    elif args.since.isdigit():
        prior_turn = int(args.since)
        if prior_turn > len(turns):
            branch_reset = True
            shown = turns
        else:
            shown = turns[prior_turn:]
    else:
        matches = [turn for turn in turns if turn[4] == args.since]
        if matches:
            shown = [turn for turn in turns if turn[5] > matches[-1][5]]
        else:
            anchor = None
            current = args.since
            seen = set()
            while current and current in by_uuid and current not in seen:
                if active is None or current in active:
                    anchor = current
                    break
                seen.add(current)
                current = by_uuid[current].get("parentUuid")

            if anchor is None or anchor not in active_rank:
                branch_reset = True
                shown = turns
            else:
                anchor_rank = active_rank[anchor]
                shown = [turn for turn in turns if turn[5] > anchor_rank]
                if anchor != args.since:
                    branch_reset = True
                    rewind_turn = sum(
                        1 for turn in turns if turn[5] <= anchor_rank
                    )

    if rewind_turn is not None:
        print(
            "*** REWOUND: the other session was rolled back to turn "
            f"{rewind_turn}. Anything you noted after turn {rewind_turn} no "
            "longer applies; the turns below are the current conversation "
            "from that point. ***\n"
        )
    elif branch_reset and args.since is not None:
        print("(active branch changed; full active transcript follows)")

    if args.since is not None and not branch_reset and not shown:
        print("(no new persisted turns on the active branch)")
    else:
        for index, label, timestamp, text, _, _ in shown:
            if timestamp:
                timestamp = str(timestamp).replace("T", " ").replace("Z", "")[:19]
            header = f"[{index}] {label}" + (
                f"  {timestamp}" if timestamp else ""
            )
            print(header)
            print(text)
            print()

    cursor = turns[-1][4] if turns else ""
    print(f"BRANCH_RESET={int(branch_reset)}")
    print(f"TURNS_TOTAL={len(turns)}")
    print(f"CURSOR={cursor}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
