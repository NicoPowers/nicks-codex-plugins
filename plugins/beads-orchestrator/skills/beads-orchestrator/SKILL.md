---
name: beads-orchestrator
description: Coordinate Beads issue delivery from an orchestrator thread by claiming ready beads, creating same-directory Codex implementation and review threads at standard speed, checking progress with a five-minute heartbeat automation, owning Beads status/comment updates as workers progress, and closing only after review passes. Use when Nicolas asks Codex to orchestrate Beads, ready beads, bd issue queues, bead implementation/review workers, or background completion loops driven by Beads.
---

# Beads Orchestrator

Coordinate Beads delivery as the orchestrator, not as the implementation worker. Keep the current thread responsible for queue intake, worker/reviewer delegation, a compact ledger, heartbeat scheduling, Beads status/comment updates, and final disposition.

Assume Beads is already installed and initialized in the target repo. Do not clone the Beads repository, install `bd`, or run Beads setup unless Nicolas explicitly asks for setup help.

## Tool Discovery

Before starting or resuming orchestration, discover the current tool surface with `tool_search`:

- Codex threads: `list_projects`, `create_thread`, `read_thread`, `send_message_to_thread`, `set_thread_title`, `set_thread_pinned`, `set_thread_archived`, and `list_threads` when resolving existing thread ids.
- Automations: `automation_update`. Use a heartbeat automation attached to the current orchestrator thread for five-minute wakeups; do not use cron for thread progress checks.
- Beads CLI: use `bd` from the repo root, or `bd -C <repo>` when orchestrating a different working directory.

If a required Codex tool is unavailable, continue with direct checks in the current thread and tell Nicolas which automation/thread operation could not be performed.

## Beads Grounding

At the start of a run, load local Beads guidance with `bd -C <repo> prime`. Treat that output, repo `AGENTS.md`, and the bead records as the source of truth.

Use Beads for task state, not markdown TODO files:

- `bd -C <repo> ready --json` to find ready work.
- `bd -C <repo> show <id> --json --long --include-comments --include-dependents` to inspect a bead.
- `bd -C <repo> update <id> --claim` or `bd -C <repo> ready --claim --json` to claim one bead.
- `bd -C <repo> comment <id> --stdin` or `bd -C <repo> note <id> --stdin` for durable orchestration notes.
- `bd -C <repo> close <id> --reason <summary>` only after completion gates pass and closing is authorized.

## Queue Intake

1. Confirm the target repository and Beads database:
   - Run `bd -C <repo> where` when a repo path is known.
   - Run `bd -C <repo> ping` if the database is missing or suspect.
2. Run `bd -C <repo> prime` once per orchestration session.
3. Read the ready queue with `bd -C <repo> ready --json --limit 10`. Use label, type, priority, parent, or molecule filters only when Nicolas requested them.
4. Work one bead at a time unless Nicolas explicitly asks for parallel execution.
5. Claim exactly one bead with `bd -C <repo> ready --claim --json` or `bd -C <repo> update <id> --claim` if the bead id was specified.
6. Capture the full bead packet with `bd -C <repo> show <id> --json --long --include-comments --include-dependents`.

If there is no ready work, write a short final ledger and stop. Do not create a heartbeat with an empty queue.

## Context Packet

Before dispatching implementation, build a concise context packet from the repo and Beads data. Prefer repo-local truth over memory.

Include:

- Bead id, title, status, priority, type, labels, acceptance criteria, dependencies, dependents, comments, and notes.
- Exact repo path, current branch/ref, and confirmation that implementation and review threads must use the same working directory at standard speed unless Nicolas explicitly requests isolation.
- Relevant instructions named by `bd prime`, `AGENTS.md`, `CLAUDE.md`, `.codex/**`, `.agents/**/SKILL.md`, `CONTRIBUTING.md`, README files, ADRs, domain docs, and nearby tests/code.
- Validation commands inferred from the repo, `bd prime`, and local agent instructions.

If a category is absent, say so in the worker prompt. Do not invent missing acceptance criteria or project rules.

## Dispatch

Create a fresh implementation thread for the claimed bead:

