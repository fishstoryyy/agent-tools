#!/usr/bin/env python3
"""End-to-end tests for the session-companion Claude Code and OMP parser."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PARSER = Path(__file__).with_name("parse_session.py")


class ParseSessionTests(unittest.TestCase):
    def run_parser(self, records, *args, truncated=False, expected_code=0):
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".jsonl",
            encoding="utf-8",
            delete=False,
        )
        try:
            with handle:
                for record in records:
                    handle.write(json.dumps(record) + "\n")
                if truncated:
                    handle.write('{"type":"assistant","uuid":"partial"')
            result = subprocess.run(
                [sys.executable, str(PARSER), handle.name, *args],
                check=False,
                capture_output=True,
                text=True,
            )
        finally:
            os.unlink(handle.name)
        self.assertEqual(result.returncode, expected_code, result.stderr)
        return result.stdout, result.stderr

    def test_preserves_questions_answers_and_image_markers(self):
        records = [
            {
                "type": "user",
                "uuid": "u1",
                "parentUuid": None,
                "message": {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Please inspect this."},
                        {"type": "image", "source": {"data": "private-image"}},
                    ],
                },
            },
            {
                "type": "assistant",
                "uuid": "q1",
                "parentUuid": "u1",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "I need one decision."},
                        {
                            "type": "tool_use",
                            "id": "ask-1",
                            "name": "AskUserQuestion",
                            "input": {
                                "questions": [{
                                    "header": "Scope",
                                    "question": "Which path?",
                                    "options": [
                                        {
                                            "label": "Reusable",
                                            "description": "Build for repeated use.",
                                        },
                                        {
                                            "label": "One-off",
                                            "description": "Optimize for speed.",
                                        },
                                    ],
                                    "multiSelect": False,
                                }],
                            },
                        },
                        {
                            "type": "tool_use",
                            "id": "read-1",
                            "name": "Read",
                            "input": {"path": "/secret/tool-output"},
                        },
                    ],
                },
            },
            {
                "type": "user",
                "uuid": "u2",
                "parentUuid": "q1",
                "toolUseResult": {"answers": {"Which path?": "Reusable"}},
                "message": {
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": "ask-1",
                        "content": "fallback answer",
                    }],
                },
            },
            {
                "type": "assistant",
                "uuid": "a2",
                "parentUuid": "u2",
                "message": {"role": "assistant", "content": "Proceeding."},
            },
        ]

        stdout, _ = self.run_parser(records, truncated=True)

        self.assertIn("[Image attached]", stdout)
        self.assertIn("Question — Scope", stdout)
        self.assertIn("Which path?", stdout)
        self.assertIn("1. Reusable — Build for repeated use.", stdout)
        self.assertIn("Which path? → Reusable", stdout)
        self.assertNotIn("fallback answer", stdout)
        self.assertNotIn("/secret/tool-output", stdout)
        self.assertIn("BRANCH_RESET=0", stdout)
        self.assertIn("TURNS_TOTAL=4", stdout)
        self.assertTrue(stdout.rstrip().endswith("CURSOR=a2"))

    def test_preserves_free_text_notes_on_an_answer(self):
        records = [
            self.message("user", "u1", None, "Scope this."),
            self.message("assistant", "a1", "u1", "One decision first."),
            {
                "type": "user",
                "uuid": "u2",
                "parentUuid": "a1",
                "toolUseResult": {
                    "answers": {"Which scope?": "(notes only)"},
                    "annotations": {
                        "Which scope?": {
                            "notes": "Neither option fits:\nsolve for the band instead.",
                            "preview": "ASCII option preview, not user text",
                        },
                    },
                },
                "message": {"role": "user", "content": []},
            },
        ]

        stdout, _ = self.run_parser(records)

        self.assertIn("Which scope? → (notes only)", stdout)
        self.assertIn("notes: Neither option fits:", stdout)
        self.assertIn("solve for the band instead.", stdout)
        self.assertNotIn("ASCII option preview", stdout)
        self.assertIn("TURNS_TOTAL=3", stdout)

    def test_detached_tail_record_still_shows_the_conversation(self):
        records = [
            self.message("user", "u1", None, "Real question"),
            self.message("assistant", "a1", "u1", "Real answer"),
            {"type": "system", "uuid": "s1", "parentUuid": "absent", "content": "hook"},
        ]

        stdout, stderr = self.run_parser(records)

        self.assertIn("Real question", stdout)
        self.assertIn("Real answer", stdout)
        self.assertIn("TURNS_TOTAL=2", stdout)
        self.assertIn("holds no dialogue", stderr)

    def test_last_prompt_selects_live_branch_and_rewind_shows_divergence(self):
        records = [
            self.message("user", "u1", None, "Root"),
            self.message("assistant", "a1", "u1", "Shared"),
            self.message("user", "u-live", "a1", "Live prompt"),
            self.message("assistant", "a-live", "u-live", "Live reply"),
            self.message("user", "u-old", "a1", "Abandoned prompt"),
            self.message("assistant", "a-old", "u-old", "Abandoned reply"),
            {"type": "last-prompt", "leafUuid": "a-live"},
        ]

        full, _ = self.run_parser(records)
        self.assertIn("Live prompt", full)
        self.assertIn("Live reply", full)
        self.assertNotIn("Abandoned prompt", full)
        self.assertNotIn("Abandoned reply", full)
        self.assertIn("TURNS_TOTAL=4", full)
        self.assertTrue(full.rstrip().endswith("CURSOR=a-live"))

        refreshed, _ = self.run_parser(records, "--since", "a-old")
        self.assertIn("*** REWOUND", refreshed)
        self.assertIn("rolled back to turn 2", refreshed)
        self.assertIn("Live prompt", refreshed)
        self.assertIn("Live reply", refreshed)
        self.assertNotIn("Root\n", refreshed)
        self.assertNotIn("Shared\n", refreshed)
        self.assertIn("BRANCH_RESET=1", refreshed)

    def test_refresh_reports_no_new_turns_and_unknown_cursor_reset(self):
        records = [
            self.message("user", "u1", None, "Hello"),
            self.message("assistant", "a1", "u1", "Hi"),
        ]

        unchanged, _ = self.run_parser(records, "--cursor", "a1")
        self.assertIn("(no new persisted turns on the active branch)", unchanged)
        self.assertIn("BRANCH_RESET=0", unchanged)

        reset, _ = self.run_parser(records, "--since", "missing-cursor")
        self.assertIn("(active branch changed; full active transcript follows)", reset)
        self.assertIn("Hello", reset)
        self.assertIn("Hi", reset)
        self.assertIn("BRANCH_RESET=1", reset)

    def test_sidechains_are_optional_and_must_attach_to_active_branch(self):
        records = [
            self.message("user", "u1", None, "Root"),
            self.message("assistant", "a1", "u1", "Main reply"),
            self.message("user", "s-u", "a1", "Subagent task", sidechain=True),
            self.message(
                "assistant", "s-a", "s-u", "Subagent reply", sidechain=True
            ),
            self.message("user", "u2", "a1", "Continue main"),
        ]

        default, _ = self.run_parser(records)
        self.assertNotIn("Subagent task", default)
        self.assertNotIn("Subagent reply", default)
        self.assertIn("TURNS_TOTAL=3", default)

        included, _ = self.run_parser(records, "--include-sidechains")
        self.assertIn("[subagent] You", included)
        self.assertIn("[subagent] Agent", included)
        self.assertIn("TURNS_TOTAL=5", included)

    def test_claude_away_summaries_are_optional_context(self):
        records = [
            self.message("user", "u1", None, "Start the analysis."),
            self.message("assistant", "a1", "u1", "Working on it."),
            {
                "type": "system",
                "subtype": "away_summary",
                "uuid": "summary-1",
                "parentUuid": "a1",
                "content": "The analysis finished while you were away.",
            },
            self.message("user", "u2", "summary-1", "Show me the result."),
            self.message("assistant", "a2", "u2", "Here it is."),
        ]

        default, _ = self.run_parser(records)
        self.assertNotIn("[Away summary]", default)
        self.assertNotIn("The analysis finished while you were away.", default)
        self.assertIn("TURNS_TOTAL=4", default)

        stdout, _ = self.run_parser(records, "--include-context")

        self.assertIn("[3] Context", stdout)
        self.assertIn("[Away summary]", stdout)
        self.assertIn("The analysis finished while you were away.", stdout)
        self.assertIn("TURNS_TOTAL=5", stdout)

    def test_include_sidechains_surfaces_inline_claude_agent_results(self):
        records = [
            self.message("user", "u1", None, "Investigate this."),
            {
                "type": "assistant",
                "uuid": "a1",
                "parentUuid": "u1",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "I will delegate the search."},
                        {
                            "type": "tool_use",
                            "id": "agent-1",
                            "name": "Agent",
                            "input": {"prompt": "Find the cause."},
                        },
                    ],
                },
            },
            {
                "type": "user",
                "uuid": "result-1",
                "parentUuid": "a1",
                "toolUseResult": {
                    "agentId": "agent-abc",
                    "status": "completed",
                    "content": [{
                        "type": "text",
                        "text": "The subagent found the root cause.",
                    }],
                },
                "message": {
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": "agent-1",
                        "content": "Agent completed successfully.",
                    }],
                },
            },
            self.message("assistant", "a2", "result-1", "I agree with it."),
        ]

        default, _ = self.run_parser(records)
        self.assertNotIn("The subagent found the root cause.", default)
        self.assertNotIn("Agent completed successfully.", default)
        self.assertIn("TURNS_TOTAL=3", default)

        included, _ = self.run_parser(records, "--include-sidechains")
        self.assertIn("[3] [subagent] Agent", included)
        self.assertIn("The subagent found the root cause.", included)
        self.assertNotIn("Agent completed successfully.", included)
        self.assertIn("TURNS_TOTAL=4", included)

    def test_thinking_is_opt_in(self):
        records = [
            self.message("user", "u1", None, "Think"),
            {
                "type": "assistant",
                "uuid": "a1",
                "parentUuid": "u1",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "thinking", "thinking": "Private rationale"}],
                },
            },
        ]

        default, _ = self.run_parser(records)
        self.assertNotIn("Private rationale", default)
        self.assertIn("TURNS_TOTAL=1", default)

        included, _ = self.run_parser(records, "--include-thinking")
        self.assertIn("[thinking] Private rationale", included)
        self.assertIn("TURNS_TOTAL=2", included)

    def test_warns_when_a_file_contains_a_separate_root(self):
        records = [
            self.message("user", "u-old", None, "Separate root"),
            self.message("assistant", "a-old", "u-old", "Separate reply"),
            self.message("user", "u-live", None, "Live root"),
            self.message("assistant", "a-live", "u-live", "Live reply"),
        ]

        stdout, stderr = self.run_parser(records)
        self.assertNotIn("Separate root", stdout)
        self.assertIn("Live root", stdout)
        self.assertIn("2 turn(s) from a separate thread", stderr)

    def test_omp_dialogue_images_thinking_and_hidden_entries(self):
        records = self.omp_header() + [
            {
                "type": "session_init",
                "id": "init",
                "parentId": None,
                "timestamp": "2026-08-11T10:00:00Z",
                "task": "Duplicated by the next user message.",
            },
            self.omp_message(
                "user",
                "u1",
                "init",
                [
                    {"type": "text", "text": "Please inspect this."},
                    {"type": "image", "data": "private-image"},
                ],
            ),
            self.omp_message(
                "assistant",
                "a1",
                "u1",
                [
                    {"type": "thinking", "thinking": "Private rationale"},
                    {"type": "text", "text": "Inspection complete."},
                    {
                        "type": "toolCall",
                        "id": "read-1",
                        "name": "read",
                        "arguments": {"path": "/secret/tool-output"},
                    },
                ],
            ),
            {
                "type": "custom_message",
                "id": "custom-1",
                "parentId": "a1",
                "timestamp": "2026-08-11T10:00:03Z",
                "customType": "irc:incoming",
                "display": True,
                "content": "Do not include this custom message.",
            },
        ]

        stdout, _ = self.run_parser(records, truncated=True)
        self.assertIn("[Image attached]", stdout)
        self.assertIn("Inspection complete.", stdout)
        self.assertNotIn("Private rationale", stdout)
        self.assertNotIn("/secret/tool-output", stdout)
        self.assertNotIn("custom message", stdout)
        self.assertNotIn("Duplicated by the next user message", stdout)
        self.assertIn("TURNS_TOTAL=2", stdout)
        self.assertTrue(stdout.rstrip().endswith("CURSOR=a1"))

        with_thinking, _ = self.run_parser(records, "--include-thinking")
        self.assertIn("[thinking] Private rationale", with_thinking)
        self.assertIn("TURNS_TOTAL=2", with_thinking)

    def test_omp_preserves_rich_ask_questions_and_answers(self):
        records = self.omp_header() + [
            self.omp_message("user", "u1", None, "Help me choose."),
            self.omp_message(
                "assistant",
                "q1",
                "u1",
                [{
                    "type": "toolCall",
                    "id": "ask-1",
                    "name": "ask",
                    "arguments": {
                        "questions": [{
                            "id": "scope",
                            "header": "Scope",
                            "question": "Which path?",
                            "options": [
                                {
                                    "label": "Reusable",
                                    "description": "Build for repeated use.",
                                },
                                {
                                    "label": "One-off",
                                    "description": "Optimize for speed.",
                                },
                            ],
                            "multi": True,
                            "recommended": 0,
                        }],
                    },
                }],
            ),
            self.omp_message(
                "toolResult",
                "r1",
                "q1",
                [{"type": "text", "text": "raw fallback answer"}],
                toolName="ask",
                toolCallId="ask-1",
                isError=False,
                details={
                    "results": [{
                        "id": "scope",
                        "question": "Which path?",
                        "selectedOptions": ["Reusable"],
                        "customInput": "with a fallback",
                        "note": "Keep the interface stable.\nAvoid migration work.",
                    }],
                },
            ),
            self.omp_message("assistant", "a2", "r1", "Proceeding."),
        ]

        stdout, _ = self.run_parser(records)
        self.assertIn("Question — Scope", stdout)
        self.assertIn("1. Reusable (Recommended) — Build for repeated use.", stdout)
        self.assertIn("(Multiple selections allowed.)", stdout)
        self.assertIn("Which path? → Reusable, with a fallback", stdout)
        self.assertIn("notes: Keep the interface stable.", stdout)
        self.assertIn("Avoid migration work.", stdout)
        self.assertNotIn("raw fallback answer", stdout)
        self.assertIn("TURNS_TOTAL=4", stdout)

    def test_omp_context_records_and_rewind_follow_the_live_branch(self):
        records = self.omp_header() + [
            self.omp_message("user", "u1", None, "Root"),
            self.omp_message("assistant", "a1", "u1", "Shared"),
            self.omp_message("user", "u-old", "a1", "Abandoned prompt"),
            self.omp_message("assistant", "a-old", "u-old", "Abandoned reply"),
            {
                "type": "branch_summary",
                "id": "summary-1",
                "parentId": "a1",
                "timestamp": "2026-08-11T10:00:04Z",
                "fromId": "a-old",
                "summary": "Useful context retained from the old branch.",
            },
            {
                "type": "compaction",
                "id": "compact-1",
                "parentId": "summary-1",
                "timestamp": "2026-08-11T10:00:05Z",
                "summary": "The context the agent retained after compaction.",
                "firstKeptEntryId": "summary-1",
                "tokensBefore": 1000,
            },
            {
                "type": "reset_boundary",
                "id": "reset-1",
                "parentId": "compact-1",
                "timestamp": "2026-08-11T10:00:06Z",
            },
            self.omp_message("user", "u-live", "reset-1", "Current prompt"),
            self.omp_message("assistant", "a-live", "u-live", "Current reply"),
        ]

        full, _ = self.run_parser(records)
        self.assertNotIn("Abandoned prompt", full)
        self.assertNotIn("Abandoned reply", full)
        self.assertIn("[3] Context", full)
        self.assertNotIn("[Branch summary]", full)
        self.assertNotIn("[Compaction summary]", full)
        self.assertIn("[Context cleared]", full)
        self.assertIn("TURNS_TOTAL=5", full)

        included, _ = self.run_parser(records, "--include-context")
        self.assertNotIn("Abandoned prompt", included)
        self.assertNotIn("Abandoned reply", included)
        self.assertIn("[3] Context", included)
        self.assertIn("[Branch summary]", included)
        self.assertIn("[Compaction summary]", included)
        self.assertIn("[Context cleared]", included)
        self.assertIn("TURNS_TOTAL=7", included)

        refreshed, _ = self.run_parser(
            records, "--include-context", "--since", "a-old")
        self.assertIn("*** REWOUND", refreshed)
        self.assertIn("rolled back to turn 2", refreshed)
        self.assertIn("[Branch summary]", refreshed)
        self.assertIn("Current reply", refreshed)
        self.assertNotIn("Root\n", refreshed)
        self.assertIn("BRANCH_RESET=1", refreshed)

    def test_omp_agent_attribution_and_numeric_stable_cursor(self):
        records = self.omp_header() + [
            self.omp_message(
                "user",
                "12345678",
                None,
                "Task supplied by a parent agent.",
                attribution="agent",
            ),
            self.omp_message("assistant", "a1", "12345678", "Task complete."),
        ]

        full, _ = self.run_parser(records)
        self.assertIn("[1] Context", full)
        self.assertNotIn("[1] You", full)

        refreshed, _ = self.run_parser(records, "--since", "12345678")
        self.assertIn("[2] Agent", refreshed)
        self.assertNotIn("Task supplied by a parent agent.", refreshed)
        self.assertIn("BRANCH_RESET=0", refreshed)

    def test_rejects_an_unsupported_jsonl_format(self):
        stdout, stderr = self.run_parser(
            [{"type": "unrelated", "value": "not a session"}],
            expected_code=2,
        )
        self.assertEqual(stdout, "")
        self.assertIn("unsupported session format", stderr)

    @staticmethod
    def message(role, uuid, parent_uuid, text, sidechain=False):
        return {
            "type": role,
            "uuid": uuid,
            "parentUuid": parent_uuid,
            "isSidechain": sidechain,
            "message": {"role": role, "content": text},
        }

    @staticmethod
    def omp_header():
        return [{
            "type": "session",
            "version": 3,
            "id": "019fee76-4107-7000-9b27-b4294caae33b",
            "timestamp": "2026-08-11T10:00:00Z",
            "cwd": "/tmp/example",
        }]

    @staticmethod
    def omp_message(role, entry_id, parent_id, content, **message_fields):
        return {
            "type": "message",
            "id": entry_id,
            "parentId": parent_id,
            "timestamp": "2026-08-11T10:00:01Z",
            "message": {
                "role": role,
                "content": content,
                "timestamp": 1786442401000,
                **message_fields,
            },
        }


if __name__ == "__main__":
    unittest.main()
