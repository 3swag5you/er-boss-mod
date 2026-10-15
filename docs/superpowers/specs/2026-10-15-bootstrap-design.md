# Workspace and agent bootstrap

## Intent and boundaries

Create a project-local workspace at `/home/elron/projects/elden-ring-boss-memories` for a future Elden Ring mod inspired by Sekiro memories: selecting a boss fight while resting at a Site of Grace. That sentence records intent only; boss behavior and mod architecture are not being designed now.

This bootstrap adds Git, repository instructions, introductory documentation, and OpenCode agent configuration. It does not add mod code, install dependencies, select a modding framework, inspect or alter game files, launch the game, create a remote repository, or change global OpenCode settings.

## Approach

Use native project-local OpenCode V2 configuration, rather than global agents (which would affect unrelated projects) or a custom orchestration plugin (unnecessary dependencies and complexity).

Keep the agent definitions and role-specific command templates together in `opencode.json`. Use `AGENTS.md` for project-wide scope and handoff rules, `README.md` for entry instructions, and `.gitignore` for local secrets, game assets, saves, and generated outputs.

## Roles and handoffs

| Role | Model | Responsibility |
| --- | --- | --- |
| Planner | `openai/gpt-6.1-sol#high` | Primary coordinator; clarify requirements and prepare approved work. |
| Implementer | `opencode-go/deepseek-v4.1-flash` | Carry out explicitly approved, bounded tasks and report checks through the user's OpenCode Go subscription. |
| Reviewer | `openai/gpt-6.1-sol#high` | Independently inspect changes and report findings without editing files. |

The planner is the default agent and can delegate to the implementer and reviewer. It may edit documentation, but implementation belongs to DeepSeek. The implementer cannot launch further agents; it must stop and report blockers instead of silently expanding scope. The reviewer cannot edit files or launch agents; shell access is limited to ordinary read-only Git inspection, with any additional command requiring approval.

Add `/er-plan`, `/er-implement`, and `/er-review` commands with explicit agent and model references. This avoids relying on agent switching to replace an already selected session model. The implementer uses the provider-default reasoning setting; no DeepSeek reasoning level was requested.

Handoffs identify the approved scope, relevant files, acceptance checks, and outstanding uncertainty. Planning and review are distinct from implementation. No automatic workflow, paid-model probe, or delegation begins merely by opening the project.

## Repository guidance

Record that mod planning is deferred until explicitly requested. Future agents must not invent a toolchain or act on the broad mod idea as authorization to begin work.

Require explicit approval before touching a game installation, save data, anti-cheat settings, or online play. Do not commit proprietary game files, credentials, or saves. Do not claim in-game validation from static checks.

Document how to open the workspace, select the role-specific commands, and distinguish model availability in the catalog from successful provider authentication. Keep bootstrap tracking separate from future mod plans.

## Verification and failure handling

Verify JSON parsing, documented V2 field shapes, exact model references and role modes, explicit command routing, permission restrictions, and absence of product dependencies or mod implementation. Confirm OpenCode discovers the project agents if its local CLI/API is available. Obtain an independent Sol high review of the final bootstrap changes.

Catalog availability has been confirmed for both models; live requests and provider credentials have not. Report authentication or runtime limitations without switching models or storing secrets. Do not install software or restart shared services to work around a validation limitation without approval.

## Acceptance

- A local Git repository exists at the approved path; no remote is created.
- Planner and reviewer explicitly select Sol high; implementer explicitly selects DeepSeek V4.1 Flash.
- Role-specific commands explicitly select the intended agent and model.
- Instructions and README make the deferred mod scope and workflow clear.
- Global configuration and game files remain unchanged.
- Verification results distinguish static configuration checks from live model or game execution.
