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
