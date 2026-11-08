from __future__ import annotations

import json
import unittest
from pathlib import Path

import validate_catalog


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT / "workflows/streamlined-onboard-launch.workflow.json"


class StreamlinedHeaderNavigationContractTest(unittest.TestCase):
    def load_workflow(self) -> dict:
        return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def step(self, workflow: dict, step_id: str) -> dict:
        return next(step for step in workflow["steps"] if step.get("id") == step_id)

    def test_published_workflow_binds_the_header_menu(self) -> None:
        try:
            validate_catalog.validate_streamlined_page_review_contract(
                self.load_workflow()
            )
        except validate_catalog.CatalogValidationError as error:
            self.fail(f"published workflow violates its contract: {error}")

    def test_rejects_workflow_without_header_navigation_step(self) -> None:
        workflow = self.load_workflow()
        workflow["steps"] = [
            step for step in workflow["steps"] if step.get("id") != "header-navigation"
        ]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "header-navigation step is missing",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_rejects_menu_step_that_runs_before_content_import(self) -> None:
        workflow = self.load_workflow()
        self.step(workflow, "header-navigation")["dependsOn"] = ["publish-theme"]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "header-navigation must wait for import-content",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_rejects_menu_step_that_drops_the_locale_selector(self) -> None:
        workflow = self.load_workflow()
        step = self.step(workflow, "header-navigation")
        step["prompt"] = step["prompt"].replace("navbar_locale_dropdown", "the selector")

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "header-navigation contract",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_rejects_handoff_that_ignores_the_menu_step(self) -> None:
        workflow = self.load_workflow()
        handoff = self.step(workflow, "handoff")
        handoff["dependsOn"] = [
            dependency
            for dependency in handoff["dependsOn"]
            if dependency != "header-navigation"
        ]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "handoff must wait for header-navigation",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)


if __name__ == "__main__":
    unittest.main()
