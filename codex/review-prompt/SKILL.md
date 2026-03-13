---
name: review-prompt
description: Prepare scoped code-review prompts from a generic template, preferring current-session edits over unrelated dirty files, and by default save a ready-to-submit `/review @tmp/...` handoff file with optional repo-specific context only when directly relevant. Use when Codex needs to draft or "run" a review prompt, prepare a review request for the current branch or a commit range, or keep a reviewer focused on the chosen solution instead of relitigating the architecture.
---

# Review Prompt

Use this skill to turn a change into a filled review prompt that stays anchored to the chosen design. Start from the bundled generic template in `references/review_prompt_template.md`, then add repo-local context only when it is directly relevant to the current change.

## Default Behavior

- Treat "run the review prompt" as "prepare a `/review` handoff", not "explain the template".
- If the user gives no scope, prefer files touched in the current session/chat when they can be inferred reliably.
- Only fall back to the full current working tree when no session-local scope can be inferred. If the working tree is clean and the user gives no scope, default to `HEAD~1..HEAD`.
- By default, save the finished prompt body to a collision-safe file under `tmp/` using `mktemp tmp/review-input-XXXXXX.md`.
- By default, return only the ready command `/review @<path>` in chat.
- If the user explicitly asks for inline output, draft-only output, or a fixed save path, honor that instead.

## Workflow

### 1. Choose The Template

- If the user names a template path, use that path.
- Otherwise read `references/review_prompt_template.md` as the base template.
- Then search the repo for `REVIEW_PROMPT_ADDITIONS.md`. Prefer `docs/guides/REVIEW_PROMPT_ADDITIONS.md` when present.
- If a repo-local additions file exists, read it only to extract facts or review guidance that are directly relevant to the current change. Do not inject repo-specific rules wholesale into every prompt.

### 2. Gather The Review Scope

- If the user gives a revision range or file list, honor it.
- Otherwise infer a session-local scope from the strongest available evidence:
  - files edited or created in the current session
  - files explicitly named by the user as the target of the work
  - tests run in the current session
- Otherwise run:

```bash
uv run python ~/.codex/skills/review-prompt/scripts/review_scope.py --repo . --json
```

- Use the script output to confirm and expand the inferred scope, not to automatically replace it.
- If session-local files are known and overlap with the script output, use that narrower set as the default `Files to review` and include matching changed tests.
- If session-local files are known but the repo has many other unrelated dirty files, keep those extra files out of `Files to review`. Mention them only briefly as out-of-scope context if useful.
- If no session-local scope can be inferred, use the script output to seed `Files to review` and `Tests to review`.
- If the repo is not a git repo or neither the session evidence nor the script returns usable scope, ask for the files or range once.

### 3. Read Evidence

- Read the scoped files and scoped tests first, then any task or design doc that explains the change, and any repo-local review additions.
- Expand beyond the scoped files only when a nearby file is a direct dependency or needed to understand the chosen solution.
- Infer `Implementation summary`, `Files to review`, and `Tests to review` from the evidence.
- Infer `Verification already run` only from explicit evidence such as user-provided commands, CI output, terminal output, or docs in the repo. Never invent verification commands.
- If project-specific facts matter, include them under a short `Relevant project context` section sourced from the repo. Keep this section conditional and evidence-backed.

### 4. Ask Only For Missing Anchors

- Ask for the smallest missing set from:
  - `Problem`
  - `Chosen solution`
  - `Why we chose this solution`
  - `Primary invariant`
  - `Non-goals`
  - `What I want reviewed specifically`
- If several are missing, ask in one compact message.
- If the user already provided equivalent information in another form, normalize it instead of asking again.

### 5. Draft The Prompt

- Preserve the structure and review focus from the generic template unless the user explicitly supplied a different template path.
- Keep the template itself project-agnostic.
- Merge repo-local findings into the most relevant existing sections only when they are directly relevant to the reviewed change.
- If project-specific context does not map cleanly to an existing section, add a short `Relevant project context` section instead of rewriting the full template.
- Keep the instruction that broader disagreement belongs under `Architectural Objection`.
- Prefer concrete file paths over descriptions.
- Keep `Files to review` centered on the current-session scope unless the user explicitly asked for current-branch or full-working-tree review.
- If broader dirty-tree changes exist but are out of scope, do not list them as primary review files. Mention them in one short note or a `Related context` section only if that helps the reviewer avoid confusion.
- Use short, direct bullets.
- If a field is still unknown after one clarification pass, leave a clear placeholder such as `[confirm primary invariant]` instead of guessing.
- The saved handoff file should contain the review request body only, not the literal `/review ` prefix.

### 6. Save Optional Output

- Default output mode is handoff-file.
- Create the handoff path with `mkdir -p tmp && mktemp tmp/review-input-XXXXXX.md` so parallel runs do not overwrite each other.
- Save the finished review request body to that file unless the user specifies another path.
- By default, reply with exactly one line: `/review @<path>`.
- If the user asks for inline output, paste the finished prompt in chat instead.
- If the user asks for both, save the file and also paste the prompt body in chat.

## Resources

- `scripts/review_scope.py`: collect changed files and changed tests from the current repo or an explicit revision range.
- `references/review_prompt_template.md`: generic base template used by default.
- `REVIEW_PROMPT_ADDITIONS.md`: optional repo-local additions file. Prefer `docs/guides/REVIEW_PROMPT_ADDITIONS.md` when present.

## Example Invocations

- `Use $review-prompt for the changes from this session, not the whole dirty working tree.`
- `Use $review-prompt for the current branch.`
- `Use $review-prompt for HEAD~3..HEAD and save it to a specific path.`
- `Use $review-prompt with repo additions from docs/guides/REVIEW_PROMPT_ADDITIONS.md only where they are directly relevant.`
