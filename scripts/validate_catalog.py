#!/usr/bin/env python3
"""Validate the published Mist skill and workflow catalog without dependencies."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "manifest.json"


class CatalogValidationError(Exception):
    """A deterministic catalog validation failure."""


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CatalogValidationError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicate_keys,
        )
    except (json.JSONDecodeError, CatalogValidationError) as error:
        raise CatalogValidationError(f"{path.relative_to(ROOT)}: {error}") from error


def require_string(entry: dict[str, Any], key: str, label: str) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CatalogValidationError(f"{label}: {key!r} must be a non-empty string")
    return value


def validate_relative_file(raw_path: str, label: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise CatalogValidationError(f"{label}: path must stay inside the repository")

    resolved = ROOT / relative
    if not resolved.is_file():
        raise CatalogValidationError(f"{label}: missing file {raw_path!r}")
    return resolved


def validate_unique(values: Iterable[tuple[str, str]], noun: str) -> None:
    seen: dict[str, str] = {}
    for value, label in values:
        previous = seen.get(value)
        if previous is not None:
            raise CatalogValidationError(
                f"duplicate {noun} {value!r}: {previous} and {label}"
            )
        seen[value] = label


def validate_manifest(manifest: Any) -> tuple[int, int]:
    if not isinstance(manifest, dict):
        raise CatalogValidationError("manifest root must be an object")
    if manifest.get("version") != 1:
        raise CatalogValidationError("manifest version must be 1")

    skills = manifest.get("skills")
    workflows = manifest.get("workflows")
    if not isinstance(skills, list) or not isinstance(workflows, list):
        raise CatalogValidationError("manifest skills and workflows must be arrays")

    skill_identities: list[tuple[str, str]] = []
    skill_paths: list[tuple[str, str]] = []
    for index, entry in enumerate(skills):
        label = f"skills[{index}]"
        if not isinstance(entry, dict):
            raise CatalogValidationError(f"{label}: entry must be an object")

        slug = require_string(entry, "slug", label)
        require_string(entry, "name", label)
        require_string(entry, "description", label)
        require_string(entry, "category", label)
        require_string(entry, "icon", label)
        path = require_string(entry, "path", label)
        require_string(entry, "updated_at", label)
        validate_relative_file(path, label)

        references = entry.get("references", [])
        if not isinstance(references, list) or not all(
            isinstance(reference, str) for reference in references
        ):
            raise CatalogValidationError(f"{label}: references must be string paths")
        for reference in references:
            validate_relative_file(reference, label)

        skill_identities.append((slug, label))
        skill_paths.append((path, label))

    workflow_identities: list[tuple[str, str]] = []
    workflow_paths: list[tuple[str, str]] = []
    for index, entry in enumerate(workflows):
        label = f"workflows[{index}]"
        if not isinstance(entry, dict):
            raise CatalogValidationError(f"{label}: entry must be an object")

        slug = require_string(entry, "slug", label)
        path = require_string(entry, "path", label)
        require_string(entry, "updated_at", label)
        workflow_path = validate_relative_file(path, label)
        load_json(workflow_path)

        workflow_identities.append((slug, label))
        workflow_paths.append((path, label))

    validate_unique(skill_identities, "skill slug")
    validate_unique(skill_paths, "skill path")
    validate_unique(workflow_identities, "workflow slug")
    validate_unique(workflow_paths, "workflow path")
    return len(skills), len(workflows)


def main() -> int:
    try:
        skill_count, workflow_count = validate_manifest(load_json(MANIFEST_PATH))
    except CatalogValidationError as error:
        print(f"catalog validation failed: {error}", file=sys.stderr)
        return 1

    print(
        f"catalog validation passed: {skill_count} skills, "
        f"{workflow_count} workflows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
