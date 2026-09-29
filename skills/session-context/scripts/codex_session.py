"""Read local Codex rollouts without resuming sessions or changing their storage.

Normalize legacy and paginated records into the parser's parent-linked nodes.
Only history_base references are followed, never separate subagent sessions.
"""

from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import uuid


class CodexError(ValueError):
    """An unavailable or incomplete Codex transcript."""


def codex_home():
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser()


def is_uuid(value):
    try:
        return str(uuid.UUID(value)) == value.lower()
    except (ValueError, AttributeError, TypeError):
        return False


def filename_ids(path):
    match = re.fullmatch(
        r"rollout-\d{4}-\d\d-\d\dT\d\d-\d\d-\d\d-"
        r"([\da-f-]{36})(?:_([\da-f-]{36}))?\.jsonl(?:\.zst)?", path.name)
    if match and all(is_uuid(v) for v in match.groups() if v):
        return match[1], match[2] or match[1]
    return None


def session_files(home):
    for directory in ("sessions", "archived_sessions"):
        root = home / directory
        if root.is_dir():
            yield from root.rglob("rollout-*.jsonl")
            yield from root.rglob("rollout-*.jsonl.zst")


def read_meta(path):
    if path.name.endswith(".zst"):
        raise CodexError(f"compressed Codex rollout is unsupported: {path}; supply JSONL")
    try:
        with path.open("rb") as stream:
            obj = json.loads(stream.readline())
        payload = obj.get("payload")
        if obj.get("type") == "session_meta" and isinstance(payload, dict):
            return payload
    except (OSError, ValueError, AttributeError) as error:
        raise CodexError(f"cannot read Codex session metadata in {path}: {error}") from error
    raise CodexError(f"missing Codex session_meta header: {path}")


def resolve_session(thread_id, home=None):
    """Use the selected DB path if valid; otherwise the newest owned rollout."""
    home = home or codex_home()
    thread_id = str(uuid.UUID(thread_id))
    databases = sorted(home.glob("state_*.sqlite"),
                       key=lambda p: int(p.stem.split("_")[-1])
                       if p.stem.split("_")[-1].isdigit() else -1, reverse=True)
    for database in databases:
        try:
            connection = sqlite3.connect(database.resolve().as_uri() + "?mode=ro",
                                         uri=True, timeout=0.2)
            try:
                row = connection.execute(
                    "SELECT rollout_path FROM threads WHERE id = ?", (thread_id,)).fetchone()
            finally:
                connection.close()
        except (sqlite3.Error, OSError):
            continue
        if row and isinstance(row[0], str):
            path = Path(row[0]).expanduser()
            if path.is_file() and path.name.endswith(".zst"):
                raise CodexError(f"selected Codex rollout is compressed: {path}; supply JSONL")
            try:
                if read_meta(path).get("id") == thread_id:
                    return path
            except CodexError:
                continue

    matches = []
    compressed = []
    for path in session_files(home):
        ids = filename_ids(path)
        if ids and ids[0] != thread_id:
            continue
        if path.name.endswith(".zst"):
            if ids and ids[0] == thread_id:
                compressed.append(path)
            continue
        try:
            if read_meta(path).get("id") == thread_id:
                matches.append(path)
        except CodexError:
            continue
    # Filenames record rollout creation; mtime can also change on old ancestors.
    if matches or compressed:
        selected = max(matches + compressed,
                       key=lambda p: (p.name[:27], p.stat().st_mtime_ns, str(p)))
        if selected in compressed:
            raise CodexError(f"compressed Codex rollout is unsupported: {selected}; supply JSONL")
        return selected
    raise CodexError(f"Codex session {thread_id} not found under {home}")


