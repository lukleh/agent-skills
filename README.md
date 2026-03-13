# agent-skills

Reusable agent skills for coding assistants.

This repository is intended to hold skills for multiple agent runtimes, including Codex and Claude Code. It currently contains the `review-prompt` skill for Codex.

## Repository Layout

- `codex/`: skills in Codex-compatible format
- `claude-code/`: reserved for future Claude Code skills

## Current Skills

- `codex/review-prompt`: prepares a focused `/review` handoff for code changes, including the skill definition, review prompt template, helper script for inferring review scope, and agent metadata

## Status

This repository is intentionally small to start. More shared skills and Claude Code variants can be added over time.
