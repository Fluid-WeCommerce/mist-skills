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
FLAGSHIP_WORKFLOW_PATH = ROOT / "workflows/onboard-launch-company.workflow.json"
FLAGSHIP_CONTRACT_FILES = (
    ROOT / "onboarding/fluid-product-admin-import/SKILL.md",
    ROOT / "onboarding/onboard-launch-company/SKILL.md",
    ROOT / "onboarding/onboarding-prefill/SKILL.md",
    ROOT / "onboarding/onboarding-prefill/references/api-endpoints.md",
    ROOT / "onboarding/onboarding-prefill/references/brand-md.md",
    ROOT / "themes/theme-clone/SKILL.md",
    ROOT / "themes/theme-source-inventory/SKILL.md",
    ROOT / "themes/references/pixel-fidelity-core.md",
    ROOT / "themes/page-clone/references/pixel-perfect-page.md",
    ROOT / "themes/clone-page-to-liquid/SKILL.md",
    ROOT / "themes/clone-home-page/SKILL.md",
    ROOT / "themes/clone-shop-page/SKILL.md",
    ROOT / "themes/clone-product-page/SKILL.md",
    ROOT / "themes/clone-category-page/SKILL.md",
    ROOT / "themes/clone-collection-page/SKILL.md",
    FLAGSHIP_WORKFLOW_PATH,
)


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


def require_fragments(text: str, fragments: tuple[str, ...], label: str) -> None:
    for fragment in fragments:
        if fragment not in text:
            raise CatalogValidationError(
                f"{label}: required contract fragment is missing: {fragment!r}"
            )


