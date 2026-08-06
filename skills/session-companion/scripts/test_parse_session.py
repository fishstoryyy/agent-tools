#!/usr/bin/env python3
"""End-to-end tests for the session-companion Claude Code parser."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PARSER = Path(__file__).with_name("parse_session.py")


class ParseSessionTests(unittest.TestCase):
    def run_parser(self, records, *args, truncated=False):
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
        self.assertEqual(result.returncode, 0, result.stderr)
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

    @staticmethod
    def message(role, uuid, parent_uuid, text, sidechain=False):
        return {
            "type": role,
            "uuid": uuid,
            "parentUuid": parent_uuid,
            "isSidechain": sidechain,
            "message": {"role": role, "content": text},
        }


if __name__ == "__main__":
    unittest.main()