def read_records(path, end=None):
    """Snapshot complete records, validating inherited byte/ordinal cutoffs."""
    meta = read_meta(path)
    try:
        with path.open("rb") as stream:
            data = stream.read(end["end_byte_offset"] if end else -1)
    except OSError as error:
        raise CodexError(f"cannot read Codex rollout {path}: {error}") from error
    if end and (len(data) != end["end_byte_offset"] or not data.endswith(b"\n")):
        raise CodexError(f"invalid history_base byte cutoff in {path}")
    ids = filename_ids(path)
    if not is_uuid(meta.get("id")) or ids and ids[0] != meta["id"]:
        raise CodexError(f"invalid or mismatched Codex session identity in {path}")
    source = ids[1] if ids else str(meta.get("id") or path.resolve())
    records = []
    offset = 0
    lines = data.splitlines(keepends=True)
    last_ordinal = None
    for index, line in enumerate(lines):
        position = offset
        offset += len(line)
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except (ValueError, UnicodeError) as error:
            if not end and index == len(lines) - 1 and not line.endswith(b"\n"):
                break
            raise CodexError(f"invalid Codex JSONL record in {path} at byte {position}") from error
        if (not isinstance(obj, dict) or not isinstance(obj.get("payload"), dict)
                or not isinstance(obj.get("type"), str)):
            raise CodexError(f"invalid Codex record shape in {path} at byte {position}")
        ordinal = obj.get("ordinal")
        if end and (type(ordinal) is not int or ordinal >= end["end_ordinal_exclusive"]):
            raise CodexError(f"invalid history_base ordinal cutoff in {path}")
        if type(ordinal) is int:
            if last_ordinal is not None and ordinal <= last_ordinal:
                raise CodexError(f"non-increasing Codex ordinals in {path}")
            last_ordinal = ordinal
        digest = hashlib.sha256(line.strip()).hexdigest()[:20]
        obj["_codex_id"] = f"codex:{source}:{ordinal if ordinal is not None else position}:{digest}"
        records.append(obj)
    if end and last_ordinal != end["end_ordinal_exclusive"] - 1:
        raise CodexError(f"history_base cutoff does not match the source prefix in {path}")
    return meta, records


def load_lineage(path, home=None):
    """Follow immutable rollout IDs (including same-thread reverts), oldest first."""
    home = home or codex_home()
    segments = []
    seen = set()
    end = None
    index = None
    while True:
        identity = (filename_ids(path) or (None, str(path.resolve())))[1]
        if identity in seen:
            raise CodexError(f"cycle in Codex history_base at {path}")
        seen.add(identity)
        meta, records = read_records(path, end)
        segments.append(records)
        base = meta.get("history_base")
        if base is None:
            break
        if (not isinstance(base, dict) or not is_uuid(base.get("thread_id"))
                or type(base.get("end_ordinal_exclusive")) is not int
                or base["end_ordinal_exclusive"] < 1
                or type(base.get("end_byte_offset")) is not int
                or base["end_byte_offset"] < 1):
            raise CodexError(f"invalid Codex history_base in {path}")
        if (meta.get("history_mode") != "paginated"
                or not records or records[0].get("ordinal") != base["end_ordinal_exclusive"]):
            raise CodexError(f"history_base does not match the child rollout ordinal in {path}")
        if index is None:
            index = defaultdict(list)
            # A portable exported lineage may live beside the selected file.
            candidates = set(session_files(home)) | set(path.parent.glob("rollout-*.jsonl*"))
            for candidate in {candidate.resolve() for candidate in candidates}:
                ids = filename_ids(candidate)
                if ids:
                    index[ids[1]].append(candidate)
        candidates = index.get(base["thread_id"], [])
        if not candidates:
            raise CodexError(f"missing Codex history_base rollout {base['thread_id']}")
        plain = [p for p in candidates if p.suffix == ".jsonl"]
        candidates = plain or candidates
        if len(candidates) != 1:
            raise CodexError(f"ambiguous Codex history_base rollout {base['thread_id']}")
        path, end = candidates[0], base
    return [record for segment in reversed(segments) for record in segment]


