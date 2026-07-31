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
STREAMLINED_WORKFLOW_PATH = (
    ROOT / "workflows/streamlined-onboard-launch.workflow.json"
)
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


# Models permitted for the two gates that were previously pinned to a single id.
# Cross-vendor review is still enforced separately; these sets only widen WHICH
# model may hold a role, so the choice can be settled by measured runs rather
# than frozen into the validator.
SOURCE_DISCOVERY_MODELS = {
    "google/gemini-3.6-flash",
    "openai/gpt-5.6-sol",
    "anthropic/claude-opus-5",
}
PAGE_QA_MODELS = {
    "google/gemini-3.6-flash",
    "openai/gpt-5.6-sol",
    "anthropic/claude-opus-5",
}


def depends_transitively(steps: dict, start: str, target: str) -> bool:
    """True when `start` cannot run until `target` has run.

    Ordering rules below assert "X waits for Y". Asserting that as a literal
    dependsOn list makes the chain unextendable: inserting a legitimate step
    between X and Y breaks a rule that is still satisfied. Walk the graph
    instead so the invariant survives new steps in the middle.
    """
    seen: set[str] = set()
    frontier = [start]
    while frontier:
        current = frontier.pop()
        if current in seen:
            continue
        seen.add(current)
        step = steps.get(current)
        if not isinstance(step, dict):
            continue
        for dependency in step.get("dependsOn") or []:
            if dependency == target:
                return True
            frontier.append(dependency)
    return False


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