def validate_flagship_contracts() -> None:
    banned_fragments = (
        "/api/company/v1/products",
        "/api/company/v1/collections",
        "POST /api/company/pages",
        "POST /api/posts",
        "brand_guidelines has NO font field",
        "There is no `external_asset_url`",
        "does not accept an `external_asset_url`",
        "cowboy.com",
        "Suisse Intl",
    )

    for path in FLAGSHIP_CONTRACT_FILES:
        text = path.read_text(encoding="utf-8")
        for fragment in banned_fragments:
            if fragment in text:
                raise CatalogValidationError(
                    f"{path.relative_to(ROOT)}: stale or fixture-specific "
                    f"contract fragment found: {fragment!r}"
                )

    manifest = load_json(MANIFEST_PATH)
    manifest_skills = {
        entry.get("slug"): entry.get("path")
        for entry in manifest.get("skills", [])
        if isinstance(entry, dict)
    }
    expected_page_skills = {
        "themes/clone-page-to-liquid": "themes/clone-page-to-liquid/SKILL.md",
        "themes/clone-home-page": "themes/clone-home-page/SKILL.md",
        "themes/clone-shop-page": "themes/clone-shop-page/SKILL.md",
        "themes/clone-product-page": "themes/clone-product-page/SKILL.md",
        "themes/clone-category-page": "themes/clone-category-page/SKILL.md",
        "themes/clone-collection-page": "themes/clone-collection-page/SKILL.md",
    }
    for slug, expected_path in expected_page_skills.items():
        if manifest_skills.get(slug) != expected_path:
            raise CatalogValidationError(
                f"manifest must publish {slug!r} at {expected_path!r}"
            )

    product_skill = (
        ROOT / "onboarding/fluid-product-admin-import/SKILL.md"
    ).read_text(encoding="utf-8")
    require_fragments(
        product_skill,
        (
            "/openapi/api-reference/storefront-v2026-04.yaml",
            "/api/v202604/company/products",
            "meta.pagination.next_cursor",
            'status: "active"',
            "Do not send\n  `currency_code`",
            "external_asset_url",
            'product_subscription_plans_attributes:[{"_destroy":true}]',
        ),
        "fluid-product-admin-import",
    )

    brand_reference = (
        ROOT / "onboarding/onboarding-prefill/references/api-endpoints.md"
    ).read_text(encoding="utf-8")
    require_fragments(
        brand_reference,
        (
            '"brand_md":',
            '"fonts":',
            '"name":',
            '"file_url":',
            "external_asset_url",
            "update_brand_voice",
        ),
        "onboarding brand API reference",
    )

    theme_clone_skill = (ROOT / "themes/theme-clone/SKILL.md").read_text(
        encoding="utf-8"
    )
    require_fragments(
        theme_clone_skill,
        (
            'document.querySelectorAll("img,video,video source")',
            "different desktop/mobile video sources",
            "`dam_upload` with its public `url`",
            "`compress_media`",
            "`priority_media`",
            "video is a hard failure",
        ),
        "theme-clone priority media contract",
    )

    source_inventory_skill = (
        ROOT / "themes/theme-source-inventory/SKILL.md"
    ).read_text(encoding="utf-8")
    require_fragments(
        source_inventory_skill,
        (
            "evidence_run_started_at",
            "30 minutes after it",
            "union of all six rendered sidecars",
            "build_theme_source_inventory",
            "documents.html",
            "path/SHA-256/byte-length receipts",
            "`SOURCE_INVENTORY_BUILD: written`",
            "`SOURCE_INVENTORY_VALIDATION: pass`",
            "validate_theme_source_inventory",
        ),
        "theme source-inventory contract",
    )

    page_contract = (
        ROOT / "themes/page-clone/references/pixel-perfect-page.md"
    ).read_text(encoding="utf-8")
    require_fragments(
        page_contract,
        (
            "source_copy_sha256",
            "`stable`, `resource`, `dynamic`, or `external`",
            'dam_upload({ url: "<exact-public-url>", create_media: true })',
            "compress_media",
            "`currentSrc`",
            "`read_preview_dom",
            "signed Agent Surface receipt",
            'geometry_mode:"diagnostic"',
            'media_mode:"diagnostic"',
            "A successful diagnostic call",
            "failed/refused `interact_preview`",
            "tool_failures:[]",
            "page-type reviewer",
            "Do not use a universal minor-count or geometry percentage",
            'status:"pass"|"needs_adjudication"|"blocked"',
        ),
        "shared pixel-perfect page contract",
    )

    universal_page_skill = (
        ROOT / "themes/clone-page-to-liquid/SKILL.md"
    ).read_text(encoding="utf-8")
    require_fragments(
        universal_page_skill,
        (
            "This skill owns visual reconstruction only",
            "page_contract",
            "data_contract",
            "`stable`",
            "`resource`",
            "`dynamic`",
            "`external`",
            'copy_mode:"exact"',
            'copy_mode:"diagnostic"',
            'geometry_mode:"diagnostic"',
            'media_mode:"diagnostic"',
            "Diagnostic comparison success",
            "failed or refused page-contract interaction",
            "tool_failures:[]",
            "independent reviewer",
            'status:"pass"|"needs_adjudication"|"blocked"',
        ),
        "universal page-to-Liquid skill",
    )

    specialist_contracts = {
        "themes/clone-home-page/SKILL.md": (
            'run_skill("themes/clone-page-to-liquid")',
            "Home semantics",
        ),
        "themes/clone-shop-page/SKILL.md": (
            'run_skill("themes/clone-page-to-liquid")',
            "Do not start, await, or grade a complete product import",
        ),
        "themes/clone-product-page/SKILL.md": (
            'run_skill("themes/clone-page-to-liquid")',
            "bulk catalog import",
            "canonical product-data/add-to-cart section",
        ),
        "themes/clone-category-page/SKILL.md": (
            'run_skill("themes/clone-page-to-liquid")',
            "do not await a complete catalog",
            "`category_index`",
            "`category_showcase`",
        ),
        "themes/clone-collection-page/SKILL.md": (
            'run_skill("themes/clone-page-to-liquid")',
            "page-copy prerequisite",
            "`collection_index`",
            "`collection_showcase`",
        ),
    }
    for relative_path, fragments in specialist_contracts.items():
        require_fragments(
            (ROOT / relative_path).read_text(encoding="utf-8"),
            fragments,
            f"{relative_path} specialist contract",
        )

    workflow = load_json(FLAGSHIP_WORKFLOW_PATH)
    if not isinstance(workflow, dict) or not isinstance(workflow.get("steps"), list):
        raise CatalogValidationError("flagship workflow steps must be an array")

    steps = {
        step.get("id"): step
        for step in workflow["steps"]
        if isinstance(step, dict) and isinstance(step.get("id"), str)
    }
    theme_discovery = steps.get("theme-scrape-inventory")
    if not isinstance(theme_discovery, dict):
        raise CatalogValidationError(
            "flagship workflow: theme-scrape-inventory step is missing"
        )
    theme_discovery_acceptance = json.dumps(
        theme_discovery.get("acceptance", [])
    )
    if theme_discovery.get("model") != "google/gemini-3.6-flash":
        raise CatalogValidationError(
            "flagship workflow: bounded source discovery must use "
            "google/gemini-3.6-flash; catalog indexing is now a separate "
            "server-paginated step, so this gate cannot infer product ids"
        )
    require_fragments(
        theme_discovery_acceptance,
        (
            "priority_media",
            "all 24 fresh files",
            "opens the manifest plus all six manifest-recorded HTML files",
            "SOURCE_INVENTORY_VALIDATION: pass",
            "Catalog reconciliation and DAM delivery are intentionally not graded here",
        ),
        "flagship workflow source discovery",
    )
    require_fragments(
        str(theme_discovery.get("prompt", "")),
        (
            'run_skill("themes/theme-source-inventory")',
            "build_theme_source_inventory",
            "validate_theme_source_inventory",
            "Do not load the all-phases theme-clone skill",
        ),
        "flagship workflow source discovery skill boundary",
    )

    theme_catalog = steps.get("theme-catalog-index")
    theme_media = steps.get("theme-media-inventory")
    theme_tokens = steps.get("theme-tokens-skeleton")
    if (
        not isinstance(theme_catalog, dict)
        or not isinstance(theme_media, dict)
        or not isinstance(theme_tokens, dict)
    ):
        raise CatalogValidationError(
            "flagship workflow: split catalog, media, and token steps are required"
        )
    if theme_catalog.get("dependsOn") != ["theme-scrape-inventory"]:
        raise CatalogValidationError(
            "flagship workflow: catalog index must wait for source discovery"
        )
    if theme_media.get("dependsOn") != ["theme-catalog-index"]:
        raise CatalogValidationError(
            "flagship workflow: media delivery must wait for the complete catalog index"
        )
    if theme_tokens.get("dependsOn") != ["theme-media-inventory"]:
        raise CatalogValidationError(
            "flagship workflow: theme tokens must wait for media delivery"
        )
    require_fragments(
        json.dumps(theme_catalog),
        (
            "fluid-catalog-index.json",
            "page[limit]=100",
            "meta.pagination.next_cursor",
            "complete:true",
            "first, middle, and last",
            "No product id or continuation was inferred",
        ),
        "flagship workflow catalog index",
    )
    require_fragments(
        json.dumps(theme_media),
        (
            "dam_upload(url=<exact public source>,create_media=true)",
            "external_asset_url",
            "compress_media",
            "theme_dam_fidelity_fallback",
            "video content type",
            "No id was inferred",
        ),
        "flagship workflow media delivery",
    )

    home_step = steps.get("theme-homepage")
    shop_step = steps.get("theme-shop-page")
    if not isinstance(home_step, dict) or not isinstance(shop_step, dict):
        raise CatalogValidationError(
            "flagship workflow: home and shop golden-route steps are required"
        )
    if home_step.get("skill") != "themes/clone-home-page":
        raise CatalogValidationError(
            "flagship workflow: theme-homepage must use themes/clone-home-page"
        )
    if shop_step.get("skill") != "themes/clone-shop-page":
        raise CatalogValidationError(
            "flagship workflow: theme-shop-page must use themes/clone-shop-page"
        )
    if shop_step.get("dependsOn") != ["theme-homepage"]:
        raise CatalogValidationError(
            "flagship workflow: shop must wait for home without blocking on "
            "the complete product import"
        )
    for step_id, step in (
        ("theme-homepage", home_step),
        ("theme-shop-page", shop_step),
    ):
        required_tools = json.dumps(step.get("qa", {}).get("requiredTools", []))
        require_fragments(
            required_tools,
            (
                '"tool": "crawl"',
                '"minSuccessfulCalls": 2',
                '"formats": ["html", "screenshot"]',
                '"screenshot_options.viewport.width"',
                '"tool": "read_preview_dom"',
                '"tool": "compare_preview_to_source"',
                '"width": 1440',
                '"height": 900',
                '"width": 390',
                '"height": 844',
                '"mode": "full"',
                '"copy_mode": "diagnostic"',
                '"geometry_mode": "diagnostic"',
                '"media_mode": "diagnostic"',
                '"tool": "interact_preview"',
            ),
            f"flagship workflow {step_id} evidence floor",
        )
        if step.get("qa", {}).get("model") != "google/gemini-3.6-flash":
            raise CatalogValidationError(
                f"flagship workflow: {step_id} bounded page QA must use "
                "google/gemini-3.6-flash"
            )
        require_fragments(
            json.dumps(step.get("acceptance", [])),
            (
                "stable",
                "resource/dynamic/external",
                "signed compare_preview_to_source",
                "independent",
                "needs_adjudication",
                "blocked",
            ),
            f"flagship workflow {step_id} specialist gate",
        )

    product_page_step = steps.get("theme-product-page")
    collection_page_step = steps.get("theme-collection-page")
    if not isinstance(product_page_step, dict) or not isinstance(
        collection_page_step, dict
    ):
        raise CatalogValidationError(
            "flagship workflow: separate product and collection page steps "
            "are required"
        )
    if product_page_step.get("skill") != "themes/clone-product-page":
        raise CatalogValidationError(
            "flagship workflow: product page must use themes/clone-product-page"
        )
    if collection_page_step.get("skill") != "themes/clone-collection-page":
        raise CatalogValidationError(
            "flagship workflow: collection page must use "
            "themes/clone-collection-page"
        )
    if product_page_step.get("dependsOn") != ["theme-shop-page"]:
        raise CatalogValidationError(
            "flagship workflow: PDP must wait for shop without blocking on "
            "the complete product import"
        )
    if collection_page_step.get("dependsOn") != ["theme-product-page"]:
        raise CatalogValidationError(
            "flagship workflow: collection page must wait for the PDP page step"
        )

    for step_id, theme_step in (
        ("theme-product-page", product_page_step),
        ("theme-collection-page", collection_page_step),
    ):
        required_tools = json.dumps(theme_step.get("qa", {}).get("requiredTools", []))
        require_fragments(
            required_tools,
            (
                '"tool": "crawl"',
                '"minSuccessfulCalls": 2',
                '"tool": "compare_preview_to_source"',
                '"copy_mode": "diagnostic"',
                '"geometry_mode": "diagnostic"',
                '"media_mode": "diagnostic"',
                '"tool": "read_preview_dom"',
                '"tool": "interact_preview"',
            ),
            f"flagship workflow {step_id} evidence floor",
        )
        if theme_step.get("qa", {}).get("model") != "google/gemini-3.6-flash":
            raise CatalogValidationError(
                f"flagship workflow: {step_id} bounded page QA must use "
                "google/gemini-3.6-flash"
            )
        require_fragments(
            json.dumps(theme_step.get("acceptance", [])),
            (
                "stable",
                "resource/dynamic/external",
                "signed compare_preview_to_source",
                "needs_adjudication",
                "blocked",
            ),
            f"flagship workflow {step_id} specialist gate",
        )

    content_pages_step = steps.get("theme-content-pages-push")
    if not isinstance(content_pages_step, dict):
        raise CatalogValidationError(
            "flagship workflow: theme-content-pages-push step is missing"
        )
    if content_pages_step.get("dependsOn") != ["theme-collection-page"]:
        raise CatalogValidationError(
            "flagship workflow: content/push must wait for the collection page"
        )
    require_fragments(
        json.dumps(content_pages_step.get("acceptance", [])),
        (
            "priority",
            "video",
            "HARD-FAIL BAR",
        ),
        "flagship workflow theme-content-pages-push",
    )

    for removed_step_id in ("theme-product-collection",):
        if removed_step_id in steps:
            raise CatalogValidationError(
                f"flagship workflow: obsolete combined step {removed_step_id} "
                "must be split into page-type specialists"
            )

    products_import = steps.get("products-import")
    if not isinstance(products_import, dict):
        raise CatalogValidationError("flagship workflow: products-import step is missing")
    product_prompt = products_import.get("prompt")
    if not isinstance(product_prompt, str):
        raise CatalogValidationError(
            "flagship workflow: products-import prompt must be a string"
        )
    require_fragments(
        product_prompt,
        (
            'run_skill("fluid-product-admin-import")',
            "/api/v202604/company/products",
            "meta.pagination.next_cursor",
            'status:"active"',
            "external_asset_url",
            "manifest_sha256",
        ),
        "flagship workflow products-import",
    )
    product_acceptance = json.dumps(products_import.get("acceptance", []))
    require_fragments(
        product_acceptance,
        ('product_subscription_plans_attributes:[{\\"_destroy\\":true}]',),
        "flagship workflow products-import acceptance",
    )

    content_import = steps.get("content-import")
    if not isinstance(content_import, dict):
        raise CatalogValidationError("flagship workflow: content-import step is missing")
    content_prompt = content_import.get("prompt")
    if not isinstance(content_prompt, str):
        raise CatalogValidationError(
            "flagship workflow: content-import prompt must be a string"
        )
    require_fragments(
        content_prompt,
        (
            'run_skill("fluid-product-admin-import")',
            "/api/v202604/company/collections",
            "create_page",
            "meta.pagination.next_cursor",
        ),
        "flagship workflow content-import",
    )


def main() -> int:
    try:
        skill_count, workflow_count = validate_manifest(load_json(MANIFEST_PATH))
        validate_flagship_contracts()
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
