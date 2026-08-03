#!/usr/bin/env python3
"""Contract test for the regimen-guarantee-guard community skill."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = ROOT / "retention/regimen-guarantee-guard/SKILL.md"
RULES_PATH = (
    ROOT / "retention/regimen-guarantee-guard/references/cohort-rules.md"
)
COPY_PATH = (
    ROOT / "retention/regimen-guarantee-guard/references/copy-templates.md"
)


class RegimenGuaranteeGuardContractTest(unittest.TestCase):
    def test_skill_and_references_publish_the_full_read_only_contract(self) -> None:
        for path in (SKILL_PATH, RULES_PATH, COPY_PATH):
            self.assertTrue(path.is_file(), f"missing required skill file: {path}")

        skill = SKILL_PATH.read_text(encoding="utf-8")
        rules = RULES_PATH.read_text(encoding="utf-8")
        copy = COPY_PATH.read_text(encoding="utf-8")
        combined = "\n".join((skill, rules, copy))

        for fragment in (
            "name: Regimen Guarantee Guard",
            "icon: shield-check",
            'fluid_api("/api/subscriptions?per_page=100&page=1',
            "`db_schema`",
            "`db_query`",
            "`steps`",
            "`steps_mark_item`",
            "Cliff Risk",
            "Guarantee Breakage",
            "Silent Lapse",
            "Regimen Gap",
            "Assumption:",
            "customer-level action table",
            "CEO summary",
            "read-only",
        ):
            self.assertIn(fragment, combined)

    def test_manifest_publishes_folder_skill_and_references(self) -> None:
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        matching = [
            skill
            for skill in manifest["skills"]
            if skill["slug"] == "retention/regimen-guarantee-guard"
        ]
        self.assertEqual(len(matching), 1, "skill must appear exactly once")
        entry = matching[0]

        self.assertEqual(
            entry["path"], "retention/regimen-guarantee-guard/SKILL.md"
        )
        self.assertEqual(entry["category"], "retention")
        self.assertEqual(entry["icon"], "shield-check")
        self.assertEqual(
            entry["references"],
            [
                "retention/regimen-guarantee-guard/references/cohort-rules.md",
                "retention/regimen-guarantee-guard/references/copy-templates.md",
            ],
        )


if __name__ == "__main__":
    unittest.main()
