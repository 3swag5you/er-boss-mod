# Workspace and Agent Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install project-local OpenCode agents and introductory repository guidance without beginning mod work.

**Architecture:** One configuration document defines three agents and three explicit role/model commands. Markdown files define repository boundaries and usage; dependency-free Python tests check the bootstrap contract.

**Tech Stack:** OpenCode V2 JSON configuration, Markdown, Git, Python 3 standard-library unittest (bootstrap verification only).

**Spec:** `docs/superpowers/specs/2026-10-15-bootstrap-design.md`

## Global Constraints

- A local Git repository exists at the approved path; no remote is created.
- Planner and reviewer explicitly select Sol high; implementer explicitly selects DeepSeek V4.1 Flash.
- Role-specific commands explicitly select the intended agent and model.
- Instructions and README make the deferred mod scope and workflow clear.
- Global configuration and game files remain unchanged.
- Verification results distinguish static configuration checks from live model or game execution.
- Do not add mod code, install dependencies, select a modding framework, inspect or alter game files, launch the game, create a remote repository, or change global OpenCode settings.
- Do not invent a Git author identity. The initial spec commit failed because no identity is configured; leave commits pending and report that limitation if it remains unresolved.

## Review Focus

1. An existing session can retain its previous model: test explicit command models and document using `/er-plan` rather than merely switching agents.
2. A reviewer can mutate through an unrestricted shell despite denied edits: test an ask-by-default shell with only exact read-only Git commands allowed, plus explicit no-mutation instructions.
3. An implementer can recursively delegate and defeat role separation: test a final deny rule for all child agents.
4. Secrets, saves, and proprietary assets can be accidentally staged: exercise ignore patterns using `git check-ignore --no-index --stdin`, without creating any such files.
5. Opening the workspace can be mistaken for permission to start mod work or a live authentication check: test deferred-scope guidance in both documentation files and absence of automatic model probes or product manifests.

---

## Execution context

The user chose DeepSeek V4.1 Flash through their OpenCode Go subscription for implementation and GPT-6.1 Sol high for planning/review. Preserve that choice. Use one fresh DeepSeek implementation agent for the task, then independent Sol high spec and quality reviews. If named project agents are not yet in the tool catalog, use `general` with explicit `model` overrides `opencode-go/deepseek-v4.1-flash` and `openai/gpt-6.1-sol#high`, respectively. Do not silently fall back to the parent's model. The earlier `opencode/` route failed with insufficient pay-as-you-go funds; it is not the user's Go subscription route.

Use the approved checkout `/home/elron/projects/elden-ring-boss-memories`. It is a new repository with no existing code and an unborn branch; a worktree cannot be created until a first commit exists. Do not fabricate author identity to unblock worktree creation. Keep this bootstrap in the approved otherwise-empty checkout if the worktree skill confirms that limitation.

## File map

| File | Responsibility |
| --- | --- |
| `opencode.json` | Three role definitions, explicit routing commands, minimal permissions. |
| `AGENTS.md` | Scope, model ownership, handoff and safety rules. |
| `README.md` | Opening the project, role commands, verification and limitations. |
| `.gitignore` | Secrets, local game data, saves and generated artifacts. |
| `tests/test_bootstrap.py` | Static contract checks; not mod code or a chosen mod toolchain. |

### Task 1: Install and verify the bootstrap contract

**Files:** Create the five files above. Preserve the approved spec and this plan.

**Interfaces:**
- Consumes: the approved spec and the exact catalog-verified model IDs above.
- Produces: agents `planner` (primary), `implementer` (subagent), `reviewer` (subagent), and commands `/er-plan`, `/er-implement`, `/er-review`.
- Verification entrypoint: `python3 -m unittest discover -s tests -v`.

- [x] **Step 1: Record baseline and write the contract tests.**

Record the SHA-256 of `/home/elron/.config/opencode/opencode.json` in the coordinator's tool output, without copying its contents into the repository. Verify `git remote -v` is empty. Use `patch` for files.

Create `tests/test_bootstrap.py` with:

