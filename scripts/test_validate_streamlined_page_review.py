from __future__ import annotations

import json
import unittest
from pathlib import Path

import validate_catalog


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT / "workflows/streamlined-onboard-launch.workflow.json"


class StreamlinedPageReviewContractTest(unittest.TestCase):
    def load_workflow(self) -> dict:
        return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def test_rejects_the_shared_visual_shop_skill(self) -> None:
        workflow = self.load_workflow()
        shop_step = next(
            step for step in workflow["steps"] if step.get("id") == "shop-page"
        )
        shop_step["skill"] = "themes/clone-shop-page"
        shop_step.pop("prompt", None)
        validate = getattr(
            validate_catalog,
            "validate_streamlined_page_review_contract",
            lambda _workflow: None,
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "shop-page must use its inline code-review prompt",
        ):
            validate(workflow)

    def test_published_workflow_satisfies_the_page_review_contract(self) -> None:
        try:
            validate_catalog.validate_streamlined_page_review_contract(
                self.load_workflow()
            )
        except validate_catalog.CatalogValidationError as error:
            self.fail(f"published workflow violates its contract: {error}")

    def test_rejects_home_page_without_bulk_media_reconcile(self) -> None:
        workflow = self.load_workflow()
        home_step = next(
            step for step in workflow["steps"] if step.get("id") == "home-page"
        )
        home_step["prompt"] = home_step["prompt"].replace(
            "theme_media_reconcile", "a manual dam_upload loop"
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "home-page implementation contract",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_requires_home_source_control_inventory_contract(self) -> None:
        required_fragments = (
            "home_interactions.source_html_paths",
            "home_interactions.source_html_sha256",
            "visual_routes.home.source_evidence.desktop.documents.html",
            "visual_routes.home.source_evidence.mobile.documents.html",
            "home_interactions.controls",
            "controls array must be non-empty",
            "ids are unique non-empty strings",
            "required keys and types",
            "source-present visible control",
            "semantic kind, target, state transition, and keyboard/accessibility behavior",
            "expected_outcome.type is route, submission, or state",
            "repeated is a boolean",
            "viewport, path, sha256, and selector_or_locator",
            "matching signed desktop or mobile HTML cell",
            "blank, hash-only, or javascript: links",
            "action-looking buttons without a real target or state hook",
            "documented source-equivalent exception",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                workflow = self.load_workflow()
                home_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "home-page"
                )
                home_step["prompt"] = home_step["prompt"].replace(fragment, "")

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "home-page implementation contract",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_requires_independent_source_control_denominator_review(self) -> None:
        required_fragments = (
            "opened both signed desktop and mobile Home HTML files",
            "matched both hashes",
            "independently enumerated every visible actionable element in each viewport",
            "non-empty controls array",
            "unique control ids",
            "required keys and types",
            "signed source evidence path, hash, viewport, and selector or locator",
            "no source-present control family or individual non-repeated control was omitted",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                workflow = self.load_workflow()
                home_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "home-page"
                )
                home_step["acceptance"] = [
                    item.replace(fragment, "") for item in home_step["acceptance"]
                ]

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "home-page review acceptance contract",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_separates_route_checks_from_stateful_interactions(self) -> None:
        required_fragments = (
            "Use interact_preview only for stateful controls",
            "Do not call interact_preview on links, navigational CTAs, or form submissions",
            "Verify primary CTA targets in code and rendered DOM",
            "load each representative resolved route with read_preview_dom",
        )
        for step_id in ("home-page", "storefront-check"):
            for fragment in required_fragments:
                with self.subTest(step_id=step_id, fragment=fragment):
                    workflow = self.load_workflow()
                    step = next(
                        step
                        for step in workflow["steps"]
                        if step.get("id") == step_id
                    )
                    step["prompt"] = step["prompt"].replace(fragment, "")

                    with self.assertRaisesRegex(
                        validate_catalog.CatalogValidationError,
                        "implementation contract",
                    ):
                        validate_catalog.validate_streamlined_page_review_contract(
                            workflow
                        )

    def test_requires_mobile_stateful_interaction_and_route_tool_floors(self) -> None:
        for step_id in ("home-page", "storefront-check"):
            with self.subTest(step_id=step_id, tool="interact_preview"):
                workflow = self.load_workflow()
                step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == step_id
                )
                interaction_requirement = next(
                    requirement
                    for requirement in step["qa"]["requiredTools"]
                    if requirement.get("tool") == "interact_preview"
                    and requirement.get("input", {}).get("width") == 390
                )
                self.assertEqual(
                    interaction_requirement.get("input"),
                    {"path": "/", "width": 390, "height": 844},
                )

            with self.subTest(step_id=step_id, tool="CTA read_preview_dom"):
                workflow = self.load_workflow()
                step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == step_id
                )
                step["qa"]["requiredTools"] = [
                    requirement
                    for requirement in step["qa"]["requiredTools"]
                    if not (
                        requirement.get("tool") == "read_preview_dom"
                        and requirement.get("input") == {"mode": "html"}
                    )
                ]

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "deterministic QA evidence",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_requires_signed_source_denominator_tool_floors(self) -> None:
        for step_id in ("home-page", "storefront-check"):
            with self.subTest(step_id=step_id):
                workflow = self.load_workflow()
                step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == step_id
                )
                step["qa"]["requiredTools"] = [
                    requirement
                    for requirement in step["qa"]["requiredTools"]
                    if requirement.get("tool") != "file_sha256"
                ]

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "deterministic QA evidence",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_requires_inventory_linked_interaction_receipts(self) -> None:
        required_fragments = (
            "home_interactions.stateful_receipts",
            "control id, family, expected outcome type, source evidence, selector, viewport, pre-state, action, post-state, and result",
            "home_interactions.route_receipts",
            "control id, expected outcome type, resolved href or action, loaded route, status, and DOM evidence",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                workflow = self.load_workflow()
                home_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "home-page"
                )
                home_step["prompt"] = home_step["prompt"].replace(fragment, "")

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "home-page implementation contract",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_rejects_full_catalog_validator_for_home_only_evidence(self) -> None:
        for step_id in ("home-page", "storefront-check"):
            with self.subTest(step_id=step_id):
                workflow = self.load_workflow()
                step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == step_id
                )
                step["qa"]["requiredTools"].append(
                    {
                        "tool": "validate_theme_source_inventory",
                        "input": {"manifest_path": "clone-manifest.json"},
                        "minSuccessfulCalls": 1,
                    }
                )

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "Home-only workflow must not require the full-catalog source validator",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_rejects_full_catalog_validator_call_in_home_only_prompt(self) -> None:
        for step_id in ("home-page", "storefront-check"):
            with self.subTest(step_id=step_id):
                workflow = self.load_workflow()
                step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == step_id
                )
                step["prompt"] += (
                    " Call validate_theme_source_inventory with manifest_path "
                    "clone-manifest.json."
                )

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "Home-only workflow must not call the full-catalog source validator",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_requires_current_3009_dynamic_path_binding_disclosure(self) -> None:
        required_fragments = (
            "CURRENT-3009",
            "read_file/file_sha256 receipts",
            "cannot machine-bind",
            "requiredTools alone is not proof",
        )
        for step_id in ("home-page", "storefront-check"):
            for fragment in required_fragments:
                with self.subTest(step_id=step_id, fragment=fragment):
                    workflow = self.load_workflow()
                    step = next(
                        step
                        for step in workflow["steps"]
                        if step.get("id") == step_id
                    )
                    step["acceptance"] = [
                        item.replace(fragment, "") for item in step["acceptance"]
                    ]

                    with self.assertRaisesRegex(
                        validate_catalog.CatalogValidationError,
                        "review acceptance contract",
                    ):
                        validate_catalog.validate_streamlined_page_review_contract(
                            workflow
                        )

    def test_requires_bounded_home_and_storefront_interaction_tools(self) -> None:
        for step_id in ("home-page", "storefront-check"):
            with self.subTest(step_id=step_id):
                workflow = self.load_workflow()
                step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == step_id
                )
                step["qa"]["requiredTools"] = [
                    requirement
                    for requirement in step["qa"]["requiredTools"]
                    if requirement.get("tool") != "interact_preview"
                ]

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "deterministic QA evidence",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_requires_bounded_interaction_review_contracts(self) -> None:
        required_fragments = {
            "home-page": (
                "bounded Home interaction pass",
                "each distinct source-present interaction family",
                "representative repeated control",
                "primary CTA targets",
            ),
            "storefront-check": (
                "bounded final interaction smoke pass",
                "each distinct source-present interaction family",
                "representative repeated controls",
                "primary CTA targets",
            ),
        }
        for step_id, fragments in required_fragments.items():
            for fragment in fragments:
                with self.subTest(step_id=step_id, fragment=fragment):
                    workflow = self.load_workflow()
                    step = next(
                        step
                        for step in workflow["steps"]
                        if step.get("id") == step_id
                    )
                    step["acceptance"] = [
                        item.replace(fragment, "") for item in step["acceptance"]
                    ]

                    with self.assertRaisesRegex(
                        validate_catalog.CatalogValidationError,
                        "review acceptance contract",
                    ):
                        validate_catalog.validate_streamlined_page_review_contract(
                            workflow
                        )

    def test_requires_source_button_to_empty_fragment_rework_case(self) -> None:
        workflow = self.load_workflow()
        home_step = next(
            step for step in workflow["steps"] if step.get("id") == "home-page"
        )
        home_step["acceptance"] = [
            item.replace(
                'A source button implemented as a generated href="#" is REWORK and leaves this lenient step needs-review.',
                "",
            )
            for item in home_step["acceptance"]
        ]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "home-page review acceptance contract",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_rejects_the_shared_visual_product_skill(self) -> None:
        workflow = self.load_workflow()
        product_step = next(
            step for step in workflow["steps"] if step.get("id") == "product-page"
        )
        product_step["skill"] = "themes/clone-product-page"
        product_step.pop("prompt", None)

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "product-page must use its inline code-review prompt",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_rejects_the_shared_visual_collection_skill(self) -> None:
        workflow = self.load_workflow()
        collection_step = next(
            step for step in workflow["steps"] if step.get("id") == "collection-page"
        )
        collection_step["skill"] = "themes/clone-collection-page"
        collection_step.pop("prompt", None)

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "collection-page must use its inline code-review prompt",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_rejects_visual_skill_delegation_from_content_pages(self) -> None:
        for skill in (
            "themes/clone-blog-page",
            "themes/clone-post-page",
            "themes/clone-cart-page",
            "themes/clone-system-pages",
            "themes/clone-page-to-liquid",
        ):
            with self.subTest(skill=skill):
                workflow = self.load_workflow()
                content_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "content-pages"
                )
                content_step["prompt"] += f'\nCall run_skill("{skill}").'

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "content-pages must not delegate to visual page skills",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_rejects_the_customer_clickthrough_storefront_check(self) -> None:
        workflow = self.load_workflow()
        storefront_step = next(
            step for step in workflow["steps"] if step.get("id") == "storefront-check"
        )
        storefront_step["target"] = {"type": "manager"}
        storefront_step["prompt"] = "Walk the live storefront like a customer."

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "storefront-check must be a theme-targeted code review",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_rejects_unsupported_dom_and_code_evidence_claims(self) -> None:
        unsupported_claim = (
            "The DOM confirmed no horizontal overflow, every image loaded, "
            "interactions worked, totals recomputed, and prices matched the API."
        )
        for step_id in (
            "shop-page",
            "product-page",
            "collection-page",
            "content-pages",
            "storefront-check",
        ):
            with self.subTest(step_id=step_id):
                workflow = self.load_workflow()
                step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == step_id
                )
                step["acceptance"].append(unsupported_claim)

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "unsupported deterministic evidence claim",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_rejects_unprovable_file_ownership_claims(self) -> None:
        workflow = self.load_workflow()
        content_step = next(
            step for step in workflow["steps"] if step.get("id") == "content-pages"
        )
        content_step["acceptance"].append(
            "The reviewer confirmed no shared-shell edit or sibling-file overwrite."
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "unsupported deterministic evidence claim",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_keeps_the_production_home_and_source_capture_contracts(self) -> None:
        workflow = self.load_workflow()
        home_step = next(
            step for step in workflow["steps"] if step.get("id") == "home-page"
        )
        home_step["skill"] = "themes/clone-home-page"
        home_step.pop("prompt", None)

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "home-page must use its inline code-review prompt",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

        workflow = self.load_workflow()
        source_step = next(
            step for step in workflow["steps"] if step.get("id") == "source-capture"
        )
        source_step["prompt"] = source_step["prompt"].replace(
            "capturePageEvidence: true", ""
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "source evidence contract",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_requires_non_image_route_evidence_and_parallel_safe_ownership(self) -> None:
        mutations = (
            ("shop-page", 'formats ["markdown", "html"]'),
            ("shop-page", "when the source exposes them"),
            ("product-page", "Route-specific CSS is unavailable"),
            ("collection-page", "Do not assume Shop completed"),
            ("content-pages", "Do not assume a sibling completed"),
        )
        for step_id, fragment in mutations:
            with self.subTest(step_id=step_id, fragment=fragment):
                workflow = self.load_workflow()
                step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == step_id
                )
                step["prompt"] = step["prompt"].replace(fragment, "")

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "implementation contract",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_requires_all_mode_for_every_new_dom_evidence_floor(self) -> None:
        for step_id in (
            "shop-page",
            "product-page",
            "collection-page",
            "content-pages",
            "storefront-check",
        ):
            with self.subTest(step_id=step_id):
                workflow = self.load_workflow()
                step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == step_id
                )
                dom_requirement = next(
                    requirement
                    for requirement in step["qa"]["requiredTools"]
                    if requirement.get("tool") == "read_preview_dom"
                )
                dom_requirement.pop("input", None)

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "deterministic QA evidence",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_requires_exact_deterministic_qa_evidence_floors(self) -> None:
        for step_id in (
            "home-page",
            "shop-page",
            "product-page",
            "collection-page",
            "content-pages",
            "storefront-check",
        ):
            with self.subTest(step_id=step_id):
                workflow = self.load_workflow()
                step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == step_id
                )
                step["qa"]["requiredTools"].append({"tool": "screenshot_preview"})

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "deterministic QA evidence",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_preserves_lenient_fail_open_page_review_shapes(self) -> None:
        for step_id in (
            "home-page",
            "shop-page",
            "product-page",
            "collection-page",
            "content-pages",
            "storefront-check",
        ):
            for field, value in (
                ("enabled", False),
                ("strictness", "standard"),
                ("onFail", "stop"),
            ):
                with self.subTest(step_id=step_id, field=field):
                    workflow = self.load_workflow()
                    step = next(
                        step
                        for step in workflow["steps"]
                        if step.get("id") == step_id
                    )
                    step["qa"][field] = value

                    with self.assertRaisesRegex(
                        validate_catalog.CatalogValidationError,
                        "lenient fail-open contract",
                    ):
                        validate_catalog.validate_streamlined_page_review_contract(
                            workflow
                        )

    def test_rejects_malformed_roots_and_missing_page_steps(self) -> None:
        for malformed in (None, "", [], {}, {"steps": None}):
            with self.subTest(malformed=malformed):
                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "steps must be an array",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        malformed
                    )

        for step_id in (
            "shop-page",
            "product-page",
            "collection-page",
            "content-pages",
            "storefront-check",
        ):
            with self.subTest(missing_step=step_id):
                workflow = self.load_workflow()
                workflow["steps"] = [
                    step
                    for step in workflow["steps"]
                    if step.get("id") != step_id
                ]

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    f"{step_id} step is missing",
                ):
                    validate_catalog.validate_streamlined_page_review_contract(
                        workflow
                    )

    def test_rejects_malformed_prompts_and_required_tool_lists(self) -> None:
        for step_id in (
            "shop-page",
            "product-page",
            "collection-page",
            "content-pages",
            "storefront-check",
        ):
            for malformed_prompt in (None, "", "   ", 1, {}, []):
                with self.subTest(
                    step_id=step_id, malformed_prompt=malformed_prompt
                ):
                    workflow = self.load_workflow()
                    step = next(
                        step
                        for step in workflow["steps"]
                        if step.get("id") == step_id
                    )
                    step["prompt"] = malformed_prompt

                    with self.assertRaises(validate_catalog.CatalogValidationError):
                        validate_catalog.validate_streamlined_page_review_contract(
                            workflow
                        )

            for malformed_tools in (None, "", {}, [None]):
                with self.subTest(
                    step_id=step_id, malformed_tools=malformed_tools
                ):
                    workflow = self.load_workflow()
                    step = next(
                        step
                        for step in workflow["steps"]
                        if step.get("id") == step_id
                    )
                    step["qa"]["requiredTools"] = malformed_tools

                    with self.assertRaisesRegex(
                        validate_catalog.CatalogValidationError,
                        "deterministic QA evidence",
                    ):
                        validate_catalog.validate_streamlined_page_review_contract(
                            workflow
                        )


if __name__ == "__main__":
    unittest.main()
