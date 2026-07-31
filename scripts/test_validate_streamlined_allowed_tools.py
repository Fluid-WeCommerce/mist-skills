from __future__ import annotations

import json
import unittest
from pathlib import Path

import validate_catalog


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT / "workflows/streamlined-onboard-launch.workflow.json"
MANIFEST_PATH = ROOT / "manifest.json"
EXPECTED_UPDATED_AT = "2026-07-31T18:16:00Z"


class StreamlinedAllowedToolsContractTest(unittest.TestCase):
    def load_workflow(self) -> dict:
        return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def load_manifest(self) -> dict:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_published_manifest_advances_the_workflow_cache_key(self) -> None:
        manifest = self.load_manifest()
        workflow_entry = next(
            entry
            for entry in manifest["workflows"]
            if entry.get("slug") == "streamlined-onboard-launch"
        )

        self.assertEqual(workflow_entry["updated_at"], EXPECTED_UPDATED_AT)

    def test_rejects_a_stale_workflow_cache_key(self) -> None:
        workflow = self.load_workflow()
        manifest = self.load_manifest()
        workflow_entry = next(
            entry
            for entry in manifest["workflows"]
            if entry.get("slug") == "streamlined-onboard-launch"
        )
        workflow_entry["updated_at"] = "2026-07-31T06:38:34Z"

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "cache key",
        ):
            validate_catalog.validate_streamlined_product_import_contract(
                workflow, manifest
            )

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
