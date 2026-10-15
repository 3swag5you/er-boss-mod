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

Repository: [3swag5you/er-boss-mod](https://github.com/3swag5you/er-boss-mod). GitHub authentication and Git author identity are separate. Configure your own author name and GitHub noreply email before committing; do not invent an author identity.