```python
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOL = "openai/gpt-6.1-sol#high"
FLASH = "opencode-go/deepseek-v4.1-flash"


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "opencode.json").read_text())

    def test_models_modes_and_explicit_commands(self):
        self.assertEqual(self.config["default_agent"], "planner")
        for role, model, mode in [
            ("planner", SOL, "primary"),
            ("implementer", FLASH, "subagent"),
            ("reviewer", SOL, "subagent"),
        ]:
            agent = self.config["agents"][role]
            self.assertEqual(agent["model"], model)
            self.assertEqual(agent["mode"], mode)
            name = {"planner": "er-plan", "implementer": "er-implement", "reviewer": "er-review"}[role]
            command = self.config["commands"][name]
            self.assertEqual(command["agent"], role)
            self.assertEqual(command["model"], model)
            self.assertEqual(command["subagent"], role != "planner")
            self.assertIn("$ARGUMENTS", command["template"])

    def test_role_permissions(self):
        for role in ("implementer", "reviewer"):
            rules = self.config["agents"][role]["permissions"]
            child_rules = [r for r in rules if r["action"] == "subagent"]
            self.assertEqual(child_rules[-1], {"action": "subagent", "resource": "*", "effect": "deny"})
        rules = self.config["agents"]["reviewer"]["permissions"]
        self.assertIn({"action": "edit", "resource": "*", "effect": "deny"}, rules)
        shell = [r for r in rules if r["action"] == "shell"]
        self.assertEqual(shell[0], {"action": "shell", "resource": "*", "effect": "ask"})
        expected = {"git status --short --branch", "git diff --", "git diff --cached --", "git diff --check", "git diff --cached --check", "git log -5 --oneline", "git ls-files"}
        self.assertEqual({r["resource"] for r in shell[1:]}, expected)
        self.assertTrue(all(r["effect"] == "allow" for r in shell[1:]))
        self.assertIn("Do not mutate", self.config["agents"]["reviewer"]["system"])

    def test_scope_and_existing_session_guidance(self):
        for filename in ("README.md", "AGENTS.md"):
            text = (ROOT / filename).read_text()
            self.assertIn("Mod planning is deferred", text)
            self.assertIn(SOL, text)
            self.assertIn(FLASH, text)
        readme = (ROOT / "README.md").read_text()
        self.assertIn("existing session", readme)
        self.assertIn("/er-plan", readme)
        self.assertIn("authentication", readme)
        self.assertNotIn("warming", self.config)
        for name in ("package.json", "pyproject.toml", "Cargo.toml", "CMakeLists.txt"):
            self.assertFalse((ROOT / name).exists())

    def test_sensitive_paths_are_ignored(self):
        paths = [".env", ".env.local", "game/example.bin", "assets/game/example.bin", "saves/example.sl2", "backup/example.sl2.bak", "build/output.bin", "dist/mod.zip", "tests/__pycache__/test.pyc"]
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin"],
            cwd=ROOT, input="\n".join(paths) + "\n", text=True,
            capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(result.stdout.splitlines()), set(paths))


if __name__ == "__main__":
    unittest.main()
```

- [x] **Step 2: Run the tests before configuration exists.**

Run `python3 -m unittest discover -s tests -v`. Expect failures naming missing `opencode.json`; fix syntax/import errors in the test itself before proceeding. This proves the contract is not passing against an empty checkout.

- [x] **Step 3: Create the minimal V2 configuration.**

Create `opencode.json` as JSON, with schema `https://opencode.ai/config.json`, root `model` `openai/gpt-6.1-sol`, and `default_agent` `planner`. The root model intentionally has no variant; explicit agent and command references carry `#high`.

Use the following agent values. Encode the system text as ordinary JSON strings.

```json
{
  "planner": {
    "description": "Plans approved work and coordinates implementation and review",
    "mode": "primary",
    "model": "openai/gpt-6.1-sol#high",
    "system": "You are the planner and coordinator. Follow AGENTS.md and relevant skills. Mod planning is deferred until explicitly requested. Clarify requirements and write only approved planning documentation; delegate implementation to implementer and independent review to reviewer. Supply approved scope, files, acceptance checks, and uncertainties with each handoff. Do not substitute models, implement product changes yourself, or treat opening the workspace as approval to start work.",
    "permissions": [
      {"action": "edit", "resource": "*", "effect": "deny"},
      {"action": "edit", "resource": "*.md", "effect": "allow"},
      {"action": "subagent", "resource": "*", "effect": "deny"},
      {"action": "subagent", "resource": "implementer", "effect": "allow"},
      {"action": "subagent", "resource": "reviewer", "effect": "allow"},
      {"action": "shell", "resource": "*", "effect": "ask"}
    ]
  },
  "implementer": {
    "description": "Implements explicitly approved tasks with DeepSeek V4.1 Flash",
    "mode": "subagent",
    "model": "opencode-go/deepseek-v4.1-flash",
    "system": "You are the implementer. Follow AGENTS.md, the approved task and relevant skills. Implement only the supplied approved scope. Preserve user work, run the task's verification checks, and report changed files, results, blockers and uncertainties. Stop rather than choose an unapproved toolchain, expand scope, substitute models, or touch game files. Do not launch other agents.",
    "permissions": [
      {"action": "subagent", "resource": "*", "effect": "deny"},
      {"action": "shell", "resource": "*", "effect": "ask"}
    ]
  },
  "reviewer": {
    "description": "Independently reviews approved changes without editing",
    "mode": "subagent",
    "model": "openai/gpt-6.1-sol#high",
    "system": "You are an independent reviewer. Follow AGENTS.md and relevant review skills. Read the approved scope, implementation and checks. Report actionable findings by severity with file and line references, then residual risks and verification limits. Do not mutate files through edit tools, shell commands, APIs or other tools; do not launch other agents or fix findings yourself. Additional verification commands require approval. Never claim static checks prove live provider authentication or in-game behavior.",
    "permissions": [
      {"action": "edit", "resource": "*", "effect": "deny"},
      {"action": "subagent", "resource": "*", "effect": "deny"},
      {"action": "shell", "resource": "*", "effect": "ask"},
      {"action": "shell", "resource": "git status --short --branch", "effect": "allow"},
      {"action": "shell", "resource": "git diff --", "effect": "allow"},
      {"action": "shell", "resource": "git diff --cached --", "effect": "allow"},
      {"action": "shell", "resource": "git diff --check", "effect": "allow"},
      {"action": "shell", "resource": "git diff --cached --check", "effect": "allow"},
      {"action": "shell", "resource": "git log -5 --oneline", "effect": "allow"},
      {"action": "shell", "resource": "git ls-files", "effect": "allow"}
    ]
  }
}
```

