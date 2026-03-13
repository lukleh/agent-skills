# agent-skills

Shared agent skills for local tooling.

## Layout

- `codex/`: Codex skill directories copied in their native format
- `claude-code/`: planned namespace for future Claude Code skills

## Current Skills

- `codex/review-prompt`: Codex review handoff skill, including its template, helper script, and agent metadata

## Notes

- The Codex skill is stored as source content from the local skill installation.
- If we later want this repo to double as an install source, we can add lightweight sync or install scripts.
