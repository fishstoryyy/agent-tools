#!/usr/bin/env python3
"""Reconstruct the human-readable conversation from a Claude Code session .jsonl.

Extracts only user prompts and assistant replies, dropping tool calls, tool
results, thinking (by default), slash-command scaffolding, and other meta.
Designed to run repeatedly against a live, growing session file.

A session is a tree, not a flat log: rewinding or editing a prompt forks it
and leaves the abandoned turns in the file. Only the live branch is
reconstructed -- the parentUuid chain from the newest message back to the
root -- so rewound turns are skipped rather than replayed as real dialogue.

Usage:
    parse_session.py SESSION.jsonl [--since CURSOR] [--include-thinking]
                                   [--include-sidechains]

    --since CURSOR       Show only turns after CURSOR -- the value from the
                         CURSOR= line of a prior run (a turn uuid). A plain
                         integer turn index also works. Omit for the full
                         transcript.
    --include-thinking   Include the assistant's thinking blocks.
    --include-sidechains Include subagent (Task) turns; default is main thread.

The final two stdout lines are always:
    TURNS_TOTAL=<int>    turns on the live branch (for display)
    CURSOR=<uuid>        pass back as --since next refresh. It survives
                         rewinds: if the cursor was rolled back, the run
                         prints a "*** REWOUND ... ***" notice and shows the
                         current conversation from the divergence point.
"""

import argparse
import json
import re
import sys

# User strings dominated by these markers are pure CLI/system meta, not dialogue.
_META_MARKERS = ("<local-command-stdout>", "<local-command-caveat>")
# Mechanical slash-command wrappers: drop the tag+inner (the invocation itself).
_DROP_WRAPPERS = re.compile(
    r"<(command-name|command-message)>.*?</\1>", re.DOTALL
)
# The args a user passed to a slash command ARE their intent: keep the inner text.
_UNWRAP = re.compile(r"</?(command-args|command-contents)>")
# Any residual command-ish tags.
_STRAY_TAGS = re.compile(r"</?(command-[a-z-]+|local-command-[a-z-]+)>")


def clean_user_text(s):
    """Return conversational text from a user string, or '' if it is noise."""
    if any(m in s for m in _META_MARKERS):
        return ""
    s = _DROP_WRAPPERS.sub("", s)
    s = _UNWRAP.sub("", s)
    s = _STRAY_TAGS.sub("", s)
    return s.strip()


def blocks_text(content, include_thinking):
    """Join text (and optionally thinking) blocks from a list-form message."""
    parts = []
    for b in content:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "text":
            parts.append(b.get("text", ""))
        elif t == "thinking" and include_thinking:
            think = b.get("thinking", "") or b.get("text", "")
            if think.strip():
                parts.append("[thinking] " + think)
        # tool_use / tool_result / image / etc. are intentionally dropped.
    return "\n".join(p for p in parts if p.strip()).strip()


