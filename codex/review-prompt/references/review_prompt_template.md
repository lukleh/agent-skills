# Review Prompt Template

Use this template when asking for a review of a code change or design implementation.

The goal is to keep the reviewer focused on:
- bugs in the chosen solution
- missed cases
- regressions
- missing tests

It is especially useful when a task has already gone through multiple review rounds and you want to avoid drifting into a different architecture by accident.

## When To Use This

Use this template when:
- the team already chose a solution direction
- there are explicit tradeoffs or non-goals
- you want the reviewer to check implementation quality, not relitigate the whole design
- earlier reviews kept pulling toward a stronger but different solution

## Core Principle

Always anchor the review to:
1. the real production or user-visible problem
2. the chosen solution
3. the reason that solution was chosen
4. the primary invariant that must hold
5. the explicit non-goals

The most important line to keep in the prompt is:

> Do not treat failure to satisfy a stronger alternative design as a bug unless it would still realistically break the chosen user-facing invariant.

## Reusable Prompt

```text
Please review this change with a code-review mindset, but evaluate it against the chosen solution and intended scope below.

Review priorities:
1. correctness bugs
2. missed failure cases
3. behavioral regressions
4. missing tests
5. security/privacy issues

Important: review against the chosen design
We intentionally chose the solution described below.
Please review whether this implementation is correct for that solution.

Do not treat failure to satisfy a stronger or different design as a bug by itself unless it would still realistically break the chosen user-facing invariant.

If you think the architecture itself is wrong, put that in a separate section called:
Architectural Objection

Otherwise, please stay focused on implementation bugs and misses in the chosen design.

Problem
- [Describe the real production/user-visible problem]
- [Describe the observed evidence/logs if relevant]
- [Describe what the user experiences today]

Chosen solution
- [Describe the solution we intentionally chose]
- [Describe the main mechanism]
- [Describe any important boundaries or simplifications]

Why we chose this solution
- [Explain why we chose this path]
- [Explain what alternative path we rejected]
- [Explain why the rejected path was too risky/complex/misaligned]

Primary invariant
This is the main thing the fix must achieve:
- [State the core invariant in one sentence]

Non-goals
These are explicitly not required unless they break the invariant above:
- [Non-goal 1]
- [Non-goal 2]
- [Non-goal 3]

Implementation summary
- [Key implementation point 1]
- [Key implementation point 2]
- [Key implementation point 3]

Files to review
- `[path/to/file1]`
- `[path/to/file2]`
- `[path/to/file3]`

Tests to review
- `[path/to/test1]`
- `[path/to/test2]`
- `[path/to/test3]`

What I want reviewed specifically
- [Question/risk area 1]
- [Question/risk area 2]
- [Question/risk area 3]
- [Question/risk area 4]

Review instructions
- Please give findings first, ordered by severity.
- Include concrete file/line references.
- Keep summaries brief.
- If you believe a stronger/different design is needed, only raise that as a finding if you can explain how the current chosen design would still realistically fail the primary invariant.
- Otherwise, put broader design concerns under `Architectural Objection`.

Verification already run
- `[command 1]`
- `[command 2]`
- `[command 3]`
```

## Minimal Fill-In Checklist

If you are preparing a review request quickly, make sure you provide these seven inputs:

1. `Problem`
2. `Chosen solution`
3. `Why chosen`
4. `Primary invariant`
5. `Non-goals`
6. `Files and tests in scope`
7. `Specific risks you want checked`

## Compact Request To Generate A Prompt

If you want an assistant to generate a filled review prompt for you, this short request works well:

```text
Prepare a review prompt using this structure:
problem, chosen solution, why chosen, primary invariant, non-goals, files, tests, specific risks, verification run.
Make it explicit that the reviewer should review against the chosen design and put broader disagreement in a separate "Architectural Objection" section.
```

## Why This Helps

This template reduces review drift by making two things explicit:
- what success means for the current change
- what the reviewer should treat as out of scope unless it breaks that success condition

That usually leads to higher-signal findings:
- real contract mismatches
- missed cleanup paths
- incomplete cancellation or retry behavior
- inconsistent sanitization
- gaps in tests for the chosen solution

Instead of endless review loops around:
- stronger but unchosen designs
- theoretical edge cases unrelated to the main invariant
- architectural preferences that do not block the current fix
