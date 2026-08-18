#!/usr/bin/env python3
"""Conservative documentation accessibility checks.

This checker is not an ASD-STE100 validator. It catches a small set of obvious
regressions that are useful for this repository. Human review and
``docs/writing-style.md`` remain authoritative for project style.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

FILES = [
    REPO / "README.md",
    REPO / "SPEC.md",
    REPO / "spec" / "behavior.md",
    REPO / "spec" / "tests" / "README.md",
    REPO / "docs" / "design.md",
    REPO / "docs" / "runtime-implementation.md",
    REPO / "docs" / "terminology.md",
    REPO / "docs" / "writing-style.md",
    REPO / "docs" / "open-questions.md",
    REPO / "CONTRIBUTING.md",
    REPO / "SECURITY.md",
    REPO / "ROADMAP.md",
    REPO / "CHANGELOG.md",
    REPO / "examples" / "README.md",
    REPO / ".github" / "ISSUE_TEMPLATE" / "spec-bug.md",
    REPO / ".github" / "ISSUE_TEMPLATE" / "spec-change.md",
    REPO / ".github" / "pull_request_template.md",
]

# Hard failures are limited to phrases that are known to be stale or that have
# caused ambiguity in this repository. Broader style remains a human review
# responsibility.
FORBIDDEN_PROSE = {
    "scratch quotas": "scratch quota configuration was removed",
    "filesystem/network": "write 'filesystem and network'",
    "resource state/authority": "write the two concepts separately",
}

# Long-line detection is advisory. Technical identifiers and Markdown can make
# automatic sentence-length enforcement noisy.
ADVISORY_PROSE_WORDS = 55
WORD_RE = re.compile(r"\b[\w][\w'-]*\b")


def visible_prose_lines(path: Path):
    in_fence = False
    in_front_matter = False
    first_nonempty = True

    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()

        if first_nonempty and line:
            first_nonempty = False
            if line == "---":
                in_front_matter = True
                continue

        if in_front_matter:
            if line == "---":
                in_front_matter = False
            continue

        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if not line or line.startswith("#") or line.startswith("|"):
            continue

        if line.startswith("<!--") or line.startswith("[") and "]:" in line:
            continue

        yield number, line


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    for path in FILES:
        if not path.exists():
            failures.append(f"missing documentation file: {path.relative_to(REPO)}")
            continue

        for number, line in visible_prose_lines(path):
            lower = line.lower()
            for phrase, explanation in FORBIDDEN_PROSE.items():
                if phrase in lower:
                    failures.append(
                        f"{path.relative_to(REPO)}:{number}: avoid {phrase!r}: {explanation}"
                    )

            code_spans = re.findall(r"`[^`]+`", line)
            code_words = sum(len(WORD_RE.findall(span)) for span in code_spans)
            words = len(WORD_RE.findall(line))
            prose_words = max(0, words - code_words)
            if prose_words > ADVISORY_PROSE_WORDS:
                warnings.append(
                    f"{path.relative_to(REPO)}:{number}: prose line has "
                    f"{prose_words} words; consider splitting it"
                )

    for warning in warnings:
        print(f"warning: {warning}")

    if failures:
        print("documentation accessibility checks failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        f"documentation accessibility checks passed ({len(FILES)} files, "
        f"{len(warnings)} advisory warnings)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
