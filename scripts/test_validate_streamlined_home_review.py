from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import validate_catalog


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT / "workflows/streamlined-onboard-launch.workflow.json"

HOME_PROMPT = """Build the home page from the retained source evidence and the existing theme code. This step implements the page; screenshots are not a correctness gate.

Read clone-manifest.json first, then read the retained source HTML, source CSS, resolved landmark styles, and exact stable copy for Home. Retained source screenshots are optional, non-authoritative design input only. You may open only the retained source screenshot paths from clone-manifest.json with view_project_image as design context. Do not capture new or local screenshots and do not call screenshot_preview or compare_preview_to_source.

Inspect the existing layout, shared header, shared footer, tokens, sections, blocks, components, and assets before editing. Reuse the shared shell and existing canonical components where they fit. Build the source order as multiple named Liquid sections mounted separately in home_page/default/index.liquid; never replace it with one monolithic page-sized section.

Copy every stable source heading, paragraph, label, and CTA exactly. Bind products, collections, prices, images, routes, cart controls, and other resource/dynamic content through Fluid Liquid data and existing Fluid hooks rather than hardcoding the observed example. Keep editor-manageable section schemas and normal responsive document flow.

Reject base-theme scaffold filler, lorem text, placeholder products or images, inline binary media (data: or base64), hardcoded development theme ids, generated company hostnames, localhost ports, query-triggered QA shortcuts, and absolute environment-specific asset URLs. Do not use fixed or absolute whole-section relocation, page-height clamps, overflow clipping, hidden/cropped source content, transparent duplicates, or other layout-hiding hacks to simulate correctness.

Run fluid theme lint --json and fix every error. Use the local preview only for deterministic runtime checks: read the rendered DOM for `/`, browser console, and local server logs. Verify HTTP success, source-ordered sections and stable copy, Fluid-bound dynamic content, shared-shell reuse, and no runtime/resource failures. Do not take or compare local screenshots.

End with STEP_OUTPUT: { files_read: [...], files_changed: [...], sections: [...], stable_copy_checked: [...], dynamic_bindings: [...], lint: {...}, dom_checks: [...], console_errors: [...], server_errors: [...], unresolved: [...] }."""

HOME_ACCEPTANCE = [
    "The independent reviewer read clone-manifest.json plus at least three distinct implementation files, including home_page/default/index.liquid and the separately mounted section or shared-shell files it references.",
    "The independent reviewer ran fluid theme lint --json in read-only mode and it returned zero errors.",
    "Targeted code searches found multiple named section mounts in source order, exact stable source copy, Fluid-backed resource/dynamic bindings, and shared-shell reuse.",
    "Targeted code searches found no base-theme scaffold filler, inline binary media, hardcoded environment identity, monolithic page-sized section, or layout-hiding workaround.",
    "The independent reviewer read the local rendered DOM for / in all mode and confirmed HTTP success, multiple source-ordered sections, stable copy, dynamic bindings, and shared shell output.",
    "The independent reviewer read the preview console and local server logs and found no unresolved Liquid, runtime, resource, or browser errors.",
    "Screenshots are optional source-design context only. The reviewer did not use screenshot_preview, compare_preview_to_source, view_project_image, or screenshot-producing interaction checks as correctness evidence.",
]

HOME_REQUIRED_TOOLS = [
    {
        "tool": "run_cli",
        "input": {"command": "fluid", "args": ["theme", "lint", "--json"]},
        "minSuccessfulCalls": 1,
    },
    {"tool": "read_file", "input": {"path": "clone-manifest.json"}},
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
    {"tool": "read_preview_console", "minSuccessfulCalls": 1},
    {"tool": "read_local_server_logs", "minSuccessfulCalls": 1},
]


