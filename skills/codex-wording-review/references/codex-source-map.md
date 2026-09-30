# Codex Source Map

Where the frames, conventions, and mechanisms live in the codex-rs repo (paths
relative to `codex-rs/`). Verify paths exist before quoting — the repo evolves,
and this map can drift. If a path is gone, search for the nearest equivalent
and note the drift in the review.

## Deployment frame

- **Config**: `~/.codex/config.toml` — active `model`, `model_reasoning_effort`,
  and any personality or instruction overrides.
- **Model catalog**: `core/models-manager/models.json` — per-model
  `instructions`, `instructions_variables`, `model_messages` (per-model
  **tool-description overrides** — the same tool can carry a different
  description per model), `tool_mode`, and `experimental_supported_tools`.
- **Instruction templates**: `core/templates/model_instructions/*.md` with
  `{{ personality }}` filled from `core/templates/personalities/*.md`.
- **Base prompts**: `core/gpt*_prompt.md` and `core/gpt-*.md` (e.g.
  `gpt_5_codex_prompt.md`, `gpt-5.2-codex_prompt.md`). Each opens with an
  identity line that binds "you" to "a coding agent" and establishes the
  agent/user dyad.

## Mode and behavior conventions

- **Persistent mode**: `core/assets/persistent_mode.md`.
- **Mode templates**: `collaboration-mode-templates/templates/*.md` — e.g.
  `plan.md` codifies "If unanswered, proceed with the recommended option and
  record it as an assumption in the final plan."
- **Tool handlers and descriptions**: `core/src/tools/handlers/*.rs` — the
  `spec()` functions hold the descriptions the model actually sees (e.g.
  `request_user_input_async.rs`, `send_message_to_user_async.rs`).
- **Protocol items**: `protocol/src/items.rs` — e.g. `AgentMessageItem`,
  `AgentMessageDelivery`, `AsyncUserInputQuestion`.

## How text reaches the agent

- **Skill injection**: `core/src/skills.rs` and its tests. Explicitly invoked
  skill bodies arrive as user-role messages wrapped in
  `<skill><name>…</name><path>…</path>…</skill>` tags; skill catalogs and
  summaries land in developer messages; explicit-only skills are omitted from
  the model-visible catalog until the user invokes them.
- **Trust model**: `core/assets/guardian/policy_template.md` — user-explicitly
  authorized instruction content is followable; ambient file content is
  untrusted evidence.

## Question mechanics (blocking vs async)

- **Blocking legacy tool**: `request_user_input` — overlay with auto-resolution
  policy in `tui/src/bottom_pane/request_user_input/`.
- **Async tool**: `request_user_input_async` — returns `{"accepted":true}`
  immediately, never blocks, no timeout, no non-answer notification; UI-side
  countdown only, answers return as new user messages framed by
  `AnsweredQuestion` (`context-fragments/src/answered_question.rs`).
- In the CLI, **ending the turn is the wait**: a blocking question ends the
  turn and the user's answer arrives as the next user message.