- Use `list_projects`, then `create_thread` with the target project, the same working directory, and standard speed. Do not request fast speed, a new worktree, branch, or isolated workspace unless Nicolas explicitly asks for one.
- Pin and title the thread with the bead id and role.
- Prompt the worker to implement only that bead, preserve unrelated changes, avoid changing Beads status directly, run repo-appropriate validation, and report changed files, commits if any, validation, screenshots if UI changed, blockers, and completion status.
- Update the bead status/comment from the orchestrator thread to record that implementation has started, including the implementation thread id.

Create a review thread only after the implementation thread reports completion:

- The review thread must be independent from the worker, use the same working directory, use standard speed, and receive the bead packet, implementation report, branch/ref if any, changed files, validation output, and context packet.
- Ask the reviewer for findings first, ordered by severity, plus a clear pass/fail recommendation. Tell the reviewer to report review state to the orchestrator and not close or re-status the bead directly.
- If review fails, send a concise steering prompt back to the worker and keep the bead active.

## Heartbeat Loop

When there is an active worker or reviewer, create or update one heartbeat automation attached to the current orchestrator thread:

- Name it `Beads orchestrator: <repo or bead id>`.
- Schedule it to wake this orchestrator thread every five minutes.
- Prompt it to resume the Beads orchestration loop, read the ledger, inspect the active worker/reviewer thread, update Beads comments/state, and either continue, escalate, or stop and delete/pause the heartbeat.
- Store the automation id in the ledger when available.

On each wakeup:

1. Read the active thread with `read_thread`.
2. Classify state as `running`, `blocked`, `needs-steering`, `ready-for-review`, `reviewing`, `review-failed`, or `complete`.
3. If running, update the orchestrator ledger and update Beads status/comment when the durable state changed.
4. If blocked or drifting, update Beads status/comment from the orchestrator thread and send one steering prompt grounded in the bead and repo context.
5. If ready for review, update Beads status/comment from the orchestrator thread and create the review thread.
6. If review fails, update Beads status/comment from the orchestrator thread and route findings back to implementation.
7. If review passes, perform completion gates and close or update the bead from the orchestrator thread.
8. If there is another ready bead, claim it and repeat. If not, delete or pause the heartbeat and stop.

## Ledger

Maintain a compact ledger in the orchestrator thread and refresh it after every material action:

- Repo and Beads database path.
- Active bead id/title and Beads state.
- Implementation thread id, same-directory working path, branch/ref if any, and last observed state.
- Review thread id, same-directory working path, and last observed state.
- Heartbeat automation id/status.
- Validation summary and next action.

Use the ledger as the source of truth for resumes. If the ledger conflicts with Beads, thread state, or git state, inspect the external state and repair the ledger.

## Completion Gates

Do not close a bead until:

- The worker submitted a structured completion report.
- The reviewer found no blocking issues.
- Required validation passed, or failures are documented and accepted by Nicolas.
- UI changes have screenshots or browser checks when the repo expects them.
- Beads dependencies and acceptance criteria were rechecked.
- Branch, commit, push, merge, and deployment state match the requested delivery mode.

When gates pass:

- Add a Beads comment with implementation thread, review thread, branch/ref, validations, and disposition.
- Close with `bd -C <repo> close <id> --reason <summary>` when shipping/closing is authorized.
- Otherwise set an explicit operational state or leave a comment saying what remains.
- Archive worker/reviewer threads only when they are no longer useful to keep visible.

## Safety Rules

- Do not push, merge, deploy, or close beads unless Nicolas or repo instructions authorize it.
- Preserve unrelated worktree changes and tell workers to stage deliberate paths only.
- Use the same repo working directory and standard speed for implementation and review threads so all workers observe and update the same local Beads files with adequate reasoning time. Do not use fast speed. Only create worktrees or branches when Nicolas explicitly requests them.
- The orchestrator owns Beads status transitions and durable Beads comments. Workers and reviewers should report progress, blockers, validation, and recommendations back to the orchestrator instead of changing bead lifecycle state directly.
- Use `bd -C <repo>` for every Beads command once a target repo is known.
- Use Beads comments for durable coordination notes; use the current-thread ledger for orchestration state.
- Stop the heartbeat when the queue is complete, the bead is waiting on Nicolas, or the same blocker repeats without a useful next action.
