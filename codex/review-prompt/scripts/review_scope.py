#!/usr/bin/env python3
"""Collect a review scope from the current git repository."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


TEST_SUFFIXES = (
    ".spec.js",
    ".spec.jsx",
    ".spec.ts",
    ".spec.tsx",
    ".test.js",
    ".test.jsx",
    ".test.ts",
    ".test.tsx",
)


def run_git(repo_root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise RuntimeError(message)
    return result.stdout


def resolve_repo_root(repo_path: str) -> Path:
    repo = Path(repo_path).expanduser().resolve()
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "not a git repository"
        raise RuntimeError(message)
    return Path(result.stdout.strip())


def unique_sorted(paths: list[str]) -> list[str]:
    return sorted({path for path in paths if path})


def split_lines(output: str) -> list[str]:
    return [line.strip() for line in output.splitlines() if line.strip()]


def is_test_file(path: str) -> bool:
    normalized = path.replace("\\", "/")
    name = Path(normalized).name

    if normalized.startswith("tests/") or normalized.startswith("web/tests/"):
        return True
    if "/tests/" in normalized:
        return True
    if name.startswith("test_") and name.endswith(".py"):
        return True
    if name.endswith("_test.py"):
        return True
    if any(normalized.endswith(suffix) for suffix in TEST_SUFFIXES):
        return True
    return False


def collect_working_tree_files(repo_root: Path) -> list[str]:
    unstaged = split_lines(run_git(repo_root, ["diff", "--name-only"]))
    staged = split_lines(run_git(repo_root, ["diff", "--cached", "--name-only"]))
    untracked = split_lines(run_git(repo_root, ["ls-files", "--others", "--exclude-standard"]))
    return unique_sorted(unstaged + staged + untracked)


def collect_diff_files(repo_root: Path, rev_range: str) -> list[str]:
    return unique_sorted(split_lines(run_git(repo_root, ["diff", "--name-only", rev_range])))


def collect_head_files(repo_root: Path) -> list[str]:
    output = run_git(repo_root, ["show", "--pretty=format:", "--name-only", "HEAD"])
    return unique_sorted(split_lines(output))


def head_has_parent(repo_root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD~1"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def build_scope(repo_root: Path, rev_range: str | None) -> dict[str, object]:
    if rev_range:
        changed_files = collect_diff_files(repo_root, rev_range)
        scope_kind = "revision_range"
        scope_label = rev_range
    else:
        changed_files = collect_working_tree_files(repo_root)
        if changed_files:
            scope_kind = "working_tree"
            scope_label = "working-tree"
        elif head_has_parent(repo_root):
            scope_kind = "revision_range"
            scope_label = "HEAD~1..HEAD"
            changed_files = collect_diff_files(repo_root, scope_label)
        else:
            scope_kind = "head_commit"
            scope_label = "HEAD"
            changed_files = collect_head_files(repo_root)

    test_files = [path for path in changed_files if is_test_file(path)]
    non_test_files = [path for path in changed_files if not is_test_file(path)]

    return {
        "repo_root": str(repo_root),
        "scope": {
            "kind": scope_kind,
            "label": scope_label,
        },
        "changed_files": changed_files,
        "test_files": test_files,
        "non_test_files": non_test_files,
    }


def print_text(scope: dict[str, object]) -> None:
    scope_info = scope["scope"]
    if not isinstance(scope_info, dict):
        raise RuntimeError("invalid scope data")

    print(f"Repo root: {scope['repo_root']}")
    print(f"Scope: {scope_info['label']} ({scope_info['kind']})")
    print()
    print("Changed files:")
    changed_files = scope["changed_files"]
    if isinstance(changed_files, list) and changed_files:
        for path in changed_files:
            print(f"- {path}")
    else:
        print("- (none)")
    print()
    print("Changed tests:")
    test_files = scope["test_files"]
    if isinstance(test_files, list) and test_files:
        for path in test_files:
            print(f"- {path}")
    else:
        print("- (none)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        default=".",
        help="Path inside the git repository to inspect. Defaults to the current directory.",
    )
    parser.add_argument(
        "--rev-range",
        help="Explicit revision range, for example HEAD~3..HEAD or main..HEAD.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of plain text.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        repo_root = resolve_repo_root(args.repo)
        scope = build_scope(repo_root, args.rev_range)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(scope, indent=2, sort_keys=True))
    else:
        print_text(scope)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
