"""CLI regression tests with synthetic Codex storage; no account or network needed."""

import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest


PARSER = Path(__file__).with_name("parse_session.py")
ROOT = "00000000-0000-4000-8000-000000000001"
CHILD = "00000000-0000-4000-8000-000000000002"
REVERT = "00000000-0000-4000-8000-000000000003"


def record(kind, payload, **fields):
    return {"timestamp": "2026-09-23T10:00:00Z", "type": kind, "payload": payload, **fields}


def meta(thread=ROOT, **fields):
    return record("session_meta", {"id": thread, "cwd": "/example/project", "source": "vscode", **fields})


def event(kind, **fields):
    return record("event_msg", {"type": kind, **fields})


def response(role, text, **fields):
    return record("response_item", {"type": "message", "role": role,
                                   "content": [{"type": "input_text" if role == "user" else "output_text", "text": text}], **fields})


def item(kind, text=None, **fields):
    value = {"type": kind, "id": f"{kind}-id", **fields}
    if text is not None:
        value["content"] = [{"type": "text" if kind == "UserMessage" else "Text", "text": text}]
    return event("item_completed", item=value)


def task(number, user="hello", assistant="world", paginated=False):
    return [event("task_started", turn_id=f"turn-{number}"),
            response("user", user),
            item("UserMessage", user) if paginated else event("user_message", message=user),
            item("AgentMessage", assistant) if paginated else event("agent_message", message=assistant),
            response("assistant", assistant),
            event("task_complete", turn_id=f"turn-{number}", last_agent_message=assistant)]


def state(output, key="CURSOR"):
    return next(line[len(key)+1:] for line in output.splitlines() if line.startswith(key + "="))


class CodexSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.env = {**os.environ, "CODEX_HOME": str(self.home), "PYTHONDONTWRITEBYTECODE": "1"}
        self.env.pop("CODEX_THREAD_ID", None)
        self.env.pop("CODEX_SESSION_ID", None)

    def write(self, records, thread=ROOT, rollout=None, archived=False, day="23", numbered=False):
        directory = self.home / ("archived_sessions" if archived else "sessions/2026/09/" + day)
        directory.mkdir(parents=True, exist_ok=True)
        suffix = f"_{rollout}" if rollout else ""
        path = directory / f"rollout-2026-09-{day}T10-00-00-{thread}{suffix}.jsonl"
        if numbered:
            start = records[0]["payload"].get("history_base", {}).get("end_ordinal_exclusive", 0)
            records = [{**r, "ordinal": i + start} for i, r in enumerate(records)]
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))
        return path

    def run_parser(self, *args, code=0):
        result = subprocess.run([sys.executable, "-B", str(PARSER), *map(str, args)],
                                capture_output=True, text=True, env=self.env)
        self.assertEqual(result.returncode, code, result.stderr)
        return result.stdout, result.stderr

    def base(self, path, cutoff):
        lines = path.read_bytes().splitlines(keepends=True)
        selected = [line for line in lines if json.loads(line)["ordinal"] < cutoff]
        return {"thread_id": (path.stem.split("_")[-1] if "_" in path.stem else ROOT),
                "end_ordinal_exclusive": cutoff, "end_byte_offset": sum(map(len, selected))}

    def database(self, rows):
        connection = sqlite3.connect(self.home / "state_5.sqlite")
        connection.execute("CREATE TABLE threads (id TEXT PRIMARY KEY, rollout_path TEXT)")
        connection.executemany("INSERT INTO threads VALUES (?, ?)", [(key, str(path)) for key, path in rows])
        connection.commit()
        connection.close()

    def test_legacy_dialogue_is_not_duplicated(self):
        path = self.write([meta()] + task(1))
        output, _ = self.run_parser(path)
        self.assertEqual(state(output, "TURNS_TOTAL"), "2")
        self.assertEqual(output.count("hello"), 1)
        self.assertEqual(output.count("world"), 1)

    def test_paginated_dialogue_and_commentary(self):
        path = self.write([meta(history_mode="paginated")] + task(1, paginated=True) + [
            event("task_started", turn_id="second"), item("AgentMessage", "Working", phase="commentary"),
            response("assistant", "Working", phase="commentary"), item("AgentMessage", "Done", phase="final_answer"),
            response("assistant", "Done", phase="final_answer")], numbered=True)
        output, _ = self.run_parser(path)
        self.assertEqual(state(output, "TURNS_TOTAL"), "4")
        self.assertIn("Working", output)
        self.assertIn("Done", output)

    def test_repeated_messages_in_different_turns_survive(self):
        path = self.write([meta()] + task(1) + task(2))
        output, _ = self.run_parser(path)
        self.assertEqual(output.count("hello"), 2)
        self.assertEqual(output.count("world"), 2)

    def test_repeated_messages_in_same_turn_survive(self):
        records = [meta(), event("task_started", turn_id="one")]
        for _ in range(2):
            records += [event("agent_message", message="Again"), response("assistant", "Again")]
        output, _ = self.run_parser(self.write(records))
        self.assertEqual(output.count("Again"), 2)

    def test_response_only_and_implicit_turn_rollback(self):
        records = [meta(), response("user", "first"), response("assistant", "one"),
                   response("user", "second"), response("assistant", "two"), event("thread_rolled_back", num_turns=1)]
        output, _ = self.run_parser(self.write(records))
        self.assertIn("first", output)
        self.assertNotIn("second", output)
        self.assertEqual(state(output, "TURNS_TOTAL"), "2")

    def test_event_only_and_implicit_mirrors(self):
        records = [meta(), event("user_message", message="first"), response("user", "first"),
                   event("agent_message", message="one"), response("assistant", "one"),
                   event("user_message", message="second"), event("agent_message", message="two")]
        output, _ = self.run_parser(self.write(records))
        self.assertEqual(state(output, "TURNS_TOTAL"), "4")

    def test_hides_scaffolding_and_tools(self):
        records = [meta(), response("developer", "private developer instructions"),
                   response("user", "# AGENTS.md instructions for /example\nprivate setup"),
                   response("user", "<recommended_plugins>private setup</recommended_plugins>"),
                   response("user", "<skill>private setup</skill>"),
                   response("user", "<environment_context>private setup</environment_context>"),
                   item("CommandExecution", command=["private tool"]),
                   record("response_item", {"type": "function_call", "name": "exec_command", "arguments": "private tool"}),
                   event("token_count", private="private metrics"), response("user", "Please explain the code")]
        output, _ = self.run_parser(self.write(records))
        self.assertNotIn("private", output)
        self.assertIn("Please explain the code", output)

    def test_images_without_data(self):
        for records in ([meta(), event("user_message", message="inspect", images=["private image"], local_images=["private path"])],
                        [meta(), item("UserMessage", content=[{"type": "image", "url": "private image"}, {"type": "localImage", "path": "private path"}])],
                        [meta(), record("response_item", {"type": "message", "role": "user", "content": [{"type": "input_image", "image_url": "private image"}]})]):
            with self.subTest(records=records):
                output, _ = self.run_parser(self.write(records))
                self.assertIn("[Image attached]", output)
                self.assertNotIn("private", output)

    def test_question_and_answer_pairing_and_secrets(self):
        questions = [{"id": "q", "header": "Choice", "question": "Which approach?", "options": [{"label": "A", "description": "Fast"}]},
                     {"id": "secret", "question": "Token?", "isSecret": True}]
        records = [meta(), event("task_started", turn_id="one"),
                   record("response_item", {"type": "function_call", "name": "functions.request_user_input", "call_id": "ask1", "arguments": json.dumps({"questions": questions})}),
                   event("request_user_input", call_id="ask1", questions=questions),
                   record("response_item", {"type": "function_call_output", "call_id": "ask1", "output": json.dumps({"answers": {"q": {"answers": ["A", "custom note"]}, "secret": {"answers": ["sensitive-value"]}}})}),
                   record("response_item", {"type": "function_call_output", "call_id": "unrelated", "output": "private tool output"})]
        output, _ = self.run_parser(self.write(records))
        self.assertEqual(state(output, "TURNS_TOTAL"), "2")
        self.assertIn("1. A — Fast", output)
        self.assertIn("Which approach? → A, custom note", output)
        self.assertNotIn("sensitive-value", output)
        self.assertNotIn("private tool", output)

    def test_image_wrappers_and_attachment_order_are_mirrors(self):
        records = [meta(), event("task_started", turn_id="one"),
                   record("response_item", {"type": "message", "role": "user", "content": [
                       {"type": "input_text", "text": '<image name=[Image #1] path="private.png">'},
                       {"type": "input_image", "image_url": "private image"},
                       {"type": "input_text", "text": "</image>"},
                       {"type": "input_text", "text": "inspect this"}]}),
                   event("user_message", message="inspect this", local_images=["private.png"])]
        output, _ = self.run_parser(self.write(records))
        self.assertEqual(state(output, "TURNS_TOTAL"), "1")
        self.assertEqual(output.count("[Image attached]"), 1)
        self.assertNotIn("private", output)

    def test_legacy_inter_agent_communication_is_optional_and_deduplicated(self):
        records = [meta(), event("task_started", turn_id="one"),
                   record("inter_agent_communication", {"author": "worker", "recipient": "root", "content": "Finding", "trigger_turn": False}),
                   record("response_item", {"type": "agent_message", "author": "worker", "recipient": "root", "content": [{"type": "input_text", "text": "Finding"}]}),
                   record("response_item", {"type": "agent_message", "content": [{"type": "encrypted_content", "encrypted_content": "secret"}]})]
        path = self.write(records)
        hidden, _ = self.run_parser(path)
        self.assertNotIn("Finding", hidden)
        output, _ = self.run_parser(path, "--include-sidechains")
        self.assertEqual(output.count("Finding"), 1)
        self.assertNotIn("secret", output)

    def test_async_questions_and_malformed_tool_arguments(self):
        records = [meta(), event("agent_message", message="Pick a direction", questions=[{"title": "What next?", "options": ["Build", "Explore"]}]),
                   record("response_item", {"type": "function_call", "name": "request_user_input", "arguments": "not JSON", "call_id": "bad"}),
                   record("response_item", {"type": "function_call_output", "output": "not JSON", "call_id": "bad"})]
        output, _ = self.run_parser(self.write(records))
        self.assertIn("What next?", output)
        self.assertIn("2. Explore", output)
        self.assertEqual(state(output, "TURNS_TOTAL"), "2")

    def test_async_question_arriving_after_message_is_visible_on_refresh(self):
        records = [meta(), event("task_started", turn_id="one"), response("assistant", "Pick a direction")]
        path = self.write(records)
        initial, _ = self.run_parser(path)
        records.append(event("agent_message", message="Pick a direction", questions=[{"title": "What next?", "options": ["Build"]}]))
        refreshed, _ = self.run_parser(self.write(records), "--since", state(initial))
        self.assertNotIn("Pick a direction", refreshed)
        self.assertIn("What next?", refreshed)

    def test_async_tool_and_message_question_are_mirrors(self):
        questions = [{"title": "What next?", "options": ["Build", "Explore"]}]
        records = [meta(), event("task_started", turn_id="one"),
                   record("response_item", {"type": "function_call", "name": "request_user_input_async", "call_id": "ask", "arguments": json.dumps({"questions": questions})})]
        path = self.write(records)
        initial, _ = self.run_parser(path)
        records.append(event("agent_message", message="", questions=questions))
        path = self.write(records)
        output, _ = self.run_parser(path)
        self.assertEqual(output.count("What next?"), 1)
        refreshed, _ = self.run_parser(path, "--since", state(initial))
        self.assertIn("no new persisted turns", refreshed)

    def test_selected_compressed_rollout_does_not_fall_back_to_old_history(self):
        self.write([meta()] + task(1), day="20")
        path = self.write([meta()] + task(2), day="23", rollout=REVERT)
        compressed = Path(str(path) + ".zst")
        path.rename(compressed)
        self.database([(ROOT, compressed)])
        _, error = self.run_parser(ROOT, code=2)
        self.assertIn("compressed", error)

    def test_optional_reasoning_context_and_sidechains(self):
        records = [meta()] + task(1) + [
            record("response_item", {"type": "reasoning", "summary": [{"type": "summary_text", "text": "Reason summary"}], "encrypted_content": "encrypted-secret"}),
            record("compacted", {"message": "Context summary", "replacement_history": [{"role": "user", "content": "duplicated history"}]}),
            record("response_item", {"type": "agent_message", "author": "worker", "recipient": "root", "content": [{"type": "text", "text": "Worker finding"}]})]
        path = self.write(records)
        output, _ = self.run_parser(path)
        for hidden in ("Reason summary", "Context summary", "Worker finding", "encrypted-secret", "duplicated history"):
            self.assertNotIn(hidden, output)
        output, _ = self.run_parser(path, "--include-thinking", "--include-context", "--include-sidechains")
        for visible in ("hello", "Reason summary", "Context summary", "Worker finding"):
            self.assertIn(visible, output)
        self.assertNotIn("encrypted-secret", output)
        self.assertNotIn("duplicated history", output)

    def test_paginated_reasoning_mirrors_and_encrypted_only(self):
        records = [meta(), event("task_started", turn_id="one"), item("Reasoning", summary_text=["Think"], raw_content=[]),
                   record("response_item", {"type": "reasoning", "summary": [{"type": "summary_text", "text": "Think"}]}),
                   record("response_item", {"type": "reasoning", "summary": [], "encrypted_content": "secret"})]
        output, _ = self.run_parser(self.write(records), "--include-thinking")
        self.assertEqual(output.count("Think"), 1)
        self.assertNotIn("secret", output)

    def test_plan_mirror(self):
        records = [meta(), event("task_started", turn_id="one"), event("item_completed", item={"type": "Plan", "id": "plan", "text": "Build a thing"}), response("assistant", "<proposed_plan>\nBuild a thing\n</proposed_plan>")]
        output, _ = self.run_parser(self.write(records))
        self.assertEqual(output.count("Build a thing"), 1)
        self.assertNotIn("<proposed_plan>", output)

    def test_malformed_metadata_and_records_have_diagnostics(self):
        path = self.write([meta(history_base={"thread_id": None})])
        _, error = self.run_parser(path, code=2)
        self.assertIn("invalid Codex history_base", error)
        path = self.write([meta(), {"payload": {}}])
        _, error = self.run_parser(path, code=2)
        self.assertIn("invalid Codex record shape", error)

    def test_every_prefix_refresh_never_replays_a_mirror(self):
        for paginated in (False, True):
            records = [meta()] + task(1, paginated=paginated) + task(2, user="next", assistant="done", paginated=paginated)
            cursor = None
            seen = []
            for length in range(1, len(records) + 1):
                path = self.write(records[:length], numbered=paginated)
                args = ("--since", cursor) if cursor else ()
                output, _ = self.run_parser(path, *args)
                self.assertEqual(state(output, "BRANCH_RESET"), "0", output)
                for word in ("hello", "world", "next", "done"):
                    if word in output:
                        self.assertNotIn(word, seen, output)
                        seen.append(word)
                cursor = state(output)
            self.assertEqual(seen, ["hello", "world", "next", "done"])

    def test_no_updates_and_unknown_cursor(self):
        path = self.write([meta()] + task(1))
        output, _ = self.run_parser(path)
        refresh, _ = self.run_parser(path, "--cursor", state(output))
        self.assertIn("no new persisted turns", refresh)
        reset, _ = self.run_parser(path, "--since", "codex:missing")
        self.assertEqual(state(reset, "BRANCH_RESET"), "1")
        self.assertIn("hello", reset)

    def test_partial_json_and_partial_utf8_then_completion(self):
        path = self.write([meta()] + task(1))
        initial, _ = self.run_parser(path)
        complete = (json.dumps(event("agent_message", message="café"), ensure_ascii=False) + "\n").encode()
        prefix = path.read_bytes()
        for cut in (12, complete.index("é".encode()) + 1):
            path.write_bytes(prefix + complete[:cut])
            output, _ = self.run_parser(path, "--since", state(initial))
            self.assertIn("no new persisted turns", output)
        path.write_bytes(prefix + complete)
        output, _ = self.run_parser(path, "--since", state(initial))
        self.assertIn("café", output)

    def test_corrupt_middle_record_is_reported(self):
        path = self.write([meta()] + task(1))
        path.write_bytes(path.read_bytes() + b'{broken}\n' + json.dumps(event("task_complete")).encode())
        _, error = self.run_parser(path, code=2)
        self.assertIn("invalid Codex JSONL record", error)

    def test_repeated_rollback_and_divergence(self):
        records = [meta()] + task(1, "keep", "kept") + task(2, "discard", "discarded")
        path = self.write(records)
        original, _ = self.run_parser(path)
        records += [event("thread_rolled_back", num_turns=1)] + task(3, "new", "new reply")
        path = self.write(records)
        output, _ = self.run_parser(path, "--since", state(original))
        self.assertIn("REWOUND", output)
        self.assertIn("new reply", output)
        self.assertNotIn("discarded", output)
        records += [event("thread_rolled_back", num_turns=1), event("thread_rolled_back", num_turns=1)]
        output, _ = self.run_parser(self.write(records), "--since", state(output))
        self.assertEqual(state(output, "BRANCH_RESET"), "1")
        self.assertEqual(state(output, "TURNS_TOTAL"), "0")
        self.assertNotIn("new reply", output)
        refreshed, _ = self.run_parser(path, "--since", state(output))
        self.assertEqual(state(refreshed, "BRANCH_RESET"), "0")

    def test_rollback_counts_tasks_not_visible_messages(self):
        records = [meta()] + task(1, "keep", "kept") + [event("task_started", turn_id="two"),
                   event("user_message", message="one"), event("user_message", message="two"),
                   event("agent_message", message="three"), event("agent_message", message="four"),
                   record("compacted", {"message": "summary"}), event("thread_rolled_back", num_turns=1)]
        output, _ = self.run_parser(self.write(records), "--include-context")
        self.assertEqual(state(output, "TURNS_TOTAL"), "2")
        self.assertNotIn("summary", output)
        self.assertNotIn("four", output)

    def test_zero_and_oversized_rollbacks(self):
        records = [meta()] + task(1) + [event("thread_rolled_back", num_turns=0)]
        output, _ = self.run_parser(self.write(records))
        self.assertIn("hello", output)
        records += [event("thread_rolled_back", num_turns=100)]
        output, _ = self.run_parser(self.write(records))
        self.assertEqual(state(output, "TURNS_TOTAL"), "0")

    def test_invalid_rollback_is_reported(self):
        _, error = self.run_parser(self.write([meta(), event("thread_rolled_back", num_turns=-1)]), code=2)
        self.assertIn("rollback", error)

    def test_inherited_history_cutoff_and_same_thread_revert(self):
        root = self.write([meta(history_mode="paginated")] + task(1, "keep", "kept", True) + task(2, "discard", "discarded", True), numbered=True)
        base = self.base(root, 7)
        child = self.write([meta(CHILD, history_mode="paginated", history_base=base)] + task(3, "child", "child reply", True), thread=CHILD, numbered=True)
        output, _ = self.run_parser(child)
        self.assertIn("kept", output)
        self.assertIn("child reply", output)
        self.assertNotIn("discarded", output)
        reverted = self.write([meta(ROOT, history_mode="paginated", history_base=base)] + task(4, "replacement", "new reply", True), rollout=REVERT, numbered=True)
        original, _ = self.run_parser(root)
        self.database([(ROOT, reverted)])
        output, _ = self.run_parser(ROOT, "--since", state(original))
        self.assertEqual(state(output, "BRANCH_RESET"), "1")
        self.assertIn("new reply", output)
        self.assertNotIn("discarded", output)
        pinned, _ = self.run_parser(root)
        self.assertIn("discarded", pinned)

    def test_nested_inheritance_and_archived_base(self):
        root = self.write([meta(history_mode="paginated")] + task(1, "root text", "root reply", True), archived=True, numbered=True)
        child = self.write([meta(CHILD, history_mode="paginated", history_base=self.base(root, 7))] + task(2, "child text", "child reply", True), thread=CHILD, numbered=True)
        base = self.base(child, 14)
        base["thread_id"] = CHILD
        leaf = self.write([meta(REVERT, history_mode="paginated", history_base=base)] + task(3, "leaf text", "leaf reply", True), thread=REVERT, numbered=True)
        output, _ = self.run_parser(leaf)
        for value in ("root reply", "child reply", "leaf reply"):
            self.assertIn(value, output)

    def test_missing_cyclic_and_invalid_history_base(self):
        root = self.write([meta(history_mode="paginated")] + task(1, paginated=True), numbered=True)
        good = self.base(root, 7)
        bad_bases = [{**good, "thread_id": REVERT}, {**good, "end_byte_offset": good["end_byte_offset"] + 10},
                     {**good, "end_byte_offset": good["end_byte_offset"] - 2}, {**good, "end_ordinal_exclusive": 999},
                     {**good, "end_ordinal_exclusive": 0}, {**good, "end_byte_offset": "bad"}]
        for base in bad_bases:
            with self.subTest(base=base):
                path = self.write([meta(CHILD, history_mode="paginated", history_base=base)], thread=CHILD,
                                  numbered=type(base.get("end_ordinal_exclusive")) is int)
                _, error = self.run_parser(path, code=2)
                self.assertIn("history_base", error)
        cyclic = {"thread_id": CHILD, "end_ordinal_exclusive": 1, "end_byte_offset": 1}
        path = self.write([meta(CHILD, history_mode="paginated", history_base=cyclic)], thread=CHILD, numbered=True)
        _, error = self.run_parser(path, code=2)
        self.assertIn("cycle", error)

    def test_lineage_rejects_mismatched_identity_and_child_ordinal(self):
        path = self.write([meta(CHILD)] + task(1))
        _, error = self.run_parser(path, code=2)
        self.assertIn("identity", error)
        root = self.write([meta(history_mode="paginated")] + task(1, paginated=True), numbered=True)
        base = self.base(root, 7)
        child = self.write([meta(CHILD, history_mode="paginated", history_base=base),
                            event("user_message", message="child")], thread=CHILD)
        _, error = self.run_parser(child, code=2)
        self.assertIn("child rollout ordinal", error)

    def test_lineage_accepts_symlinked_codex_home(self):
        root = self.write([meta(history_mode="paginated")] + task(1, paginated=True), numbered=True)
        child = self.write([meta(CHILD, history_mode="paginated", history_base=self.base(root, 7))], thread=CHILD, numbered=True)
        alias = self.home / "home-alias"
        alias.symlink_to(self.home, target_is_directory=True)
        self.env["CODEX_HOME"] = str(alias)
        output, _ = self.run_parser(child)
        self.assertIn("hello", output)

    def test_path_uuid_custom_home_and_archive(self):
        path = self.write([meta()] + task(1), archived=True)
        by_path, _ = self.run_parser(path)
        by_id, _ = self.run_parser(ROOT)
        self.assertEqual(by_path, by_id)

    def test_database_selection_and_stale_or_mismatched_fallback(self):
        old = self.write([meta()] + task(1, "old", "old reply"), day="20")
        new = self.write([meta()] + task(2, "new", "new reply"), day="23", rollout=REVERT)
        self.database([(ROOT, old)])
        output, _ = self.run_parser(ROOT)
        self.assertIn("old reply", output)
        con = sqlite3.connect(self.home / "state_5.sqlite")
        for path in (self.home / "missing.jsonl", self.write([meta(CHILD)] + task(3, "wrong", "wrong reply"), thread=CHILD)):
            con.execute("UPDATE threads SET rollout_path = ?", (str(path),))
            con.commit()
            output, _ = self.run_parser(ROOT)
            self.assertIn("new reply", output)
            self.assertNotIn("wrong reply", output)
        con.close()
        self.assertTrue(new.exists())

    def test_corrupt_database_falls_back(self):
        self.write([meta()] + task(1))
        (self.home / "state_5.sqlite").write_bytes(b"not sqlite")
        output, _ = self.run_parser(ROOT)
        self.assertIn("hello", output)

    def test_missing_id_and_compressed_inputs(self):
        _, error = self.run_parser(ROOT, code=2)
        self.assertIn("not found", error)
        path = self.write([meta()] + task(1))
        compressed = Path(str(path) + ".zst")
        path.rename(compressed)
        _, error = self.run_parser(compressed, code=2)
        self.assertIn("compressed", error)
        _, error = self.run_parser(ROOT, code=2)
        self.assertIn("compressed", error)

    def test_listing_filters_current_subagent_cwd_and_limits(self):
        for number in range(1, 10):
            thread = f"00000000-0000-4000-8000-{number:012d}"
            fields = {"parent_thread_id": ROOT} if number == 2 else {}
            if number == 3:
                fields["source"] = {"subagent": {"other": "guardian"}}
            if number == 4:
                fields["cwd"] = "/different/project"
            path = self.write([meta(thread, **fields)] + task(number, f"request {number}", "done"), thread=thread)
            os.utime(path, (number, number))
        self.env["CODEX_THREAD_ID"] = ROOT
        output, _ = self.run_parser("--list-codex", "--cwd", "/example/project")
        rows = json.loads(output)
        self.assertEqual(len(rows), 5)
        self.assertEqual([row["preview"] for row in rows], [f"request {n}" for n in range(9, 4, -1)])
        self.assertTrue(all({"id", "path", "timestamp", "preview"} == set(row) for row in rows))
        output, _ = self.run_parser("--list-codex", "--cwd", "/nothing")
        self.assertEqual(json.loads(output), [])

    def test_files_and_database_are_unchanged(self):
        path = self.write([meta()] + task(1))
        self.database([(ROOT, path)])
        def snapshot():
            return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.home.rglob("*") if p.is_file()}
        before = snapshot()
        self.run_parser(ROOT)
        self.run_parser("--list-codex", "--cwd", "/example/project")
        self.assertEqual(snapshot(), before)


if __name__ == "__main__":
    unittest.main()
