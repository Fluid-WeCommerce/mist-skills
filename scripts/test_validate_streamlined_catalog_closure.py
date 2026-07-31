from __future__ import annotations

import json
import unittest
from pathlib import Path

import validate_catalog


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT / "workflows/streamlined-onboard-launch.workflow.json"


class StreamlinedCatalogClosureContractTest(unittest.TestCase):
    def load_workflow(self) -> dict:
        return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def step(self, workflow: dict, step_id: str) -> dict:
        return next(step for step in workflow["steps"] if step.get("id") == step_id)

    def test_published_workflow_satisfies_catalog_closure_contract(self) -> None:
        try:
            validate_catalog.validate_streamlined_catalog_closure_contract(
                self.load_workflow()
            )
        except validate_catalog.CatalogValidationError as error:
            self.fail(f"published workflow violates catalog closure: {error}")

    def test_requires_a_run_scoped_product_baseline_before_page_writes(self) -> None:
        workflow = self.load_workflow()
        ledger = self.step(workflow, "preview-product-ledger")
        ledger["prompt"] = ledger["prompt"].replace(
            "baseline_product_ids", "untracked_products"
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "preview-product-ledger contract",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_home_page_must_wait_for_the_product_baseline(self) -> None:
        workflow = self.load_workflow()
        home = self.step(workflow, "home-page")
        home["dependsOn"].remove("preview-product-ledger")

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "home-page must wait for preview-product-ledger",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_rejects_one_way_catalog_closure(self) -> None:
        workflow = self.load_workflow()
        closure = self.step(workflow, "catalog-closure")
        closure["prompt"] = closure["prompt"].replace(
            "both directions", "only manifest to destination"
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "two-way catalog closure contract",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_import_must_consume_closed_manifest_and_stop_on_failed_qa(self) -> None:
        workflow = self.load_workflow()
        product_import = self.step(workflow, "import-products")
        product_import["dependsOn"] = ["catalog-manifest"]
        product_import["qa"]["onFail"] = "continue"

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "import-products must wait for catalog-closure",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_publish_must_wait_for_successful_product_import(self) -> None:
        workflow = self.load_workflow()
        publish = self.step(workflow, "publish-theme")
        publish["dependsOn"].remove("import-products")

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "publish-theme must wait for import-products",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_rejects_fail_open_catalog_closure(self) -> None:
        workflow = self.load_workflow()
        closure = self.step(workflow, "catalog-closure")
        closure["qa"]["onFail"] = "continue"

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "catalog-closure must be a fail-closed gate",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_rejects_missing_catalog_closure_step(self) -> None:
        workflow = self.load_workflow()
        workflow["steps"] = [
            step for step in workflow["steps"] if step.get("id") != "catalog-closure"
        ]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "catalog-closure step is missing",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)


if __name__ == "__main__":
    unittest.main()
