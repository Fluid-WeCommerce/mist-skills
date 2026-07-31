from __future__ import annotations

import json
import unittest
from pathlib import Path

import validate_catalog


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT / "workflows/streamlined-onboard-launch.workflow.json"


class StreamlinedAllowedToolsContractTest(unittest.TestCase):
    def load_workflow(self) -> dict:
        return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def test_published_import_worker_is_restricted_to_the_importer(self) -> None:
        workflow = self.load_workflow()

        try:
            validate_catalog.validate_streamlined_product_import_contract(workflow)
        except validate_catalog.CatalogValidationError as error:
            self.fail(f"published workflow violates its import contract: {error}")

    def test_rejects_missing_or_broadened_import_worker_allowlist(self) -> None:
        for allowed_tools in (None, [], ["fluid_product_import", "fluid_api"]):
            with self.subTest(allowed_tools=allowed_tools):
                workflow = self.load_workflow()
                import_step = next(
                    step
                    for step in workflow["steps"]
                    if step.get("id") == "import-products"
                )
                if allowed_tools is None:
                    import_step.pop("allowedTools", None)
                else:
                    import_step["allowedTools"] = allowed_tools

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "worker tool allowlist",
                ):
                    validate_catalog.validate_streamlined_product_import_contract(
                        workflow
                    )


if __name__ == "__main__":
    unittest.main()
