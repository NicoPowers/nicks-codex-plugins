---
name: seeds-and-mulch
description: Use Seeds (`sd`) as the lightweight, git-native source of truth for repository work and Mulch (`ml`) as its durable expertise layer. Use by default for Nicolas's epics, features, tasks, bugs, chores, plans, dependencies, ready queues, work status, implementation handoffs, and multi-agent orchestration; whenever a repo contains `.seeds/` or `.mulch/`; when creating or decomposing tracked work; when selecting, starting, blocking, updating, or closing work; and when loading or recording reusable repository learnings before or after implementation. If the user explicitly requests another issue tracker, use that tracker instead and do not mirror records automatically.
---

# Seeds and Mulch

Treat Seeds and Mulch as a paired, deliberately small workflow:

- Seeds owns work: what must change, why, priority, dependencies, status, and acceptance.
- Mulch owns reusable expertise: conventions, patterns, failures, decisions, references, and guides that future work should load.

Do not put task status in Mulch or copy ordinary implementation details into expertise. Do not create parallel Markdown task lists when Seeds is available.

Assume the CLIs are named `sd` and `ml`. On Windows, use `sd.cmd` or `ml.cmd` when PowerShell execution policy blocks the generated `.ps1` wrappers.

## Ground Every Session

1. Resolve the repository root and read `AGENTS.md`, `CLAUDE.md`, contributing guidance, ADRs, and local Codex instructions before changing tracker state.
2. Check for `.seeds/` and `.mulch/` and confirm the CLIs with `sd --version` and `ml --version`.
3. When `.seeds/` exists, run `sd prime --compact` before reading or changing work. Treat its output and `.seeds/config.yaml` as authoritative over this skill.
4. When `.mulch/` exists, run `ml prime` before implementation. Prefer `ml prime --files <repo-relative-paths>` or `ml prime <domain>` once the working set is known; use manifest mode when the repo config recommends it.
5. Inspect `git status` and preserve unrelated worktree changes.

If either CLI is missing, report the missing dependency and the official package name (`@os-eco/seeds-cli` or `@os-eco/mulch-cli`). Do not install global packages without the user's approval. Treat `sd init`, `ml init`, `sd onboard`, and `ml setup` as one-time repository setup operations; run them only when setup or adoption is requested or clearly authorized, and serialize them when other agents are active.

## Find or Create Work

Before creating a seed:

- Search for an existing match with `sd search <distinctive terms> --json` and inspect candidates with `sd show <id> --json`.
- Reuse or update an existing seed when it already represents the requested outcome.
- Check `sd config show` or `sd create --help` rather than assuming a repo's allowed types, priorities, or required fields.

Create one seed for one independently verifiable outcome:

```bash
sd create --title "Add retry policy to mail delivery" \
  --type task --priority 1 \
  --description "Outcome, constraints, and concrete acceptance checks."
sd label add <seed-id> <label>
```

Use the configured type that best reflects the outcome. Common defaults are:

- `epic`: a broad outcome spanning multiple capabilities or plans.
- `feature`: a user-visible or system capability that may need decomposition.
- `task`: one focused implementation or operational outcome.
- `bug`: incorrect behavior with reproduction and expected behavior.

Use dependencies only for real execution ordering:

```bash
sd dep add <issue> <depends-on>
sd blocked --json
sd ready --json
```

The first seed depends on the second. Avoid speculative dependency chains; unnecessary blockers hide valid work from `sd ready`.

## Decompose Epics and Larger Features

Keep a small, well-scoped request as one seed. For an epic, feature, or ambiguous multi-step request:

1. Create or reuse the parent seed.
2. Run `sd plan templates` and select the repo's matching template.
3. Emit the structured request with `sd plan prompt <seed-id> --json`.
4. Fill every required section from repository evidence and the user's request. Make steps vertical, independently verifiable slices rather than layer-only work.
5. Submit with `sd plan submit <seed-id> --plan <file>`.
6. Inspect with `sd plan show <seed-id>` and confirm that the correct first children appear in `sd ready --json`.

In a plan submission, a step's `blocks: [2, 3]` means that step blocks steps 2 and 3. Indices are one-based. Use `existing_seed` to adopt already-open work instead of duplicating it. Use `plan_template` for a child that needs its own nested plan. Use `sd plan adopt`, `reorder`, or `release` for an adopt-only plan such as a release train.

Do not hand-author parent/child relationships in descriptions when the plan surface can represent them.

## Execute Tracked Work

When the user specifies a seed, inspect it with `sd show <id> --json`. Otherwise select from `sd ready --json` using priority, labels, scope, and repository instructions; do not silently choose blocked work.