def content_text(content):
    if isinstance(content, str):
        return content.strip()
    if not isinstance(content, list):
        return ""
    image_types = {"image", "input_image", "localimage", "local_image", "imagefile", "image_file"}
    has_image = any(isinstance(block, dict) and str(block.get("type", "")).lower() in image_types
                    for block in content)
    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        kind = str(block.get("type", "")).lower()
        if kind in ("text", "input_text", "output_text", "summary_text", "reasoning_text"):
            if isinstance(block.get("text"), str):
                text = block["text"].strip()
                if has_image and re.fullmatch(r"</?image(?:\s.*)?>|\[Image #\d+\]", text, re.DOTALL):
                    continue
                parts.append(text)
        elif kind in image_types:
            parts.append("[Image attached]")
    return "\n".join(part for part in parts if part)


def json_object(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            return {}
    return value if isinstance(value, dict) else {}


def question_text(questions):
    parts = []
    for question in questions if isinstance(questions, list) else []:
        if not isinstance(question, dict):
            continue
        title = question.get("question") or question.get("title")
        if not isinstance(title, str) or not title.strip():
            continue
        parts.append("Question" + (f" — {question['header']}" if question.get("header") else ""))
        parts.append(title.strip())
        options = question.get("options")
        for number, option in enumerate(options if isinstance(options, list) else [], 1):
            if isinstance(option, str):
                parts.append(f"{number}. {option}")
            elif isinstance(option, dict) and option.get("label"):
                suffix = f" — {option['description']}" if option.get("description") else ""
                parts.append(f"{number}. {option['label']}{suffix}")
    return "\n".join(parts)


def answer_text(value, questions):
    answers = json_object(value).get("answers")
    if not isinstance(answers, dict):
        return ""
    by_id = {q.get("id"): q for q in questions if isinstance(q, dict)}
    parts = []
    for key, answer in answers.items():
        q = by_id.get(key, {})
        values = answer.get("answers") if isinstance(answer, dict) else None
        if not isinstance(values, list) or not values:
            continue
        rendered = "[Secret answer omitted]" if q.get("isSecret") else ", ".join(map(str, values))
        parts.append(f"{q.get('question') or q.get('title') or key} → {rendered}")
    return "\n".join(parts)


def scaffold(text):
    return text.startswith(("# AGENTS.md instructions for ", "<environment_context>",
                            "<permissions instructions>", "<turn_aborted>",
                            "<developer_instructions>", "<INSTRUCTIONS>",
                            "<recommended_plugins>", "<skill>"))


def readable(record, questions):
    """Return (kind, text, representation, identity) or None; never evaluate tools."""
    outer = record["type"]
    payload = record["payload"]
    kind = payload.get("type")
    source = "response" if outer == "response_item" else "event"
    identity = payload.get("id")
    if outer == "inter_agent_communication":
        text = content_text(payload.get("content"))
        if text:
            return "sidechain", f"[{payload.get('author', 'agent')} → {payload.get('recipient', 'agent')}]\n{text}", source, identity
        return None
    if outer == "compacted":
        text = content_text(payload.get("message"))
        return "context", "[Compaction summary]" + (f"\n{text}" if text else ""), "context", identity
    if outer == "event_msg" and kind == "item_completed":
        payload = payload.get("item")
        if not isinstance(payload, dict):
            return None
        kind = payload.get("type")
        identity = payload.get("id")
        source = "item"
    if outer == "response_item" and kind == "message":
        role = payload.get("role")
        if role not in ("user", "assistant"):
            return None
        text = content_text(payload.get("content"))
        if role == "user" and scaffold(text):
            return None
        return role, text, source, identity
    if kind in ("user_message", "UserMessage"):
        text = content_text(payload.get("message") if kind == "user_message" else payload.get("content"))
        if kind == "user_message":
            count = sum(len(payload.get(key) or []) for key in ("images", "file_ids", "local_images"))
            text = "\n".join([text] + ["[Image attached]"] * count).strip()
        return "user", text, source, identity
    if kind in ("agent_message", "AgentMessage"):
        if outer == "response_item":
            text = content_text(payload.get("content"))
            if text:
                return "sidechain", f"[{payload.get('author', 'agent')} → {payload.get('recipient', 'agent')}]\n{text}", source, identity
            return None
        text = content_text(payload.get("message") if kind == "agent_message" else payload.get("content"))
        return "assistant", text, source, identity
    if kind == "Plan" and source == "item":
        return "assistant", content_text(payload.get("text")), source, identity
    if kind in ("reasoning", "Reasoning", "agent_reasoning", "agent_reasoning_raw_content"):
        if kind == "reasoning":
            text = content_text(payload.get("summary")) or content_text(payload.get("content"))
        elif kind == "Reasoning":
            text = "\n".join(payload.get("summary_text") or payload.get("raw_content") or [])
        else:
            text = content_text(payload.get("text"))
        return "thinking", text, source, identity
    if kind == "request_user_input" and outer == "event_msg":
        call_id = payload.get("call_id")
        items = payload.get("questions") or []
        questions[call_id] = items
        return "question", question_text(items), source, call_id
    if kind == "function_call" and outer == "response_item":
        if payload.get("name", "").split(".")[-1] in ("request_user_input", "request_user_input_async"):
            items = json_object(payload.get("arguments")).get("questions") or []
            questions[payload.get("call_id")] = items
            return "question", question_text(items), source, payload.get("call_id")
    if kind == "function_call_output" and payload.get("call_id") in questions:
        text = answer_text(payload.get("output"), questions[payload["call_id"]])
        return "answer", text, source, payload.get("call_id")
    return None


def normalize(records):
    """Create a tree whose final leaf reflects rollbacks, retaining abandoned IDs.

    Mirror records are paired once per representation within one task. The first
    record owns the cursor even when its human-facing mirror is written later.
    """
    nodes = []
    parent = None
    groups = []
    current = None
    questions = {}
    pending = defaultdict(list)
    priorities = {"response": 0, "event": 1, "item": 2, "context": 3}
    for record in records:
        payload = record["payload"]
        event = payload.get("type") if record["type"] == "event_msg" else None
        if event == "thread_rolled_back":
            count = payload.get("num_turns")
            if type(count) is not int or count < 0:
                raise CodexError("invalid Codex rollback turn count")
            if count:
                removed = groups[max(0, len(groups) - count):]
                if removed:
                    parent = removed[0]["base"]
                    del groups[max(0, len(groups) - count):]
                current = None
                pending.clear()
                questions.clear()
        elif event == "task_started":
            turn_id = payload.get("turn_id")
            if current is None or current["turn_id"] != turn_id:
                current = {"base": parent, "turn_id": turn_id, "explicit": True}
                groups.append(current)
                pending.clear()

        rendered = readable(record, questions)
        match = None
        if rendered and rendered[1]:
            kind, text, source, identity = rendered
            # Plans have an XML wrapper only in the model-visible response.
            comparable = re.sub(r"^<proposed_plan>\s*|\s*</proposed_plan>$", "", text).strip()
            if kind == "user":
                # Legacy events put attachments after the text; response items
                # can put them before it. Do not duplicate the same user turn.
                comparable = (comparable.replace("[Image attached]", "").strip(),
                              comparable.count("[Image attached]"))
            key = (kind, identity if kind == "answer" else comparable)
            for candidate in pending[key]:
                if source not in candidate["sources"]:
                    match = candidate
                    break
            if kind == "user" and match is None and (current is None or not current["explicit"]):
                current = {"base": parent, "turn_id": record["_codex_id"], "explicit": False}
                groups.append(current)
                pending.clear()
            elif current is None and kind in ("assistant", "question", "thinking"):
                current = {"base": parent, "turn_id": record["_codex_id"], "explicit": False}
                groups.append(current)
                pending.clear()
            if match:
                match["sources"].add(source)
                if priorities[source] > match["priority"]:
                    match["node"]["_codex_turn"] = (kind, text)
                    match["priority"] = priorities[source]

        node = {"id": record["_codex_id"], "parentId": parent,
                "timestamp": record.get("timestamp", "")}
        if rendered and rendered[1] and match is None:
            node["_codex_turn"] = rendered[:2]
            pending[key].append({"node": node, "sources": {source}, "priority": priorities[source]})
        nodes.append(node)
        parent = node["id"]
        # Async questions can arrive after the mirrored message. Give them their
        # own node so a refresh never loses a newly persisted question.
        question_payload = payload.get("item", {}) if event == "item_completed" else payload
        if (event == "agent_message" or event == "item_completed"
                and question_payload.get("type") == "AgentMessage"):
            extra = question_text(question_payload.get("questions"))
            if extra:
                source = "item" if event == "item_completed" else "event"
                key = ("question", extra)
                mirror = next((p for p in pending[key] if source not in p["sources"]), None)
                if mirror:
                    mirror["sources"].add(source)
                else:
                    question_node = {"id": node["id"] + ":questions", "parentId": parent,
                                     "timestamp": node["timestamp"], "_codex_turn": ("question", extra)}
                    nodes.append(question_node)
                    parent = question_node["id"]
                    pending[key].append({"node": question_node, "sources": {source}, "priority": priorities[source]})
        if event in ("task_complete", "turn_aborted"):
            current = None
            pending.clear()
    return nodes


def extract_turn(node, include_thinking, include_context, include_sidechains):
    turn = node.get("_codex_turn")
    if not turn:
        return None
    kind, text = turn
    if kind == "thinking":
        return ("Agent", "[thinking] " + text) if include_thinking else None
    if kind == "context":
        return ("Context", text) if include_context else None
    if kind == "sidechain":
        return ("[subagent] Agent", text) if include_sidechains else None
    return ("You" if kind in ("user", "answer") else "Agent"), text


def list_sessions(cwd, home=None):
    home = home or codex_home()
    cwd = Path(cwd).expanduser().resolve()
    current_ids = {os.environ.get(key) for key in ("CODEX_THREAD_ID", "CODEX_SESSION_ID")}
    by_thread = {}
    for path in session_files(home):
        try:
            meta = read_meta(path)
            thread_id = meta.get("id")
            source = meta.get("source")
            if (not is_uuid(thread_id) or thread_id in current_ids
                    or meta.get("parent_thread_id")
                    or isinstance(source, dict) and "subagent" in source
                    or isinstance(source, str) and source.lower().startswith("subagent")
                    or Path(meta.get("cwd", "")).expanduser().resolve() != cwd):
                continue
            by_thread[thread_id] = None
        except (CodexError, OSError):
            continue
    candidates = []
    for thread_id in by_thread:
        path = resolve_session(thread_id, home)
        candidates.append((path.stat().st_mtime, thread_id, path))
    result = []
    for _, thread_id, path in sorted(candidates, reverse=True)[:5]:
        try:
            nodes = normalize(load_lineage(path, home))
            by_id = {node["id"]: node for node in nodes}
            active = set()
            leaf = nodes[-1]["id"] if nodes else None
            while leaf:
                active.add(leaf)
                leaf = by_id[leaf]["parentId"]
            preview = next((node["_codex_turn"][1] for node in nodes
                            if node["id"] in active and node.get("_codex_turn", (None,))[0] == "user"), "")
            preview = " ".join(preview.split())[:160]
        except CodexError as error:
            preview = f"[Unavailable: {error}]"
        result.append({"id": thread_id, "path": str(path),
                       "timestamp": read_meta(path).get("timestamp", ""), "preview": preview})
    return result
