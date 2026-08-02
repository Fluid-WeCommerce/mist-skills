from __future__ import annotations

import json
import unittest
from pathlib import Path

import validate_catalog


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT / "workflows/streamlined-onboard-launch.workflow.json"


class StreamlinedTaxonomyMembershipContractTest(unittest.TestCase):
    def load_workflow(self) -> dict:
        return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def step(self, workflow: dict, step_id: str) -> dict:
        return next(step for step in workflow["steps"] if step.get("id") == step_id)

    def test_published_workflow_preserves_and_verifies_membership(self) -> None:
        try:
            validate_catalog.validate_streamlined_page_review_contract(
                self.load_workflow()
            )
        except validate_catalog.CatalogValidationError as error:
            self.fail(f"published workflow violates its contract: {error}")

    def test_rejects_manifest_without_category_membership(self) -> None:
        workflow = self.load_workflow()
        manifest_step = self.step(workflow, "catalog-manifest")
        manifest_step["prompt"] = manifest_step["prompt"].replace(
            "category_membership", "category name"
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "catalog taxonomy contract",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_rejects_import_without_exact_membership_readback(self) -> None:
        workflow = self.load_workflow()
        content_step = self.step(workflow, "import-content")
        content_step["prompt"] = content_step["prompt"].replace(
            "exact expected and actual destination product-id sets",
            "product counts",
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "import-content taxonomy contract",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)

    def test_rejects_acceptance_that_allows_membership_failures(self) -> None:
        workflow = self.load_workflow()
        content_step = self.step(workflow, "import-content")
        content_step["acceptance"] = [
            criterion.replace(
                "membership_failures and unresolved are empty",
                "membership failures are reported",
            )
            for criterion in content_step["acceptance"]
        ]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "taxonomy acceptance contract",
        ):
            validate_catalog.validate_streamlined_page_review_contract(workflow)


if __name__ == "__main__":
    unittest.main()