def _tool_result_text(content):
    """Flatten a tool_result's content (a str, or a list of text blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def answers_from_tool_results(content, tool_names):
    """The user's answers to AskUserQuestion arrive as a tool_result, not as
    text -- and that result also echoes the question. Surface it so a decision
    the user made through the question tool isn't dropped. Every other
    tool_result (file reads, command output, ...) stays dropped."""
    if not tool_names:
        return ""
    out = []
    for b in content:
        if not (isinstance(b, dict) and b.get("type") == "tool_result"):
            continue
        if b.get("is_error"):
            continue
        if tool_names.get(b.get("tool_use_id")) != "AskUserQuestion":
            continue
        s = _tool_result_text(b.get("content")).strip()
        if s and "<tool_use_error>" not in s:
            out.append(s)
    return "\n".join(out)


def extract_turn(obj, include_thinking, tool_names=None):
    """Return (role_label, text) for a conversational turn, or None to skip."""
    if obj.get("type") not in ("user", "assistant"):
        return None
    if obj.get("isMeta"):
        return None
    msg = obj.get("message") or {}
    role = msg.get("role")
    content = msg.get("content")

    if role == "user":
        if isinstance(content, str):
            text = clean_user_text(content)
        elif isinstance(content, list):
            # User list-form messages carry tool_result blocks; keep only text
            # plus the user's answers to AskUserQuestion (also a tool_result).
            text = blocks_text(content, include_thinking=False)
            answers = answers_from_tool_results(content, tool_names)
            text = "\n".join(p for p in (text, answers) if p).strip()
        else:
            text = ""
        label = "You"
    elif role == "assistant":
        if isinstance(content, list):
            text = blocks_text(content, include_thinking)
        elif isinstance(content, str):
            text = content.strip()
        else:
            text = ""
        label = "Agent"
    else:
        return None

    if not text:
        return None
    return label, text


def active_branch_uuids(objs, by_uuid):
    """UUIDs on the live conversation branch, or None if it can't be traced.

    The branch is the parentUuid chain from the newest main-thread message
    back to the root. Appends always land on whatever branch is live, so the
    last user/assistant line is the branch tip; fall back to the last-prompt
    leafUuid if there is no such line yet.
    """
    leaf = None
    for o in objs:
        if (o.get("type") in ("user", "assistant")
                and not o.get("isSidechain") and o.get("uuid")):
            leaf = o["uuid"]  # keep the last match: the newest tip
    if leaf is None:
        for o in objs:
            if o.get("type") == "last-prompt" and o.get("leafUuid"):
                leaf = o["leafUuid"]
    if leaf is None or leaf not in by_uuid:
        return None

    active = set()
    cur = leaf
    while cur and cur in by_uuid and cur not in active:  # guard against cycles
        active.add(cur)
        cur = by_uuid[cur].get("parentUuid")
    return active


def root_of(uuid, by_uuid):
    """Walk to the root (parentUuid is None) of the branch holding uuid."""
    seen = set()
    while uuid in by_uuid and uuid not in seen:
        parent = by_uuid[uuid].get("parentUuid")
        if parent is None:
            return uuid
        seen.add(uuid)
        uuid = parent
    return None  # chain broke before reaching a root


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session", help="Path to the session .jsonl file")
    ap.add_argument("--since", default=None, metavar="CURSOR",
                    help="Show only turns after CURSOR (a turn uuid from a "
                         "prior CURSOR= line, or a plain turn index)")
    ap.add_argument("--include-thinking", action="store_true",
                    help="Include the assistant's thinking blocks")
    ap.add_argument("--include-sidechains", action="store_true",
                    help="Include subagent (Task) turns")
    args = ap.parse_args()

    try:
        with open(args.session, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()
    except OSError as e:
        print(f"ERROR: cannot open session file: {e}", file=sys.stderr)
        return 2

    turns = []  # (index, label, timestamp, text, uuid)
    idx = 0
    objs = []
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        try:
            objs.append(json.loads(line))
        except json.JSONDecodeError:
            # A live session may be mid-write: skip a truncated/partial line.
            continue

    by_uuid = {o["uuid"]: o for o in objs if o.get("uuid")}
    # Map tool_use id -> tool name so a user's AskUserQuestion answer (which
    # comes back as a tool_result) can be recognised and kept.
    tool_names = {}
    for o in objs:
        if o.get("type") == "assistant":
            c = (o.get("message") or {}).get("content")
            if isinstance(c, list):
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        tool_names[b.get("id")] = b.get("name")
    active = active_branch_uuids(objs, by_uuid)
    if active is not None and not any(
            o.get("uuid") in active for o in objs
            if o.get("type") in ("user", "assistant")
            and not o.get("isSidechain")):
        # Couldn't trace a usable branch (e.g. unknown format): show
        # everything rather than a blank transcript.
        print("WARN: could not trace the active branch; showing all turns",
              file=sys.stderr)
        active = None

    if active is not None and not any(
            by_uuid[u].get("parentUuid") is None for u in active):
        # The chain stopped at a missing parent (truncated/compacted log)
        # instead of the root, so we may be showing only the tail. Say so
        # loudly -- never drop earlier turns in silence.
        print("WARN: live branch does not reach the session root; "
              "earlier turns may be missing from this transcript",
              file=sys.stderr)
    elif active is not None:
        # Turns under a *different* root are a separate thread in the same
        # file (e.g. a resumed session), not rewinds. Flag them; don't hide.
        live_root = next(u for u in active
                         if by_uuid[u].get("parentUuid") is None)
        other = sum(1 for o in objs
                    if o.get("type") in ("user", "assistant")
                    and not o.get("isMeta") and not o.get("isSidechain")
                    and o.get("uuid") and o["uuid"] not in active
                    and extract_turn(o, args.include_thinking, tool_names)
                    and root_of(o["uuid"], by_uuid) != live_root)
        if other:
            print(f"WARN: {other} turn(s) from a separate thread in this "
                  f"file (different root) are not shown", file=sys.stderr)

    for obj in objs:
        if obj.get("isSidechain") and not args.include_sidechains:
            continue
        # Skip turns on abandoned (rewound) branches -- main thread only.
        if active is not None and not obj.get("isSidechain"):
            u = obj.get("uuid")
            if u is not None and u not in active:
                continue
        turn = extract_turn(obj, args.include_thinking, tool_names)
        if turn is None:
            continue
        idx += 1
        label, text = turn
        turns.append((idx, label, obj.get("timestamp", ""), text, obj.get("uuid")))

    total = idx

    # Resolve --since: a turn uuid (robust cursor that survives rewinds) or,
    # for convenience, a plain integer turn index. Omitted -> full transcript.
    rewound = False
    if args.since is None:
        shown = turns
    elif args.since.isdigit():
        n = int(args.since)
        shown = [t for t in turns if t[0] > n]
        if not shown:
            print(f"(no new turns since {n})")
    else:
        # Anchor the cursor on the live branch: the cursor turn itself if it
        # is still there, else its nearest ancestor that is -- a rewind rolled
        # the cursor onto an abandoned branch.
        anchor = None
        cur = args.since
        seen = set()
        while cur and cur in by_uuid and cur not in seen:
            if active is None or cur in active:
                anchor = cur
                break
            seen.add(cur)
            cur = by_uuid[cur].get("parentUuid")
        if anchor is None:
            print("NOTE: last-seen turn not found on the live branch; "
                  "showing the full transcript", file=sys.stderr)
            shown = turns
        else:
            order = [o.get("uuid") for o in objs
                     if active is None or o.get("uuid") in active]
            rank = {u: i for i, u in enumerate(order)}
            ai = rank.get(anchor, -1)
            shown = [t for t in turns if rank.get(t[4], -1) > ai]
            if anchor != args.since:
                rewound = True
                before = sum(1 for t in turns if rank.get(t[4], -1) <= ai)
                print(f"*** REWOUND: the other session was rolled back to turn "
                      f"{before}. Anything you noted after turn {before} no "
                      f"longer applies; the turns below are the current "
                      f"conversation from that point. ***\n")
            elif not shown:
                print("(no new turns since the last cursor)")

    for t in shown:
        i, label, ts, text = t[0], t[1], t[2], t[3]
        ts_short = ts.replace("T", " ").replace("Z", "")[:19] if ts else ""
        header = f"[{i}] {label}" + (f"  {ts_short}" if ts_short else "")
        print(header)
        print(text)
        print()

    print(f"TURNS_TOTAL={total}")
    print(f"CURSOR={turns[-1][4] if turns else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