Put that object under root `agents`, not directly at the root. V2 whole-value `*` matching includes `/`, so the planner's `*.md` permission covers Markdown documentation in nested directories. Do not represent this as an OS-level sandbox; shell approval is a separate boundary.

Add these root `commands`:

```json
{
  "er-plan": {
    "description": "Select Sol high for explicitly requested planning",
    "agent": "planner",
    "model": "openai/gpt-6.1-sol#high",
    "subagent": false,
    "template": "Handle this explicit planning request under AGENTS.md; do not begin implementation or expand beyond the request: $ARGUMENTS"
  },
  "er-implement": {
    "description": "Run an approved implementation task with DeepSeek",
    "agent": "implementer",
    "model": "opencode-go/deepseek-v4.1-flash",
    "subagent": true,
    "template": "Implement only this explicitly approved task. If scope, acceptance checks, or required approval is missing, report the blocker without editing: $ARGUMENTS"
  },
  "er-review": {
    "description": "Review changes with Sol high without editing",
    "agent": "reviewer",
    "model": "openai/gpt-6.1-sol#high",
    "subagent": true,
    "template": "Independently review this scope against its approved requirements. Do not modify files. Report findings and verification limits: $ARGUMENTS"
  }
}
```

Do not add providers, credentials, plugins, automatic warming, mod dependencies, or a DeepSeek variant override.

- [x] **Step 4: Create repository instructions and usage documentation.**

Create `AGENTS.md`:

```markdown
# Project instructions

## Scope
Mod planning is deferred until explicitly requested. This repository currently contains only workspace and agent setup. The eventual goal is an Elden Ring boss-selection option at a Site of Grace, inspired by Sekiro memories; this is context, not an approved mod design or implementation task.

## Model ownership
- Planner and reviewer: `openai/gpt-6.1-sol#high`.
- Implementer: `opencode-go/deepseek-v4.1-flash`, provider-default reasoning, through the user's OpenCode Go subscription.
- The planner coordinates and writes approved documentation; DeepSeek implements; an independent Sol high reviewer checks changes.
- Do not silently substitute models. Report provider/authentication failures without storing credentials in the repository.

## Handoffs
Pass the approved scope, relevant files, acceptance checks, and unresolved uncertainty. Stop for missing approval or blockers. Implementers and reviewers must not delegate further. Follow applicable skills without overriding the chosen role/model split.

## Safety
Preserve user changes. Do not install dependencies, choose a modding framework, or begin mod work without an explicit request. Require explicit approval before accessing or changing a game installation, save data, anti-cheat settings, or online play. Do not commit secrets, saves, proprietary assets, or game binaries. Ignore rules are safeguards, not a substitute for reviewing staged files.

## Verification
Run `python3 -m unittest discover -s tests -v` for the bootstrap contract. Python is only a bootstrap-check utility, not a selected mod implementation language. Distinguish static checks from live model authentication and in-game tests. Reviewers must not mutate files through shell or other tools. No automatic model calls or mod workflow starts when opening this project.
```

Create `README.md`:

```markdown
# Elden Ring Boss Memories

Workspace bootstrap for a future mod inspired by Sekiro memories: choose a boss fight while resting at a Site of Grace.

**Mod planning is deferred.** No mod implementation, framework, dependency stack, game integration, or in-game validation exists yet.

## Open the workspace
Run `opencode` from `/home/elron/projects/elden-ring-boss-memories`.

## Agents
| Role | Model |
| --- | --- |
| Planner | `openai/gpt-6.1-sol#high` |
| Reviewer | `openai/gpt-6.1-sol#high` |
| Implementer (OpenCode Go) | `opencode-go/deepseek-v4.1-flash` |