def normalize_streamlined_catalog_artifacts(
    identity_index_jsonl: str,
    enriched_records: list[dict[str, Any]],
    *,
    source_market_iso: str,
) -> dict[str, Any]:
    """Normalize the workflow's separate discovery and enrichment artifacts.

    The runtime workflow uses the same invariant when it finalizes its import
    manifest: discovery rows are an ordered denominator, while enriched
    records are one-per-identity state. They are not two event shapes appended
    to one JSONL stream.
    """

    identities: list[dict[str, Any]] = []
    seen_identities: set[str] = set()
    seen_handles: set[str] = set()
    for line_number, line in enumerate(identity_index_jsonl.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            identity = json.loads(line, object_pairs_hook=reject_duplicate_keys)
        except (json.JSONDecodeError, CatalogValidationError) as error:
            raise CatalogValidationError(
                f"catalog identity index line {line_number}: {error}"
            ) from error
        if not isinstance(identity, dict):
            raise CatalogValidationError(
                f"catalog identity index line {line_number} must be an object"
            )
        source_id = identity.get("source_id")
        source_handle = identity.get("source_handle")
        if not isinstance(source_id, str) or not source_id.strip():
            raise CatalogValidationError(
                f"catalog identity index line {line_number} has no source_id"
            )
        if not isinstance(source_handle, str) or not source_handle.strip():
            raise CatalogValidationError(
                f"catalog identity index line {line_number} has no source_handle"
            )
        if source_id in seen_identities:
            raise CatalogValidationError(
                f"duplicate catalog identity index row: {source_id}"
            )
        if source_handle in seen_handles:
            raise CatalogValidationError(
                f"duplicate catalog identity handle: {source_handle}"
            )
        seen_identities.add(source_id)
        seen_handles.add(source_handle)
        identities.append(identity)

    required_product_fields = {
        "source_id",
        "source_url",
        "source_handle",
        "title",
        "description",
        "price",
        "currency",
        "image_urls",
        "option_axes",
        "variants",
    }
    records_by_identity: dict[str, dict[str, Any]] = {}
    record_handles: set[str] = set()
    for record in enriched_records:
        if not isinstance(record, dict):
            raise CatalogValidationError("enriched catalog record must be an object")
        source_id = record.get("source_id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise CatalogValidationError("enriched catalog record has no source_id")
        if source_id in records_by_identity:
            raise CatalogValidationError(
                f"duplicate enriched record for source identity: {source_id}"
            )
        missing_fields = sorted(required_product_fields - record.keys())
        variants = record.get("variants")
        image_urls = record.get("image_urls")
        source_handle = record.get("source_handle")
        if (
            missing_fields
            or not isinstance(record.get("source_url"), str)
            or not isinstance(source_handle, str)
            or not isinstance(record.get("title"), str)
            or not isinstance(record.get("description"), str)
            or not isinstance(record.get("price"), str)
            or not isinstance(record.get("currency"), str)
            or not isinstance(record.get("option_axes"), dict)
            or not isinstance(variants, list)
            or not variants
            or not isinstance(image_urls, list)
            or not all(isinstance(image_url, str) for image_url in image_urls)
            or not all(
                isinstance(variant, dict)
                and isinstance(variant.get("source_variant_id"), str)
                and isinstance(variant.get("options"), list)
                and isinstance(variant.get("price"), str)
                for variant in variants
            )
        ):
            detail = (
                f"; missing fields: {', '.join(missing_fields)}"
                if missing_fields
                else ""
            )
            raise CatalogValidationError(
                f"enriched record {source_id} is not importer-complete{detail}"
            )
        if source_handle in record_handles:
            raise CatalogValidationError(
                f"duplicate enriched source handle: {source_handle}"
            )
        record_handles.add(source_handle)
        records_by_identity[source_id] = record

    index_ids = [identity["source_id"] for identity in identities]
    missing_records = [
        source_id for source_id in index_ids if source_id not in records_by_identity
    ]
    extra_records = sorted(set(records_by_identity) - set(index_ids))
    if missing_records or extra_records:
        raise CatalogValidationError(
            "catalog artifact identities do not balance: "
            f"missing={missing_records}, extra={extra_records}"
        )

    for identity in identities:
        source_id = identity["source_id"]
        record = records_by_identity[source_id]
        for identity_field in ("source_url", "source_handle"):
            if record.get(identity_field) != identity.get(identity_field):
                raise CatalogValidationError(
                    f"enriched record {source_id} disagrees with identity index "
                    f"field {identity_field}"
                )

    return {
        "source_market_iso": source_market_iso,
        "products": [records_by_identity[source_id] for source_id in index_ids],
        "excluded": [],
        "unresolved": [],
    }


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

    page_reference = (
        ROOT / "themes/page-clone/references/pixel-perfect-page.md"
    ).read_text(encoding="utf-8")
    require_fragments(
        page_reference,
        (
            "baseline_admissibility",
            "contaminated",
            "repeated fixed overlays",
        ),
        "pixel-perfect-page",
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
    # Source discovery is the heaviest-context step in the workflow: it opens
    # rendered ecommerce HTML plus durable screenshots and must hold them while
    # building a signed inventory. Pinning it to the cheapest model produced 13
    # hard failures and 5 context overflows across 58 recorded runs, so the gate
    # is an allowlist of models known to hold that context, not a single id.
    if theme_discovery.get("model") not in SOURCE_DISCOVERY_MODELS:
        raise CatalogValidationError(
            "flagship workflow: bounded source discovery must use one of "
            f"{sorted(SOURCE_DISCOVERY_MODELS)}; catalog indexing is now a "
            "separate server-paginated step, so this gate cannot infer product ids"
        )
    require_fragments(
        theme_discovery_acceptance,
        (
            "priority_media",
            "deferred-to-page-specialist",
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
                '"tool": "view_project_image"',
                '"tool": "interact_preview"',
            ),
            f"flagship workflow {step_id} evidence floor",
        )
        image_requirements = [
            requirement
            for requirement in step.get("qa", {}).get("requiredTools", [])
            if requirement.get("tool") == "view_project_image"
        ]
        if not any(
            requirement.get("minSuccessfulCalls") == 2
            and requirement.get("distinctBy") == ["path"]
            for requirement in image_requirements
        ):
            raise CatalogValidationError(
                f"flagship workflow: {step_id} QA must open two distinct "
                "durable source images"
            )
        if step.get("qa", {}).get("model") not in PAGE_QA_MODELS:
            raise CatalogValidationError(
                f"flagship workflow: {step_id} bounded page QA must use one of "
                f"{sorted(PAGE_QA_MODELS)}"
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
                '"tool": "view_project_image"',
                '"tool": "read_preview_dom"',
                '"tool": "interact_preview"',
            ),
            f"flagship workflow {step_id} evidence floor",
        )
        image_requirements = [
            requirement
            for requirement in theme_step.get("qa", {}).get("requiredTools", [])
            if requirement.get("tool") == "view_project_image"
        ]
        if not any(
            requirement.get("minSuccessfulCalls") == 2
            and requirement.get("distinctBy") == ["path"]
            for requirement in image_requirements
        ):
            raise CatalogValidationError(
                f"flagship workflow: {step_id} QA must open two distinct "
                "durable source images"
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
    if not depends_transitively(
        steps, "theme-content-pages-push", "theme-collection-page"
    ):
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


def validate_streamlined_product_import_contract() -> None:
    workflow = load_json(STREAMLINED_WORKFLOW_PATH)
    if not isinstance(workflow, dict) or not isinstance(workflow.get("steps"), list):
        raise CatalogValidationError("streamlined workflow steps must be an array")

    steps = {
        step.get("id"): step
        for step in workflow["steps"]
        if isinstance(step, dict) and isinstance(step.get("id"), str)
    }
    catalog_manifest = steps.get("catalog-manifest")
    products_import = steps.get("import-products")
    if not isinstance(catalog_manifest, dict):
        raise CatalogValidationError(
            "streamlined workflow: catalog-manifest step is missing"
        )
    if "manifest_sha256" not in str(catalog_manifest.get("prompt", "")):
        raise CatalogValidationError(
            "streamlined workflow: catalog-manifest must expose its SHA-256 "
            "to import-products"
        )
    if not isinstance(products_import, dict):
        raise CatalogValidationError(
            "streamlined workflow: import-products step is missing"
        )
    if products_import.get("dependsOn") != ["catalog-manifest"]:
        raise CatalogValidationError(
            "streamlined workflow: import-products must wait for catalog-manifest"
        )
    if products_import.get("model") != "google/gemini-3.6-flash":
        raise CatalogValidationError(
            "streamlined workflow: import-products must use "
            "google/gemini-3.6-flash"
        )
    if products_import.get("maxReworkRounds") != 0:
        raise CatalogValidationError(
            "streamlined workflow: deterministic product imports must not rework"
        )
    if "skill" in products_import:
        raise CatalogValidationError(
            "streamlined workflow: import-products must use its inline tool prompt"
        )

    prompt = products_import.get("prompt")
    if not isinstance(prompt, str):
        raise CatalogValidationError(
            "streamlined workflow: import-products prompt must be a string"
        )
    require_fragments(
        prompt,
        (
            "manifest_path",
            "manifest_sha256",
            "exactly once",
            "write mode",
            "compact receipt",
            "status: complete",
            "catalog-manifest STEP_OUTPUT",
        ),
        "streamlined workflow import-products",
    )
    if prompt.count("fluid_product_import") != 1:
        raise CatalogValidationError(
            "streamlined workflow: work prompt must contain exactly one "
            "fluid_product_import invocation"
        )
    for banned_tool in ("fluid_api", "dam_upload"):
        if banned_tool in prompt:
            raise CatalogValidationError(
                "streamlined workflow: import-products must not direct the "
                f"model to call {banned_tool}"
            )

    qa = products_import.get("qa")
    expected_requirement = {
        "tool": "fluid_product_import",
        "input": {"verify_only": True},
        "minSuccessfulCalls": 1,
    }
    if not isinstance(qa, dict) or qa.get("enabled") is not True:
        raise CatalogValidationError(
            "streamlined workflow: import-products independent QA must be enabled"
        )
    if qa.get("model") != "google/gemini-3.6-flash":
        raise CatalogValidationError(
            "streamlined workflow: import-products QA must use "
            "google/gemini-3.6-flash"
        )
    if qa.get("strictness") != "standard":
        raise CatalogValidationError(
            "streamlined workflow: import-products QA must remain standard"
        )
    if qa.get("onFail") != "stop":
        raise CatalogValidationError(
            "streamlined workflow: import-products QA must stop publication on failure"
        )
    if qa.get("requiredTools") != [expected_requirement]:
        raise CatalogValidationError(
            "streamlined workflow: import-products QA must require one "
            "verify-only fluid_product_import call"
        )

    acceptance = json.dumps(products_import.get("acceptance", []))
    require_fragments(
        acceptance,
        (
            "exactly one live Fluid product",
            "no duplicates, no silent drops",
            "identity-level verification",
            "does not prove full field fidelity",
        ),
        "streamlined workflow import-products verification boundary",
    )


def validate_streamlined_catalog_closure_contract(workflow: Any) -> None:
    if not isinstance(workflow, dict) or not isinstance(workflow.get("steps"), list):
        raise CatalogValidationError("streamlined workflow steps must be an array")

    steps = {
        step.get("id"): step
        for step in workflow["steps"]
        if isinstance(step, dict) and isinstance(step.get("id"), str)
    }
    ledger = steps.get("preview-product-ledger")
    if not isinstance(ledger, dict):
        raise CatalogValidationError(
            "streamlined workflow: preview-product-ledger step is missing"
        )
    ledger_prompt = ledger.get("prompt")
    if not isinstance(ledger_prompt, str):
        raise CatalogValidationError(
            "streamlined workflow: preview-product-ledger prompt must be a string"
        )
    require_fragments(
        ledger_prompt,
        (
            "/api/v202604/company/products?page[limit]=100",
            "meta.pagination.next_cursor",
            "run_id",
            "baseline_product_ids",
            "preview_product_ledger_dir",
            "SHA-256",
            "read-only",
        ),
        "streamlined workflow preview-product-ledger contract",
    )
    ledger_qa = ledger.get("qa")
    if (
        ledger.get("dependsOn") != ["import-products"]
        or not isinstance(ledger_qa, dict)
        or ledger_qa.get("enabled") is not True
        or ledger_qa.get("strictness") != "standard"
        or ledger_qa.get("onFail") != "stop"
    ):
        raise CatalogValidationError(
            "streamlined workflow: preview-product-ledger must wait for import-products "
            "and fail closed"
        )

    home = steps.get("home-page")
    if not isinstance(home, dict) or set(home.get("dependsOn") or []) != {
        "source-capture",
        "preview-product-ledger",
    }:
        raise CatalogValidationError(
            "streamlined workflow: home-page must wait for preview-product-ledger and source-capture"
        )

    catalog_manifest = steps.get("catalog-manifest")
    if not isinstance(catalog_manifest, dict):
        raise CatalogValidationError(
            "streamlined workflow: catalog-manifest step is missing"
        )
    if catalog_manifest.get("dependsOn") != ["source-capture"]:
        raise CatalogValidationError(
            "streamlined workflow: catalog-manifest must wait for source-capture"
        )
    require_fragments(
        str(catalog_manifest.get("prompt", "")),
        (
            "clone-manifest.json",
            "distinct product or shop origin",
            "union",
        ),
        "streamlined workflow catalog-manifest source-union contract",
    )
    require_fragments(
        str(catalog_manifest.get("prompt", "")),
        (
            "catalog-identities.jsonl",
            "catalog-records/",
            "catalog-manifest.json",
            "Never append an enriched product row to catalog-identities.jsonl",
            "one importer-complete record per identity",
            "atomically",
        ),
        "streamlined workflow catalog artifact separation contract",
    )

    products_import = steps.get("import-products")
    if not isinstance(products_import, dict) or products_import.get(
        "dependsOn"
    ) != ["catalog-manifest"]:
        raise CatalogValidationError(
            "streamlined workflow: import-products must wait for catalog-manifest"
        )
    import_qa = products_import.get("qa")
    if not isinstance(import_qa, dict) or import_qa.get("onFail") != "stop":
        raise CatalogValidationError(
            "streamlined workflow: import-products must stop publication when QA fails"
        )

    gate = steps.get("preview-product-gate")
    if not isinstance(gate, dict):
        raise CatalogValidationError(
            "streamlined workflow: preview-product-gate step is missing"
        )
    if set(gate.get("dependsOn") or []) != {
        "preview-product-ledger",
        "shop-page",
        "product-page",
        "collection-page",
        "content-pages",
    }:
        raise CatalogValidationError(
            "streamlined workflow: preview-product-gate must wait for the ledger "
            "and every product-capable page step"
        )
    gate_prompt = gate.get("prompt")
    if not isinstance(gate_prompt, str):
        raise CatalogValidationError(
            "streamlined workflow: preview-product-gate prompt must be a string"
        )
    require_fragments(
        gate_prompt,
        (
            "baseline_product_ids",
            "/api/v202604/company/products?page[limit]=100",
            "meta.pagination.next_cursor",
            "fluid_product_id",
            "preview_product_ledger_path",
            "preview-product-remediation-plan.json",
            "status: BLOCKED",
            "any run-created product",
            "run_created_products == 0",
            "Do not call fluid_product_import",
            "do not create, update, publish, unpublish, or delete products",
        ),
        "streamlined workflow zero-tolerance preview-product gate contract",
    )
    for banned_claim in (
        "both directions",
        "closed_manifest_path",
        "closed_manifest_sha256",
        "fully enrich it",
    ):
        if banned_claim in gate_prompt:
            raise CatalogValidationError(
                "streamlined workflow: preview-product-gate must not claim "
                f"unsupported reconciliation via {banned_claim!r}"
            )
    gate_qa = gate.get("qa")
    if (
        not isinstance(gate_qa, dict)
        or gate_qa.get("enabled") is not True
        or gate_qa.get("strictness") != "standard"
        or gate_qa.get("onFail") != "stop"
    ):
        raise CatalogValidationError(
            "streamlined workflow: preview-product-gate must be a fail-closed gate"
        )
    require_fragments(
        json.dumps(gate.get("acceptance", [])),
        (
            "every product id absent from the post-import baseline",
            "blocks publication",
            "zero run-created products",
            "remediation plan",
        ),
        "streamlined workflow preview-product-gate acceptance contract",
    )

    for page_step_id in (
        "home-page",
        "shop-page",
        "product-page",
        "collection-page",
        "content-pages",
    ):
        if not depends_transitively(steps, page_step_id, "import-products"):
            raise CatalogValidationError(
                f"streamlined workflow: {page_step_id} must wait for canonical product import"
            )

    publish = steps.get("publish-theme")
    publish_dependencies = publish.get("dependsOn") if isinstance(publish, dict) else []
    if "preview-product-gate" not in (publish_dependencies or []):
        raise CatalogValidationError(
            "streamlined workflow: publish-theme must wait for preview-product-gate"
        )
    if "import-products" not in (publish_dependencies or []):
        raise CatalogValidationError(
            "streamlined workflow: publish-theme must wait for import-products"
        )


def _validate_streamlined_home_review_contract(workflow: Any) -> None:
    if not isinstance(workflow, dict) or not isinstance(workflow.get("steps"), list):
        raise CatalogValidationError("streamlined workflow steps must be an array")

    home_step = next(
        (
            step
            for step in workflow["steps"]
            if isinstance(step, dict) and step.get("id") == "home-page"
        ),
        None,
    )
    if not isinstance(home_step, dict):
        raise CatalogValidationError("streamlined workflow: home-page step is missing")
    if "skill" in home_step:
        raise CatalogValidationError(
            "streamlined workflow: home-page must use its inline code-review prompt"
        )
    prompt = home_step.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise CatalogValidationError(
            "streamlined workflow: home-page prompt must be a non-empty string"
        )
    require_fragments(
        prompt,
        (
            "clone-manifest.json",
            "retained source HTML",
            "source CSS",
            "resolved landmark styles",
            "exact stable copy",
            "optional, non-authoritative design input only",
            "open only the retained source screenshot paths",
            "Fluid Liquid data",
            "shared shell",
            "multiple named Liquid sections",
            "monolithic page-sized section",
            "base-theme scaffold filler",
            "inline binary media",
            "hardcoded development theme ids",
            "layout-hiding hacks",
            "fluid theme lint --json",
            "read the rendered DOM",
            "browser console",
            "local server logs",
            "priority_media.items",
            "theme_media_reconcile",
            'mode: "theme_only"',
            ".mist-desktop/home-catalog-index.json",
            "priority_media.delivery_items",
        ),
        "streamlined workflow home-page implementation contract",
    )
    qa = home_step.get("qa")
    if (
        set(home_step.get("dependsOn") or [])
        != {"source-capture", "preview-product-ledger"}
        or home_step.get("maxReworkRounds") != 1
        or not isinstance(qa, dict)
        or qa.get("enabled") is not True
        or qa.get("strictness") != "lenient"
        or qa.get("onFail") != "continue"
    ):
        raise CatalogValidationError(
            "streamlined workflow: home-page must preserve its ledger-aware "
            "lenient fail-open contract"
        )
    expected_qa_tools = [
        {
            "tool": "run_cli",
            "input": {
                "command": "fluid",
                "args": ["theme", "lint", "--json"],
            },
            "minSuccessfulCalls": 1,
        },
        {
            "tool": "read_file",
            "input": {"path": "clone-manifest.json"},
        },
        {
            "tool": "read_file",
            "input": {"path": "home_page/default/index.liquid"},
        },
        {
            "tool": "read_file",
            "minSuccessfulCalls": 4,
            "distinctBy": ["path"],
        },
        {
            "tool": "search_files",
            "minSuccessfulCalls": 2,
            "distinctBy": ["query"],
        },
        {
            "tool": "read_preview_dom",
            "input": {"path": "/", "mode": "all"},
            "minSuccessfulCalls": 1,
        },
        {
            "tool": "read_preview_console",
            "minSuccessfulCalls": 1,
        },
        {
            "tool": "read_local_server_logs",
            "minSuccessfulCalls": 1,
        },
    ]
    if qa.get("requiredTools") != expected_qa_tools:
        raise CatalogValidationError(
            "streamlined workflow: home-page must require only its deterministic "
            "QA evidence floor"
        )
    acceptance = json.dumps(home_step.get("acceptance", []))
    if "horizontal overflow" in f"{prompt} {acceptance}":
        raise CatalogValidationError(
            "streamlined workflow: home-page review claims unsupported DOM evidence"
        )
    require_fragments(
        acceptance,
        (
            "clone-manifest.json",
            "at least three distinct implementation files",
            "fluid theme lint --json",
            "Targeted code searches",
            "multiple named section mounts",
            "exact stable source copy",
            "Fluid-backed resource/dynamic bindings",
            "shared-shell reuse",
            "no base-theme scaffold filler",
            "inline binary media",
            "hardcoded environment identity",
            "monolithic page-sized section",
            "layout-hiding workaround",
            "local rendered DOM for / in all mode",
            "preview console and local server logs",
            "Screenshots are optional source-design context only",
            "completed priority_media reconciliation",
            "verified DAM delivery URLs",
        ),
        "streamlined workflow home-page review acceptance contract",
    )

    source_capture = next(
        (
            step
            for step in workflow["steps"]
            if isinstance(step, dict) and step.get("id") == "source-capture"
        ),
        None,
    )
    source_prompt = (
        source_capture.get("prompt") if isinstance(source_capture, dict) else None
    )
    if not isinstance(source_prompt, str):
        raise CatalogValidationError(
            "streamlined workflow: source evidence contract is missing"
        )
    require_fragments(
        source_prompt,
        (
            'formats ["html", "rawHtml", "screenshot"]',
            "capturePageEvidence: true",
            "desktop AND at 390 wide",
        ),
        "streamlined workflow source evidence contract",
    )


def _streamlined_step(workflow: dict[str, Any], step_id: str) -> dict[str, Any]:
    step = next(
        (
            step
            for step in workflow["steps"]
            if isinstance(step, dict) and step.get("id") == step_id
        ),
        None,
    )
    if not isinstance(step, dict):
        raise CatalogValidationError(
            f"streamlined workflow: {step_id} step is missing"
        )
    return step


def _deterministic_page_qa_tools(
    template_path: str | None,
    *,
    minimum_reads: int = 4,
    minimum_searches: int = 2,
    minimum_routes: int = 1,
    mandatory_paths: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = [
        {
            "tool": "run_cli",
            "input": {
                "command": "fluid",
                "args": ["theme", "lint", "--json"],
            },
            "minSuccessfulCalls": 1,
        },
        {
            "tool": "read_file",
            "input": {"path": "clone-manifest.json"},
        },
    ]
    if template_path is not None:
        tools.append({"tool": "read_file", "input": {"path": template_path}})
    tools.extend(
        [
            *[
                {"tool": "read_file", "input": {"path": path}}
                for path in mandatory_paths
            ],
            {
                "tool": "read_file",
                "minSuccessfulCalls": minimum_reads,
                "distinctBy": ["path"],
            },
            {
                "tool": "search_files",
                "minSuccessfulCalls": minimum_searches,
                "distinctBy": ["query"],
            },
            {
                "tool": "read_preview_dom",
                "input": {"mode": "all"},
                "minSuccessfulCalls": minimum_routes,
                "distinctBy": ["path"],
            },
            {
                "tool": "read_preview_console",
                "minSuccessfulCalls": 1,
            },
            {
                "tool": "read_local_server_logs",
                "minSuccessfulCalls": 1,
            },
        ]
    )
    return tools


def _validate_direct_page_review(
    workflow: dict[str, Any],
    *,
    step_id: str,
    template_path: str | None,
    implementation_fragments: tuple[str, ...],
    acceptance_fragments: tuple[str, ...],
) -> None:
    step = _streamlined_step(workflow, step_id)
    if "skill" in step:
        raise CatalogValidationError(
            f"streamlined workflow: {step_id} must use its inline code-review prompt"
        )
    prompt = step.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise CatalogValidationError(
            f"streamlined workflow: {step_id} prompt must be a non-empty string"
        )
    require_fragments(
        prompt,
        (
            "clone-manifest.json",
            'formats ["markdown", "html"]',
            "only_main_content:false",
            "fresh non-image structure and stable copy",
            "Do not request screenshot capture or screenshot formats",
            "Home's retained stylesheet, landmark styles",
            "Route-specific CSS is unavailable",
            "record it in unresolved",
            "optional, non-authoritative design context only",
            "Treat the shared shell as read-only",
            "Do not overwrite shared or sibling-owned",
            "fluid theme lint --json",
            "rendered DOM",
            "preview console",
            "local server logs",
            "Do not take or compare local screenshots",
            *implementation_fragments,
        ),
        f"streamlined workflow {step_id} implementation contract",
    )
    qa = step.get("qa")
    if (
        step.get("dependsOn") != ["home-page"]
        or step.get("maxReworkRounds") != 1
        or not isinstance(qa, dict)
        or qa.get("enabled") is not True
        or qa.get("strictness") != "lenient"
        or qa.get("onFail") != "continue"
    ):
        raise CatalogValidationError(
            f"streamlined workflow: {step_id} must preserve its lenient "
            "fail-open contract"
        )
    if qa.get("requiredTools") != _deterministic_page_qa_tools(template_path):
        raise CatalogValidationError(
            f"streamlined workflow: {step_id} must require only its "
            "deterministic QA evidence floor"
        )
    acceptance = json.dumps(step.get("acceptance", []))
    require_fragments(
        acceptance,
        (
            "clone-manifest.json",
            "at least three distinct implementation files",
            "fluid theme lint --json",
            "Targeted code searches",
            "rendered DOM",
            "preview console and local server logs",
            "Screenshots are optional source-design context only",
            *acceptance_fragments,
        ),
        f"streamlined workflow {step_id} review acceptance contract",
    )
    visual_tools = (
        "screenshot_preview",
        "compare_preview_to_source",
        "view_project_image",
        "interact_preview",
    )
    required_tools = json.dumps(qa.get("requiredTools", []))
    if any(tool in required_tools for tool in visual_tools):
        raise CatalogValidationError(
            f"streamlined workflow: {step_id} QA must exclude visual and "
            "interaction tools"
        )


def _validate_content_page_review(workflow: dict[str, Any]) -> None:
    step = _streamlined_step(workflow, "content-pages")
    prompt = step.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise CatalogValidationError(
            "streamlined workflow: content-pages prompt must be a non-empty string"
        )
    if "skill" in step or "run_skill(" in prompt:
        raise CatalogValidationError(
            "streamlined workflow: content-pages must not delegate to visual page skills"
        )
    require_fragments(
        prompt,
        (
            "clone-manifest.json",
            'formats ["markdown", "html"]',
            "only_main_content:false",
            "Do not request screenshot capture or screenshot formats",
            "Home's retained stylesheet, landmark styles",
            "Route-specific CSS is unavailable",
            "optional, non-authoritative design context only",
            "Treat the shared shell as read-only",
            "run in parallel",
            "only when it already exists and fits",
            "Do not assume a sibling completed",
            "do not overwrite shared or sibling-owned",
            "cart_page/default/index.liquid",
            "error_page/404/index.liquid",
            "error_page/503/index.liquid",
            "page/default/index.liquid",
            "line items, quantities, per-line totals, order totals",
            "localized error.status_code and error.* bindings",
            "post_page/default and post/default only when",
            "stored article body dynamic",
            "import-content and catalog work run concurrently",
            "report absent preview records in unresolved",
            "fluid theme lint --json",
            "at least three distinct built routes",
            "DOM review does not prove cart interaction",
            "Do not take or compare local screenshots",
        ),
        "streamlined workflow content-pages implementation contract",
    )
    qa = step.get("qa")
    expected_tools = _deterministic_page_qa_tools(
        "cart_page/default/index.liquid",
        minimum_reads=8,
        minimum_searches=4,
        minimum_routes=3,
        mandatory_paths=(
            "error_page/404/index.liquid",
            "error_page/503/index.liquid",
            "page/default/index.liquid",
        ),
    )
    if (
        step.get("dependsOn") != ["home-page"]
        or step.get("maxReworkRounds") != 1
        or not isinstance(qa, dict)
        or qa.get("enabled") is not True
        or qa.get("strictness") != "lenient"
        or qa.get("onFail") != "continue"
    ):
        raise CatalogValidationError(
            "streamlined workflow: content-pages must preserve its lenient "
            "fail-open contract"
        )
    if qa.get("requiredTools") != expected_tools:
        raise CatalogValidationError(
            "streamlined workflow: content-pages must require only its "
            "deterministic QA evidence floor"
        )
    acceptance = json.dumps(step.get("acceptance", []))
    require_fragments(
        acceptance,
        (
            "at least eight distinct implementation files",
            "post_page/default and post/default",
            "only when the source route inventory contains a real blog",
            "fluid theme lint --json",
            "At least four targeted code searches",
            "dynamic cart state and totals bindings",
            "localized error.status_code/error.* bindings",
            "dynamic generic page content",
            "no hardcoded cart item/subtotal",
            "duplicated shared-shell markup",
            "page-local fork of an already-present sibling contract",
            "at least three distinct routes",
            "Empty content or product records",
            "listed in unresolved",
            "preview console and local server logs",
            "Screenshots are optional source-design context only",
        ),
        "streamlined workflow content-pages review acceptance contract",
    )


def _validate_content_import_body_contract(workflow: dict[str, Any]) -> None:
    """`body_html` alone imports blank pages and calls them a success.

    Shopify leaves it empty on every section-built page, so a TUSHY import
    published 52 of 73 pages with no body and passed. The step has to fall back
    to the rendered DOM, separate genuinely-empty source pages from failures,
    and report content-bearing pages rather than record counts.
    """
    step = _streamlined_step(workflow, "import-content")
    prompt = step.get("prompt")
    if not isinstance(prompt, str):
        raise CatalogValidationError(
            "streamlined workflow: import-content must carry a prompt"
        )
    require_fragments(
        prompt,
        (
            "if `body_html` is empty, fetch the page's rendered DOM",
            "record those in `empty_at_source`",
            "Never publish a page whose body resolved to nothing without listing it",
            "`pages` is the count with a non-empty body",
            "pages_empty",
            "body_from_rendered_dom",
        ),
        "streamlined workflow import-content page-body contract",
    )
    qa = step.get("qa")
    if (
        not isinstance(qa, dict)
        or qa.get("enabled") is not True
        or qa.get("onFail") != "continue"
    ):
        raise CatalogValidationError(
            "streamlined workflow: import-content must be QA-reviewed "
            "fail-open so empty page bodies fail loudly"
        )
    require_fragments(
        json.dumps(step.get("acceptance", [])),
        (
            "Every imported page has a non-empty body",
            "re-read from the rendered DOM",
            "count of content-bearing pages",
        ),
        "streamlined workflow import-content acceptance contract",
    )


def _validate_handoff_live_counts_contract(workflow: dict[str, Any]) -> None:
    """A step's STEP_OUTPUT is a snapshot from before any later remediation.

    Copying it made the handoff contradict the store it described — TUSHY's
    summary reported 149 products against a live catalog of 181.
    """
    step = _streamlined_step(workflow, "handoff")
    prompt = step.get("prompt")
    if not isinstance(prompt, str):
        raise CatalogValidationError(
            "streamlined workflow: handoff must carry a prompt"
        )
    require_fragments(
        prompt,
        (
            "Every headline count is read live, not copied",
            "Paginate the products and pages APIs",
            "publish the live one and note the step it corrects",
            'counts_source: "live-api"',
        ),
        "streamlined workflow handoff live-count contract",
    )
    require_fragments(
        json.dumps(step.get("acceptance", [])),
        (
            "read from the live API in this step",
            "can_take_an_order reflects the live catalog",
        ),
        "streamlined workflow handoff acceptance contract",
    )


def _validate_storefront_code_review(workflow: dict[str, Any]) -> None:
    step = _streamlined_step(workflow, "storefront-check")
    prompt = step.get("prompt")
    target = step.get("target")
    # fallbackToManager must stay False. Every finding this step can produce is
    # a theme defect, and Home cannot edit or publish a sibling Theme's files —
    # falling back there burned the step's only rework round on discovering it
    # had no write access, then terminated the step as BLOCKED.
    if (
        not isinstance(prompt, str)
        or "Review the published theme implementation from code" not in prompt
        or target
        != {
            "type": "kind",
            "kind": "theme",
            "fallbackToManager": False,
        }
    ):
        raise CatalogValidationError(
            "streamlined workflow: storefront-check must be a theme-targeted code review"
            " that does not fall back to the manager project"
        )
    require_fragments(
        prompt,
        (
            "read-only audit",
            "at least ten distinct implementation files",
            "at least six targeted searches",
            "fluid theme lint --json",
            "Treat the shared shell and every page file as read-only",
            "retains required canonical data sections",
            "without duplicating or forking them",
            "Do not claim which parallel step edited a file",
            "at least five distinct canonical routes",
            "Home, Shop, one Product, one Collection, and Cart",
            "preview console and local server logs",
            "storefront-check and import-content are concurrent",
            "unresolved evidence, not automatically a theme-code failure",
            "do not prove viewport layout, horizontal overflow, image loading",
            "totals recomputation, or parity with API values",
            "Do not take or compare screenshots",
            "Put unprovable behavior in unresolved",
            "Blocking means",
            "Cosmetic means",
        ),
        "streamlined workflow storefront-check implementation contract",
    )
    qa = step.get("qa")
    # maxReworkRounds must stay 0. This step's own prompt forbids it from
    # editing anything, so a rework round can only be spent discovering it
    # cannot act — which is exactly how the TUSHY run ended, with the round
    # burned and the step terminated BLOCKED instead of handing its findings
    # to the Theme project that can fix them.
    if (
        step.get("dependsOn") != ["publish-theme", "import-products"]
        or step.get("maxReworkRounds") != 0
        or not isinstance(qa, dict)
        or qa.get("enabled") is not True
        or qa.get("strictness") != "lenient"
        or qa.get("onFail") != "continue"
    ):
        raise CatalogValidationError(
            "streamlined workflow: storefront-check must preserve its lenient "
            "fail-open contract with no rework round"
        )
    if qa.get("requiredTools") != _deterministic_page_qa_tools(
        None,
        minimum_reads=10,
        minimum_searches=6,
        minimum_routes=5,
    ):
        raise CatalogValidationError(
            "streamlined workflow: storefront-check must require only its "
            "deterministic QA evidence floor"
        )
    acceptance = json.dumps(step.get("acceptance", []))
    require_fragments(
        acceptance,
        (
            "at least ten distinct implementation files",
            "fluid theme lint --json",
            "At least six targeted code searches",
            "required canonical data sections remain present",
            "without duplication or page-local forks",
            "at least five distinct canonical routes",
            "Home, Shop, Product, Collection, and Cart",
            "Missing records from concurrent import-content work",
            "listed in unresolved",
            "preview console and local server logs",
            "did not claim that code or DOM proved viewport layout",
            "interaction behavior",
            "API-value parity",
            "blocking, cosmetic, and unresolved",
        ),
        "streamlined workflow storefront-check review acceptance contract",
    )


def _reject_unsupported_page_review_claims(workflow: dict[str, Any]) -> None:
    unsupported_claims = (
        "confirmed no horizontal overflow",
        "every image loaded",
        "interactions worked",
        "totals recomputed",
        "prices matched the API",
        "shared-shell edit",
        "sibling-file overwrite",
    )
    for step_id in (
        "shop-page",
        "product-page",
        "collection-page",
        "content-pages",
        "storefront-check",
    ):
        acceptance = json.dumps(
            _streamlined_step(workflow, step_id).get("acceptance", [])
        )
        if any(claim in acceptance for claim in unsupported_claims):
            raise CatalogValidationError(
                f"streamlined workflow: {step_id} makes an unsupported "
                "deterministic evidence claim"
            )


def validate_streamlined_page_review_contract(workflow: Any) -> None:
    _validate_streamlined_home_review_contract(workflow)
    assert isinstance(workflow, dict)

    _validate_direct_page_review(
        workflow,
        step_id="shop-page",
        template_path="shop_page/default/index.liquid",
        implementation_fragments=(
            "actual Fluid products",
            "canonical returned product routes",
            "filters, search, sorting, pagination or load-more",
            "when the source exposes them",
            "product-card, grid, filter/sort, search, pagination",
            "decorative controls that do nothing",
        ),
        acceptance_fragments=(
            "Fluid-backed product cards",
            "canonical product routes",
            "dynamic prices and images",
            "reusable list components",
            "when the source exposes them",
            "absent or unsupported controls are recorded",
            "no hardcoded products, prices, images",
            "decorative nonfunctional controls",
            "canonical Shop route",
        ),
    )
    _validate_direct_page_review(
        workflow,
        step_id="product-page",
        template_path="product/default/index.liquid",
        implementation_fragments=(
            "product_hero or main_product first",
            "never fork, replace, or imitate it with static Liquid",
            "title, price, availability, options, valid variants, gallery",
            "add-to-cart hooks",
            "canonical URLs",
        ),
        acceptance_fragments=(
            "product_hero or main_product first",
            "product.* bindings",
            "existing add-to-cart hooks",
            "source-ordered supporting sections",
            "no static replacement",
            "canonical Product route",
        ),
    )
    _validate_direct_page_review(
        workflow,
        step_id="collection-page",
        template_path=None,
        implementation_fragments=(
            "classification-dependent template",
            "Shop and Collection run in parallel",
            "only when they already exist and fit",
            "page-local canonical scaffold contracts",
            "Do not assume Shop completed",
            "c.image, c.url, and c.products",
            "image fallback c.image then c.image_url then c.image_path",
        ),
        acceptance_fragments=(
            "chosen classification-dependent template",
            "honest collection index/detail semantics",
            "c.image/c.url/c.products-compatible access",
            "canonical collection and product links",
            "no assumption that a parallel sibling completed",
            "duplicated shared list markup",
            "page-local fork of an already-present shared list contract",
            "canonical Collection route",
        ),
    )
    _validate_content_page_review(workflow)
    _validate_storefront_code_review(workflow)
    _validate_content_import_body_contract(workflow)
    _validate_handoff_live_counts_contract(workflow)
    _reject_unsupported_page_review_claims(workflow)


def validate_published_catalog(
    *, streamlined_workflow: Any | None = None
) -> tuple[int, int]:
    skill_count, workflow_count = validate_manifest(load_json(MANIFEST_PATH))
    validate_flagship_contracts()
    validate_streamlined_product_import_contract()
    validate_streamlined_catalog_closure_contract(
        load_json(STREAMLINED_WORKFLOW_PATH)
        if streamlined_workflow is None
        else streamlined_workflow
    )
    validate_streamlined_page_review_contract(
        load_json(STREAMLINED_WORKFLOW_PATH)
        if streamlined_workflow is None
        else streamlined_workflow
    )
    return skill_count, workflow_count


def main() -> int:
    try:
        skill_count, workflow_count = validate_published_catalog()
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
