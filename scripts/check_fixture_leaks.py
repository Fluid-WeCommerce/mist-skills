#!/usr/bin/env python3
"""Reject named validation fixtures in reusable Mist skill context."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SUFFIXES = {".json", ".md"}

# Validation can use real fixture data, but reusable instructions must not teach
# agents facts from a prior company run.
FORBIDDEN_MARKERS = (
    "cowboy.com",
    "riding reinvented",
    "suisse intl",
    "connected-e-bike",
    "€2,399",
    "€3,299",
    "€3,999",
    "#141414",
    "#f8f8f5",
    "#bf4800",
)


def reusable_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in PUBLIC_SUFFIXES
        and ".git" not in path.parts
        and "validation" not in path.parts
    )


def main() -> int:
    failures: list[str] = []
    for path in reusable_files():
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            lowered = line.lower()
            for marker in FORBIDDEN_MARKERS:
                if marker in lowered:
                    relative_path = path.relative_to(ROOT)
                    failures.append(f"{relative_path}:{line_number}: {marker}")

    if failures:
        print("Named validation fixture data leaked into reusable skill context:")
        for failure in failures:
            print(f"- {failure}")
        print("Move fixture-specific evidence under validation/ and generalize the skill.")
        return 1

    print("No named validation fixture data found in reusable skill context.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
