from __future__ import annotations

import json
import unittest
from pathlib import Path

import validate_catalog


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT / "workflows/streamlined-onboard-launch.workflow.json"


def product(
    source_id: str,
    handle: str,
    *,
    title: str,
    sku: str,
) -> dict:
    return {
        "source_id": source_id,
        "source_url": f"https://source.example/products/{handle}",
        "source_handle": handle,
        "title": title,
        "description": f"Description for {title}",
        "price": "99.00",
        "currency": "USD",
        "image_urls": [f"https://source.example/images/{handle}.webp"],
        "option_axes": {"Size": ["One Size"]},
        "variants": [
            {
                "source_variant_id": f"{source_id}-one-size",
                "sku": sku,
                "options": ["One Size"],
                "price": "99.00",
            }
        ],
    }


class StreamlinedCatalogClosureContractTest(unittest.TestCase):
    def load_workflow(self) -> dict:
        return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def step(self, workflow: dict, step_id: str) -> dict:
        return next(step for step in workflow["steps"] if step.get("id") == step_id)

    def test_published_workflow_satisfies_preview_product_gate_contract(self) -> None:
        try:
            validate_catalog.validate_streamlined_catalog_closure_contract(
                self.load_workflow()
            )
        except validate_catalog.CatalogValidationError as error:
            self.fail(f"published workflow violates preview-product gate: {error}")

    def test_canonical_import_precedes_the_page_product_baseline(self) -> None:
        workflow = self.load_workflow()
        ledger = self.step(workflow, "preview-product-ledger")
        ledger["dependsOn"] = []

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "preview-product-ledger must wait for import-products",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_home_page_must_wait_for_the_post_import_product_baseline(self) -> None:
        workflow = self.load_workflow()
        home = self.step(workflow, "home-page")
        home["dependsOn"].remove("preview-product-ledger")

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "home-page must wait for preview-product-ledger",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_source_capture_requires_evidence_backed_catalog_root_qa(self) -> None:
        workflow = self.load_workflow()
        source_capture = self.step(workflow, "source-capture")
        source_capture["qa"]["requiredTools"] = []

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "source-capture evidence QA contract",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_catalog_root_denominator_disclaims_web_completeness(self) -> None:
        workflow = self.load_workflow()
        catalog_manifest = self.step(workflow, "catalog-manifest")
        catalog_manifest["prompt"] = catalog_manifest["prompt"].replace(
            "does not prove web completeness", "proves web completeness"
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "bounded source denominator contract",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_catalog_producer_separates_identity_index_from_final_manifest(self) -> None:
        workflow = self.load_workflow()
        catalog_manifest = self.step(workflow, "catalog-manifest")
        catalog_manifest["prompt"] = catalog_manifest["prompt"].replace(
            "catalog-identities.jsonl", "catalog-manifest.jsonl"
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "artifact separation contract",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_import_must_finish_before_page_steps(self) -> None:
        workflow = self.load_workflow()
        product_import = self.step(workflow, "import-products")
        product_import["dependsOn"] = ["preview-product-gate"]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "import-products must wait for catalog-manifest",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_preview_gate_blocks_every_product_created_after_canonical_import(self) -> None:
        workflow = self.load_workflow()
        gate = self.step(workflow, "preview-product-gate")
        gate["prompt"] = gate["prompt"].replace(
            "any run-created product", "an unattributed run-created product"
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "zero-tolerance preview-product gate contract",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_publish_must_wait_for_preview_product_gate(self) -> None:
        workflow = self.load_workflow()
        publish = self.step(workflow, "publish-theme")
        publish["dependsOn"].remove("preview-product-gate")

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "publish-theme must wait for preview-product-gate",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_rejects_fail_open_preview_product_gate(self) -> None:
        workflow = self.load_workflow()
        gate = self.step(workflow, "preview-product-gate")
        gate["qa"]["onFail"] = "continue"

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "preview-product-gate must stop on QA failure",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_workflow_discloses_qa_containment_is_not_machine_proof(self) -> None:
        workflow = self.load_workflow()
        workflow["description"] = workflow["description"].replace(
            "does not provide machine-level fail-closed proof",
            "provides machine-level fail-closed proof",
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "QA containment disclosure",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_blocked_preview_gate_must_be_a_failing_qa_outcome(self) -> None:
        workflow = self.load_workflow()
        gate = self.step(workflow, "preview-product-gate")
        gate["acceptance"] = [
            criterion.replace("QA_VERDICT: FAIL", "QA_REVIEW: BLOCKED")
            for criterion in gate["acceptance"]
        ]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "blocked preview-product gate QA contract",
        ):
            validate_catalog.validate_streamlined_catalog_closure_contract(workflow)

    def test_product_safety_steps_require_deterministic_qa_evidence(self) -> None:
        for step_id in ("preview-product-ledger", "preview-product-gate"):
            with self.subTest(step_id=step_id):
                workflow = self.load_workflow()
                step = self.step(workflow, step_id)
                step["qa"]["requiredTools"] = []

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "supported QA evidence floor",
                ):
                    validate_catalog.validate_streamlined_catalog_closure_contract(
                        workflow
                    )

    def test_normalizes_realistic_separate_artifacts_in_identity_order(self) -> None:
        identity_index = "\n".join(
            [
                json.dumps(
                    {
                        "source_id": "watch",
                        "source_url": "https://source.example/products/watch",
                        "source_handle": "watch",
                        "title": "Watch",
                    }
                ),
                json.dumps(
                    {
                        "source_id": "strap",
                        "source_url": "https://source.example/products/strap",
                        "source_handle": "strap",
                        "title": "Strap",
                    }
                ),
            ]
        )
        records = [
            product("strap", "strap", title="Strap", sku="STRAP-ONE"),
            product("watch", "watch", title="Watch", sku="WATCH-ONE"),
        ]

        manifest = validate_catalog.normalize_streamlined_catalog_artifacts(
            identity_index,
            records,
            source_market_iso="US",
        )

        self.assertEqual(
            [item["source_id"] for item in manifest["products"]],
            ["watch", "strap"],
        )
        self.assertEqual(manifest["unresolved"], [])

    def test_normalization_rejects_duplicate_enriched_events(self) -> None:
        identity_index = json.dumps(
            {
                "source_id": "watch",
                "source_url": "https://source.example/products/watch",
                "source_handle": "watch",
                "title": "Watch",
            }
        )
        watch = product("watch", "watch", title="Watch", sku="WATCH-ONE")

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "duplicate enriched record",
        ):
            validate_catalog.normalize_streamlined_catalog_artifacts(
                identity_index,
                [watch, watch],
                source_market_iso="US",
            )

    def test_normalization_rejects_identity_only_final_product(self) -> None:
        identity = {
            "source_id": "watch",
            "source_url": "https://source.example/products/watch",
            "source_handle": "watch",
            "title": "Watch",
        }

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "is not importer-complete",
        ):
            validate_catalog.normalize_streamlined_catalog_artifacts(
                json.dumps(identity),
                [identity],
                source_market_iso="US",
            )

    def test_normalization_rejects_record_that_disagrees_with_identity_index(
        self,
    ) -> None:
        identity = {
            "source_id": "watch",
            "source_url": "https://source.example/products/watch",
            "source_handle": "watch",
            "title": "Watch",
        }
        enriched = product("watch", "wrong-watch", title="Watch", sku="WATCH-ONE")

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "disagrees with identity index",
        ):
            validate_catalog.normalize_streamlined_catalog_artifacts(
                json.dumps(identity),
                [enriched],
                source_market_iso="US",
            )

    def test_normalization_rejects_empty_identity_url_or_title(self) -> None:
        for field in ("source_url", "title"):
            for empty_value in ("", "   "):
                with self.subTest(field=field, empty_value=repr(empty_value)):
                    identity = {
                        "source_id": "watch",
                        "source_url": "https://source.example/products/watch",
                        "source_handle": "watch",
                        "title": "Watch",
                    }
                    identity[field] = empty_value

                    with self.assertRaisesRegex(
                        validate_catalog.CatalogValidationError,
                        f"has no {field}",
                    ):
                        validate_catalog.normalize_streamlined_catalog_artifacts(
                            json.dumps(identity),
                            [
                                product(
                                    "watch",
                                    "watch",
                                    title="Watch",
                                    sku="WATCH-ONE",
                                )
                            ],
                            source_market_iso="US",
                        )

    def test_normalization_rejects_empty_required_product_values(self) -> None:
        identity = {
            "source_id": "watch",
            "source_url": "https://source.example/products/watch",
            "source_handle": "watch",
            "title": "Watch",
        }
        for field in ("source_url", "title", "price", "currency"):
            for empty_value in ("", "   "):
                with self.subTest(field=field, empty_value=repr(empty_value)):
                    enriched = product(
                        "watch", "watch", title="Watch", sku="WATCH-ONE"
                    )
                    enriched[field] = empty_value

                    with self.assertRaisesRegex(
                        validate_catalog.CatalogValidationError,
                        "is not importer-complete",
                    ):
                        validate_catalog.normalize_streamlined_catalog_artifacts(
                            json.dumps(identity),
                            [enriched],
                            source_market_iso="US",
                        )

    def test_normalization_rejects_empty_image_url(self) -> None:
        identity = {
            "source_id": "watch",
            "source_url": "https://source.example/products/watch",
            "source_handle": "watch",
            "title": "Watch",
        }
        for empty_value in ("", "   "):
            with self.subTest(empty_value=repr(empty_value)):
                enriched = product(
                    "watch", "watch", title="Watch", sku="WATCH-ONE"
                )
                enriched["image_urls"] = [empty_value]

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "is not importer-complete",
                ):
                    validate_catalog.normalize_streamlined_catalog_artifacts(
                        json.dumps(identity),
                        [enriched],
                        source_market_iso="US",
                    )

    def test_normalization_rejects_empty_variant_id_or_price(self) -> None:
        identity = {
            "source_id": "watch",
            "source_url": "https://source.example/products/watch",
            "source_handle": "watch",
            "title": "Watch",
        }
        for field in ("source_variant_id", "price"):
            for empty_value in ("", "   "):
                with self.subTest(field=field, empty_value=repr(empty_value)):
                    enriched = product(
                        "watch", "watch", title="Watch", sku="WATCH-ONE"
                    )
                    enriched["variants"][0][field] = empty_value

                    with self.assertRaisesRegex(
                        validate_catalog.CatalogValidationError,
                        "is not importer-complete",
                    ):
                        validate_catalog.normalize_streamlined_catalog_artifacts(
                            json.dumps(identity),
                            [enriched],
                            source_market_iso="US",
                        )

    def test_normalization_rejects_empty_market_iso(self) -> None:
        identity = {
            "source_id": "watch",
            "source_url": "https://source.example/products/watch",
            "source_handle": "watch",
            "title": "Watch",
        }

        for empty_value in ("", "   "):
            with self.subTest(empty_value=repr(empty_value)):
                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "source_market_iso must be a non-empty string",
                ):
                    validate_catalog.normalize_streamlined_catalog_artifacts(
                        json.dumps(identity),
                        [product("watch", "watch", title="Watch", sku="WATCH-ONE")],
                        source_market_iso=empty_value,
                    )


if __name__ == "__main__":
    unittest.main()