1. Mark the selected seed active with `sd update <id> --status in_progress`.
2. Load relevant Mulch expertise for the likely files or domain.
3. Implement only the seed's outcome, following normal repository validation and change-safety rules.
4. Keep the seed accurate when scope, priority, assignee, or dependencies materially change.
5. If external work blocks progress, add the real dependency or leave the seed open and report the blocker. Do not close incomplete work.

Seeds state is durable coordination state. Update it as part of the requested workflow, but do not create branches, commits, pull requests, or deployments unless the user or repository workflow calls for them.

## Orchestrate with a Goal and Sub-agents

Use this section only when the user explicitly asks to orchestrate, delegate, or carry an epic or queue through completion. Keep orchestration in the current task.

Confirm that goal and sub-agent spawn, message, status, and wait tools are available. If they are missing, report the unavailable capability and continue sequentially only when that still satisfies the request. Never substitute separate Codex tasks or automations.

1. Inspect the parent seed or ready queue and define one concrete objective. If an unfinished goal exists, resume it; otherwise create one goal for the objective.
2. Decompose missing work in Seeds before delegation. Treat seed dependencies and `sd ready --json` as the scheduling graph.
3. Spawn sub-agents for bounded, independently useful ready seeds. Pass the repository root, seed ID, acceptance criteria, relevant instructions and Mulch context, allowed file scope, and validation expectations.
4. Keep lifecycle ownership in the primary agent. Sub-agents report progress, changed files, validation, blockers, and insight candidates; they do not close or re-status seeds, update the goal, sync tracker data, or record Mulch unless explicitly delegated.
5. Parallelize only independent ready seeds and stay within the available concurrency limit. Because sub-agents share the filesystem, avoid overlapping file ownership; serialize work that touches the same files or setup/config surfaces.
6. Integrate and validate each result in the primary agent, update Seeds, then dispatch newly ready work. Use direct agent wait/status primitives for active work.
7. Ask a separate sub-agent for review when the risk or repository policy warrants it. Route actionable findings back to the implementation sub-agent or fix them in the primary agent.
8. Record a small set of evidence-backed Mulch insights centrally after integration to avoid duplicates.
9. Complete the goal only after every required seed and acceptance check for the objective is complete. Follow the goal tool's blocking rules when progress is genuinely impossible.

Never create or manage separate Codex threads for this workflow. Never use automation timers or heartbeat automations to poll workers. Seeds plus the current goal are the durable resume state; sub-agent messages are the live execution state.

## Preserve Learnings with Mulch

At the end of meaningful implementation, run `ml learn` and review the diff, tests, failures, seed, and commit evidence. Record only knowledge that would change how a future agent approaches the same subsystem. Skip Mulch entirely for typo-only work, routine dependency bumps, mechanical edits, or facts already obvious from code.

Choose the shortest-lived appropriate classification and a domain allowed by `ml status` and the contract printed by `ml prime`:

- `convention`: a stable rule to follow.
- `pattern`: a reusable approach that worked.
- `failure`: what failed and the resolution.
- `decision`: a choice and its rationale.
- `reference`: an important file, endpoint, or external fact.
- `guide`: a recurring procedure.

Tie each record to concrete evidence, preferably the active seed and relevant files or commit:

```bash
ml record <domain> --type <type> <type-specific-fields> \
  --evidence-seeds <seed-id> --evidence-file <path>
ml validate
```

Follow the local schema and CLI retry hints for type-specific required fields. Prefer one precise record over several overlapping records. Do not record secrets, transient debugging state, guesses, a restatement of the diff, or filler merely to prove Mulch was used.

## Complete and Hand Off

Before closing a seed:

1. Re-read its acceptance criteria and dependencies.
2. Run the required tests, checks, and visual verification.
3. Validate any new Mulch records with `ml validate`.
4. Close with a concrete evidence-based reason: `sd close <id> --reason <summary>`.
5. For planned work, update the plan outcome or review metadata only when the actual outcome or review is known.
6. Run `sd doctor` or `ml doctor` when store integrity is suspect.

`sd sync` stages and commits `.seeds/`; `ml sync` validates, stages, and commits `.mulch/`. Run either only when the user requested a commit or repository instructions explicitly authorize one. Coordinate syncs when multiple agents share a branch. Never push unless the user asks.

Report seed IDs and final states, dependencies created or removed, implementation validation, Mulch record IDs or why none were warranted, and whether `.seeds/` or `.mulch/` changes remain uncommitted.

## Invariants

- Never hand-edit `.seeds/*.jsonl` or `.mulch/expertise/*.jsonl`; use the CLIs so validation, locking, and atomic writes remain intact.
- Prefer `--json` for agent parsing and human or compact formats for user-facing summaries.
- Treat local `sd prime`, `ml prime`, configuration, and CLI help as newer than examples in this skill.
- Keep tracking lightweight: create only durable work records and durable learnings, not process theater.
