#!/usr/bin/env python3
"""Dependency-free validator for partner-campaign company profiles."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SUBDOMAIN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
OPTION_ID = re.compile(r"^[a-z0-9_]+$")
SAFE_LINE = re.compile(r"^[^\r\n]+$")
AUDIENCE = re.compile(r"^[A-Za-z][A-Za-z -]*$")
SCREEN = re.compile(r"^portal/screens/[a-z0-9-]+\.json$")
WIDGET_ID = re.compile(r"^[A-Za-z0-9-]+$")
HOSTNAME = re.compile(
    r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$"
)
PATH = re.compile(r"^(?:\*|/[A-Za-z0-9/_-]*\*?)$")
COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")
SUSPICIOUS_KEY = re.compile(
    r"(?:api[_-]?key|access[_-]?token|authorization|bearer|cookie|password|secret)",
    re.IGNORECASE,
)
INSTRUCTION_VALUE = re.compile(
    r"(?:ignore (?:all |the )?(?:previous|prior) instructions|system prompt|call a tool|run_cli|fluid_api)",
    re.IGNORECASE,
)


def validate_profile(profile: Any) -> list[str]:
    errors: list[str] = []

    def fail(path: str, message: str) -> None:
        errors.append(f"{path}: {message}")

    def exact_keys(value: Any, path: str, required: set[str]) -> bool:
        if not isinstance(value, dict):
            fail(path, "must be an object")
            return False
        actual = set(value)
        for key in sorted(required - actual):
            fail(path, f"missing key {key!r}")
        for key in sorted(actual - required):
            fail(path, f"unknown key {key!r}")
        return actual == required

    def bounded_string(
        value: Any, path: str, maximum: int, pattern: re.Pattern[str]
    ) -> None:
        if not isinstance(value, str) or not (1 <= len(value) <= maximum):
            fail(path, f"must be a string of length 1..{maximum}")
        elif pattern.fullmatch(value) is None:
            fail(path, "has an invalid format")

    def positive_ids(value: Any, path: str) -> None:
        if (
            not isinstance(value, list)
            or not (1 <= len(value) <= 100)
            or any(type(item) is not int or item < 1 for item in value)
            or len(set(value)) != len(value)
        ):
            fail(path, "must contain 1..100 unique positive integer ids")

    def inspect(value: Any, path: str = "$") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if SUSPICIOUS_KEY.search(key):
                    fail(f"{path}.{key}", "credential-like keys are forbidden")
                inspect(child, f"{path}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                inspect(child, f"{path}[{index}]")
        elif isinstance(value, str) and INSTRUCTION_VALUE.search(value):
            fail(path, "instruction-like values are forbidden")

    if not exact_keys(
        profile,
        "$",
        {"schema_version", "profile_id", "company", "portal", "campaign", "storefront"},
    ):
        inspect(profile)
        return errors
    inspect(profile)

    if profile["schema_version"] != 1:
        fail("$.schema_version", "must equal 1")
    bounded_string(profile["profile_id"], "$.profile_id", 80, SLUG)

    company = profile["company"]
    if exact_keys(company, "$.company", {"subdomain", "display_name"}):
        bounded_string(company["subdomain"], "$.company.subdomain", 63, SUBDOMAIN)
        bounded_string(company["display_name"], "$.company.display_name", 120, SAFE_LINE)

    portal = profile["portal"]
    if exact_keys(
        portal,
        "$.portal",
        {"definition_name", "definition_id", "screen_path", "anchor_id"},
    ):
        bounded_string(portal["definition_name"], "$.portal.definition_name", 120, SAFE_LINE)
        if type(portal["definition_id"]) is not int or portal["definition_id"] < 1:
            fail("$.portal.definition_id", "must be a positive integer")
        bounded_string(portal["screen_path"], "$.portal.screen_path", 200, SCREEN)
        bounded_string(portal["anchor_id"], "$.portal.anchor_id", 120, WIDGET_ID)

    campaign = profile["campaign"]
    if exact_keys(campaign, "$.campaign", {"disclosure", "partner_segments", "goals"}):
        bounded_string(campaign["disclosure"], "$.campaign.disclosure", 500, SAFE_LINE)
        for list_key, keys in (
            ("partner_segments", {"id", "label", "audience_noun"}),
            ("goals", {"id", "label"}),
        ):
            values = campaign[list_key]
            if not isinstance(values, list) or not (1 <= len(values) <= 20):
                fail(f"$.campaign.{list_key}", "must contain 1..20 entries")
                continue
            ids: set[str] = set()
            for index, item in enumerate(values):
                path = f"$.campaign.{list_key}[{index}]"
                if not exact_keys(item, path, keys):
                    continue
                bounded_string(item["id"], f"{path}.id", 40, OPTION_ID)
                bounded_string(item["label"], f"{path}.label", 80, SAFE_LINE)
                if "audience_noun" in item:
                    bounded_string(item["audience_noun"], f"{path}.audience_noun", 40, AUDIENCE)
                if item["id"] in ids:
                    fail(f"{path}.id", "must be unique")
                ids.add(item["id"])

    storefront = profile["storefront"]
    if exact_keys(storefront, "$.storefront", {"banner"}):
        banner = storefront["banner"]
        banner_keys = {
            "enabled", "name_prefix", "domain", "path", "country_ids",
            "language_ids", "placement", "behavior", "priority", "styles",
        }
        if exact_keys(banner, "$.storefront.banner", banner_keys):
            if banner["enabled"] is not True:
                fail("$.storefront.banner.enabled", "must equal true in v1")
            bounded_string(banner["name_prefix"], "$.storefront.banner.name_prefix", 80, SLUG)
            bounded_string(banner["domain"], "$.storefront.banner.domain", 253, HOSTNAME)
            bounded_string(banner["path"], "$.storefront.banner.path", 200, PATH)
            positive_ids(banner["country_ids"], "$.storefront.banner.country_ids")
            positive_ids(banner["language_ids"], "$.storefront.banner.language_ids")
            if banner["placement"] not in {"top", "bottom"}:
                fail("$.storefront.banner.placement", "is invalid")
            if banner["behavior"] not in {"dismissible", "sticky", "persistent"}:
                fail("$.storefront.banner.behavior", "is invalid")
            if type(banner["priority"]) is not int or not (0 <= banner["priority"] <= 999):
                fail("$.storefront.banner.priority", "must be an integer from 0..999")
            styles = banner["styles"]
            style_keys = {
                "width", "background_color", "text_color", "button_color",
                "button_text_color", "shadow",
            }
            if exact_keys(styles, "$.storefront.banner.styles", style_keys):
                if styles["width"] not in {"full_width", "contained"}:
                    fail("$.storefront.banner.styles.width", "is invalid")
                if styles["shadow"] not in {"none", "small", "medium", "large"}:
                    fail("$.storefront.banner.styles.shadow", "is invalid")
                for key in ("background_color", "text_color", "button_color", "button_text_color"):
                    bounded_string(styles[key], f"$.storefront.banner.styles.{key}", 7, COLOR)

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_profile.py <profile.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        profile = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"FAIL {path}: {error}", file=sys.stderr)
        return 1
    errors = validate_profile(profile)
    if errors:
        print(f"FAIL {path} ({len(errors)} errors)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"PASS {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
