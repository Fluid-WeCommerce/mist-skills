from __future__ import annotations

import json
import unittest
from pathlib import Path

import validate_catalog


ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT / "workflows/open-country.workflow.json"


class OpenCountryAgreementContractTest(unittest.TestCase):
    def load_workflow(self) -> dict:
        return json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))

    def step(self, workflow: dict, step_id: str) -> dict:
        return next(step for step in workflow["steps"] if step.get("id") == step_id)

    def test_published_workflow_satisfies_the_agreement_contract(self) -> None:
        try:
            validate_catalog.validate_open_country_agreement_reconciliation_contract(
                self.load_workflow()
            )
        except validate_catalog.CatalogValidationError as error:
            self.fail(f"published workflow violates its agreement contract: {error}")

    def test_final_qa_must_wait_for_agreement_reconciliation(self) -> None:
        workflow = self.load_workflow()
        self.step(workflow, "final-qa")["dependsOn"] = [
            "convert-pricing",
            "translate-themes",
        ]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "final-qa must wait for create-agreements",
        ):
            validate_catalog.validate_open_country_agreement_reconciliation_contract(
                workflow
            )

    def test_requires_complete_country_scoped_semantic_reconciliation(self) -> None:
        required_behaviors = (
            "after create-country",
            "meta.pagination",
            "every page",
            "company_country_ids",
            "legal purpose",
            "case-fold",
            "punctuation and whitespace",
            "bilingual title variants",
            "country-name or ISO suffix",
            "description/body",
            "make no write",
        )
        for behavior in required_behaviors:
            with self.subTest(behavior=behavior):
                workflow = self.load_workflow()
                step = self.step(workflow, "create-agreements")
                step["prompt"] = step["prompt"].replace(behavior, "")

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "agreement reconciliation implementation contract",
                ):
                    validate_catalog.validate_open_country_agreement_reconciliation_contract(
                        workflow
                    )

    def test_requires_all_four_reconciliation_outcomes(self) -> None:
        workflow = self.load_workflow()
        step = self.step(workflow, "create-agreements")
        step["prompt"] = step["prompt"].replace(
            "created / reused / needs_review / failed",
            "created / skipped / failed",
        )

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "agreement reconciliation implementation contract",
        ):
            validate_catalog.validate_open_country_agreement_reconciliation_contract(
                workflow
            )

    def test_requires_acceptance_to_forbid_semantic_duplicates(self) -> None:
        workflow = self.load_workflow()
        step = self.step(workflow, "create-agreements")
        step["acceptance"] = [
            item.replace("semantically overlapping active agreements", "duplicate titles")
            for item in step["acceptance"]
        ]

        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError,
            "agreement reconciliation acceptance contract",
        ):
            validate_catalog.validate_open_country_agreement_reconciliation_contract(
                workflow
            )

    def test_requires_reused_agreements_to_preserve_language_and_checkout_behavior(
        self,
    ) -> None:
        required_behaviors = (
            "every requested translation language",
            "compatible checkout behavior",
        )
        for behavior in required_behaviors:
            with self.subTest(behavior=behavior):
                workflow = self.load_workflow()
                step = self.step(workflow, "create-agreements")
                step["acceptance"] = [
                    item.replace(behavior, "") for item in step["acceptance"]
                ]

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "agreement reconciliation acceptance contract",
                ):
                    validate_catalog.validate_open_country_agreement_reconciliation_contract(
                        workflow
                    )

    def test_final_qa_requires_a_fresh_paginated_overlap_gate(self) -> None:
        required_behaviors = (
            "meta.pagination",
            "same legal-purpose reconciliation",
            "unresolved overlap",
            "needs_review",
            "not launch-ready",
        )
        for behavior in required_behaviors:
            with self.subTest(behavior=behavior):
                workflow = self.load_workflow()
                step = self.step(workflow, "final-qa")
                step["prompt"] = step["prompt"].replace(behavior, "")

                with self.assertRaisesRegex(
                    validate_catalog.CatalogValidationError,
                    "final agreement QA implementation contract",
                ):
                    validate_catalog.validate_open_country_agreement_reconciliation_contract(
                        workflow
                    )


if __name__ == "__main__":
    unittest.main()
