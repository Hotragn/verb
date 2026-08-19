"""Enforce the tone constraints on every piece of prose in the repository.

    python scripts/check_prose.py

The rules are in CONTRIBUTING.md. They are checked rather than trusted because
a style guide nobody can run is a style guide nobody follows, and because these
particular tics creep back in one edit at a time.

Checked:

* No em dashes, en dashes, or the stylised spaced-hyphen substitute for them.
* None of the banned words.
* No trademark or registered symbols. Adoption is the point.
* No smart quotes, which arrive with copy-paste and break diffs.

Code files are checked too. A docstring is prose.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Windows consoles default to cp1252 and the specification is full of Greek.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

INCLUDE_SUFFIXES = {".md", ".py", ".html", ".json", ".yml", ".yaml", ".css", ".cff", ".txt"}

SKIP_DIRS = {
    ".git", "__pycache__", ".pytest_cache", "htmlcov", ".venv", "venv",
    "node_modules", ".idea", ".vscode", "build", "dist",
}

# LICENSE is the Apache text and is reproduced verbatim, so it is exempt.
SKIP_FILES = {"LICENSE"}

# Generated data. Names and identifiers in it are not prose.
SKIP_PATHS = {
    "examples/pmo40/decision_log.jsonl",
    "examples/pmo40/gate_data.json",
}

# CONTRIBUTING.md is where the banned list is published, so it has to contain
# the words. Every other check still applies to it.
BANNED_WORD_EXEMPT = {"CONTRIBUTING.md"}

BANNED_WORDS = [
    "delve", "leverage", "robust", "seamless", "transformative", "unlock",
    "crucial", "pivotal", "landscape", "navigate", "foster", "cutting-edge",
    "revolutionise", "revolutionize", "game-changing", "proprietary",
]

CHECKS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "em dash",
        re.compile(r"—"),
        "Use a comma, a colon, a semicolon or a full stop.",
    ),
    (
        "en dash",
        re.compile(r"–"),
        "Use a hyphen in ranges, or the word 'to'.",
    ),

    (
        "trademark symbol",
        re.compile(r"[™®]"),
        "The framework is not trademarked and should not look like it is.",
    ),
    (
        "smart quote",
        re.compile(r"[‘’“”]"),
        "Use straight quotes.",
    ),
    (
        "banned word",
        re.compile(r"\b(" + "|".join(BANNED_WORDS) + r")\b", re.IGNORECASE),
        "See the list in CONTRIBUTING.md.",
    ),
]

# The spaced-hyphen rule is applied to markdown prose only: outside code fences,
# outside inline code, and only between letters. A minus sign in "(1 - k)" is
# arithmetic, not a stylised dash, and flagging it would train people to ignore
# the checker.
PROSE_DASH = re.compile(r"(?<=[A-Za-z]) - (?=[A-Za-z])")
INLINE_CODE = re.compile(r"`[^`]*`")
FENCE = re.compile(r"^\s*(```|~~~)")

RED = "\033[31m" if sys.stdout.isatty() else ""
GREEN = "\033[32m" if sys.stdout.isatty() else ""
DIM = "\033[2m" if sys.stdout.isatty() else ""
RESET = "\033[0m" if sys.stdout.isatty() else ""


def files_to_check() -> list[Path]:
    found: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in INCLUDE_SUFFIXES:
            continue
        if path.name in SKIP_FILES:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative in SKIP_PATHS:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        # This file contains the banned list itself.
        if path.resolve() == Path(__file__).resolve():
            continue
        found.append(path)
    return found


def main() -> int:
    problems: list[str] = []
    checked = 0

    for path in files_to_check():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        checked += 1
        relative = path.relative_to(ROOT).as_posix()

        is_markdown = path.suffix == ".md"
        in_fence = False

        for number, line in enumerate(text.splitlines(), start=1):
            if is_markdown and FENCE.match(line):
                in_fence = not in_fence
                continue

            if is_markdown and not in_fence:
                stripped = INLINE_CODE.sub("", line)
                match = PROSE_DASH.search(stripped)
                if match:
                    problems.append(
                        f"{RED}{relative}:{number}{RESET}  spaced hyphen used as a dash\n"
                        f"    {DIM}{stripped.strip()[:90]}{RESET}\n"
                        "    Reads as a stylised em dash substitute. Rewrite the sentence."
                    )

            for label, pattern, advice in CHECKS:
                if label == "banned word" and relative in BANNED_WORD_EXEMPT:
                    continue
                match = pattern.search(line)
                if not match:
                    continue
                snippet = line.strip()
                if len(snippet) > 90:
                    start = max(0, match.start() - 35)
                    snippet = "..." + snippet[start : start + 90] + "..."
                problems.append(
                    f"{RED}{relative}:{number}{RESET}  {label}: {match.group(0)!r}\n"
                    f"    {DIM}{snippet}{RESET}\n"
                    f"    {advice}"
                )

    if problems:
        for problem in problems:
            print(problem)
        print()
        print(f"{RED}{len(problems)} tone violation(s) across {checked} files.{RESET}")
        return 1

    print(f"{GREEN}{checked} files clean.{RESET}")
    print("No em dashes, no banned words, no trademark symbols, no smart quotes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