The planner is the default. An existing session can retain its previous model when switching agents; use `/er-plan` with an explicit request to select the configured Sol high agent and model together.

- `/er-plan <explicit planning request>`: planning only; does not authorize implementation.
- `/er-implement <approved task and acceptance checks>`: a DeepSeek child implements the supplied task.
- `/er-review <scope and requirements>`: a Sol high child reviews without editing.

Child commands run in the background and return their result to the parent. Roles are configured preferences plus tool permissions and instructions, not an operating-system security sandbox. The reviewer asks before shell commands other than exact read-only Git inspections.

## Checks
Run `python3 -m unittest discover -s tests -v` using the existing Python 3 installation; no packages are required. These are bootstrap checks, not a mod toolchain choice.

The model catalog lists both requested models. Catalog presence and static checks do not establish provider authentication, billing access, successful live model calls, or in-game compatibility. If a provider is unavailable, report it; do not paste keys into project files or silently change models. Actual implementation/review calls are distinct from an extra paid authentication probe.

## Boundaries
See `AGENTS.md`. Do not touch a game installation, saves, anti-cheat settings, or online play without explicit approval. Never commit proprietary game files, saves, or credentials. No global OpenCode configuration is changed by this setup.

Git identity must be configured by the user before a first commit can succeed; do not invent an author. No remote repository is configured.
```

Create `.gitignore`:

```gitignore
# Secrets and per-machine overrides
.env
.env.*
!.env.example
*.key
*.pem

# Local game files and saves: never distribute proprietary data
/game/
/assets/game/
/saves/
*.sl2
*.sl2.*

# Generated and local output
/build/
/dist/
/artifacts/
/logs/
__pycache__/
*.py[cod]
```

- [x] **Step 5: Run contract and discovery checks.**

Run `python3 -m unittest discover -s tests -v`: expect four passing tests. Run `git diff --check` and `git diff --cached --check`: expect no whitespace errors. Read all five files to check that assertions are not the only basis for acceptance.

Run `opencode api get /api/agent` and `opencode api get /api/command` from the project directory to inspect discovery without sending model prompts. Confirm the three named agents, their model variants and permissions, plus the three command routes. If location scoping is unclear, inspect `opencode api --help` and the V2 OpenAPI route parameters before adding any header or parameter; do not guess. Record a discovery limitation if the running service cannot load the project; do not restart it or install anything without permission.

Recompute the global config SHA-256 and compare it with the Step 1 baseline. Run `git remote -v` again: expect empty output. Inspect `git status --short --branch` and ensure only bootstrap/spec/plan files are present. Do not create sample credentials, saves, or game data for tests.

- [x] **Step 6: Obtain independent Sol high review and resolve findings.**

Provide the fresh reviewer the spec, this plan, all new files (including untracked files), and exact verification output. Because the branch has no commits, do not rely on `HEAD` or `git diff` alone to enumerate files. Request spec-compliance review, then a separate fresh quality reviewer. Both use `openai/gpt-6.1-sol#high` and must not edit. Delegate fixes to DeepSeek, rerun checks, and re-review affected findings.

- [x] **Step 7: Record the final state without fabricating identity.**

If the user has supplied a valid Git identity, stage only the listed bootstrap/spec/plan files and commit with `git commit -m "chore: bootstrap project-local planning implementation and review agents"`. Otherwise leave commits pending; do not repeatedly retry the known failure or change local/global author settings. Report the repository location, entry commands, passing checks, discovery status, independent review outcome, and the identity limitation. Do not claim completion of mod work or live authentication unless separately evidenced.

## Plan self-review

The single task covers each spec section: local workspace and configuration; three exact models and roles; explicit routing; deferred scope and safety; ignore rules; static tests, runtime discovery, independent review and honest failure reporting. The five Review Focus conditions are covered by tests and human review of runtime output. No product dependencies, mod design decisions, API keys, automatic model probes or fabricated Git identity are introduced.

## Execution outcome

DeepSeek V4.1 Flash implemented through OpenCode Go. Independent Sol high spec, quality and final reviews approved the bootstrap with no blocking findings. Four static tests pass; cwd-scoped `opencode debug agents` and `opencode debug config` discover the intended roles and command mappings. Shared-service API listing remains scoped to the old location; configured slash-command execution and live permission enforcement were not probed. Actual implementation and review model requests succeeded. Mod work remains deferred, and global configuration is unchanged.

Nonblocking follow-up: expand permission regression tests for planner editing/delegation and effective reviewer edit denial. No commit was made because Git author identity remains unset; no identity, remote, merge or push was created. Execution evidence is retained in the ignored `.superpowers/sdd/2026-10-15-bootstrap/` directory while commits are pending.