class StreamlinedHomeReviewContractTest(unittest.TestCase):
    def load_workflow(self) -> dict:
        return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def code_review_workflow(self) -> dict:
        workflow = self.load_workflow()
        home_step = next(
            step for step in workflow["steps"] if step.get("id") == "home-page"
        )
        home_step.pop("skill", None)
        home_step["prompt"] = HOME_PROMPT
        home_step["acceptance"] = copy.deepcopy(HOME_ACCEPTANCE)
        home_step["qa"]["requiredTools"] = copy.deepcopy(HOME_REQUIRED_TOOLS)
        return workflow

    def test_rejects_the_shared_visual_home_skill(self) -> None:
        workflow = self.code_review_workflow()
        home_step = next(
            step for step in workflow["steps"] if step.get("id") == "home-page"
        )
        home_step["skill"] = "themes/clone-home-page"
        del home_step["prompt"]
        validate = getattr(
            validate_catalog,
            "validate_streamlined_home_review_contract",
            lambda _workflow: None,
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "home-page must use its inline code-review prompt",
        ):
            validate(workflow)

    def test_published_workflow_satisfies_the_contract(self) -> None:
        try:
            validate_catalog.validate_streamlined_home_review_contract(
                self.load_workflow()
            )
        except validate_catalog.CatalogValidationError as error:
            self.fail(f"published workflow violates its contract: {error}")

    def test_does_not_claim_dom_evidence_can_measure_horizontal_overflow(self) -> None:
        workflow = self.code_review_workflow()
        home_step = next(
            step for step in workflow["steps"] if step.get("id") == "home-page"
        )
        home_step["acceptance"].append(
            "The DOM review confirmed no horizontal overflow."
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "unsupported DOM evidence",
        ):
            validate_catalog.validate_streamlined_home_review_contract(workflow)

    def test_catalog_validation_runs_the_home_review_contract(self) -> None:
        workflow = self.code_review_workflow()
        home_step = next(
            step for step in workflow["steps"] if step.get("id") == "home-page"
        )
        home_step["skill"] = "themes/clone-home-page"
        del home_step["prompt"]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "home-page must use its inline code-review prompt",
        ):
            validate_catalog.validate_published_catalog(
                streamlined_workflow=workflow
            )

    def test_rejects_a_missing_inline_home_prompt(self) -> None:
        workflow = self.code_review_workflow()
        home_step = next(
            step for step in workflow["steps"] if step.get("id") == "home-page"
        )
        del home_step["prompt"]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "home-page prompt must be a non-empty string",
        ):
            validate_catalog.validate_streamlined_home_review_contract(workflow)

    def test_accepts_the_inline_code_review_home_contract(self) -> None:
        validate_catalog.validate_streamlined_home_review_contract(
            self.code_review_workflow()
        )

    def test_rejects_an_incomplete_implementation_prompt(self) -> None:
        required_fragments = (
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
        )

        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                workflow = self.code_review_workflow()
                home_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "home-page"
                )
                home_step["prompt"] = home_step["prompt"].replace(fragment, "")

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "implementation contract",
                ):
                    validate_catalog.validate_streamlined_home_review_contract(
                        workflow
                    )

    def test_preserves_the_lenient_fail_open_home_step_shape(self) -> None:
        mutations = (
            ("dependency", lambda step: step.update(dependsOn=[])),
            ("rework budget", lambda step: step.update(maxReworkRounds=2)),
            ("QA enabled", lambda step: step["qa"].update(enabled=False)),
            ("QA strictness", lambda step: step["qa"].update(strictness="standard")),
            ("QA failure mode", lambda step: step["qa"].update(onFail="stop")),
        )

        for label, mutate in mutations:
            with self.subTest(label=label):
                workflow = self.code_review_workflow()
                home_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "home-page"
                )
                mutate(home_step)

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "lenient fail-open contract",
                ):
                    validate_catalog.validate_streamlined_home_review_contract(
                        workflow
                    )

    def test_requires_only_deterministic_qa_evidence(self) -> None:
        mutations = []
        for tool_name in (
            "run_cli",
            "read_file",
            "read_preview_dom",
            "search_files",
            "read_preview_console",
            "read_local_server_logs",
        ):
            mutations.append(
                (
                    f"missing {tool_name}",
                    lambda tools, name=tool_name: tools.__setitem__(
                        slice(None),
                        [tool for tool in tools if tool.get("tool") != name],
                    ),
                )
            )
        for tool_name in (
            "screenshot_preview",
            "compare_preview_to_source",
            "view_project_image",
            "interact_preview",
        ):
            mutations.append(
                (
                    f"visual {tool_name}",
                    lambda tools, name=tool_name: tools.append({"tool": name}),
                )
            )

        for label, mutate in mutations:
            with self.subTest(label=label):
                workflow = self.code_review_workflow()
                home_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "home-page"
                )
                mutate(home_step["qa"]["requiredTools"])

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "deterministic QA evidence",
                ):
                    validate_catalog.validate_streamlined_home_review_contract(
                        workflow
                    )

    def test_requires_the_code_review_acceptance_contract(self) -> None:
        required_fragments = (
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
        )

        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                workflow = self.code_review_workflow()
                home_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "home-page"
                )
                home_step["acceptance"] = [
                    criterion.replace(fragment, "")
                    for criterion in home_step["acceptance"]
                ]

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "review acceptance contract",
                ):
                    validate_catalog.validate_streamlined_home_review_contract(
                        workflow
                    )

    def test_rejects_malformed_workflow_shapes(self) -> None:
        malformed_roots = (None, "", [], {}, {"steps": None})
        for workflow in malformed_roots:
            with self.subTest(workflow=workflow):
                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "steps must be an array",
                ):
                    validate_catalog.validate_streamlined_home_review_contract(
                        workflow
                    )

        for steps in ([], [None], [{"id": 1}], [{"id": "not-home"}]):
            with self.subTest(steps=steps):
                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "home-page step is missing",
                ):
                    validate_catalog.validate_streamlined_home_review_contract(
                        {"steps": steps}
                    )

    def test_rejects_malformed_prompt_values(self) -> None:
        for prompt in (None, "", "   ", 1, {}, []):
            with self.subTest(prompt=prompt):
                workflow = self.code_review_workflow()
                home_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "home-page"
                )
                home_step["prompt"] = prompt

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "prompt must be a non-empty string",
                ):
                    validate_catalog.validate_streamlined_home_review_contract(
                        workflow
                    )

    def test_keeps_source_screenshots_as_upstream_reference_material(self) -> None:
        required_fragments = (
            'formats ["html", "rawHtml", "screenshot"]',
            "capturePageEvidence: true",
            "desktop AND at 390 wide",
        )

        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                workflow = self.code_review_workflow()
                source_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "source-capture"
                )
                source_step["prompt"] = source_step["prompt"].replace(fragment, "")

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "source evidence contract",
                ):
                    validate_catalog.validate_streamlined_home_review_contract(
                        workflow
                    )

    def test_keeps_other_page_specialists_unchanged(self) -> None:
        expected_skills = {
            "shop-page": "themes/clone-shop-page",
            "product-page": "themes/clone-product-page",
            "collection-page": "themes/clone-collection-page",
        }

        for step_id, expected_skill in expected_skills.items():
            with self.subTest(step_id=step_id):
                workflow = self.code_review_workflow()
                page_step = next(
                    step for step in workflow["steps"] if step.get("id") == step_id
                )
                page_step["skill"] = "themes/clone-home-page"

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "other page specialists",
                ):
                    validate_catalog.validate_streamlined_home_review_contract(
                        workflow
                    )


if __name__ == "__main__":
    unittest.main()
