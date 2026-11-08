from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import validate_catalog


ROOT = Path(__file__).resolve().parent.parent


class BotTemplateFilesTest(unittest.TestCase):
    def manifest(self) -> dict:
        return json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_published_bots_pin_their_templates_and_markdown_files(self) -> None:
        manifest = self.manifest()
        self.assertEqual(
            validate_catalog.validate_bots(manifest), len(manifest["bots"])
        )

    def test_rejects_a_markdown_file_digest_that_does_not_match(self) -> None:
        manifest = self.manifest()
        manifest["bots"][0]["files"]["persona.md"] = "0" * 64
        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError, "does not match"
        ):
            validate_catalog.validate_bots(manifest)

    def test_rejects_a_named_file_the_entry_does_not_pin(self) -> None:
        manifest = self.manifest()
        del manifest["bots"][0]["files"]["instructions.md"]
        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError, "exactly the files"
        ):
            validate_catalog.validate_bots(manifest)

    def test_rejects_a_file_reference_outside_the_version_directory(self) -> None:
        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError, "persona must be"
        ):
            validate_catalog.bot_file_references(
                {"persona": {"file": "../persona.md"}}, "bots[0]"
            )

    def test_accepts_inline_strings(self) -> None:
        self.assertEqual(
            validate_catalog.bot_file_references(
                {"persona": "# Inline", "instructions": "Do it."}, "bots[0]"
            ),
            set(),
        )

    def test_rejects_a_duplicate_key_and_version(self) -> None:
        manifest = self.manifest()
        manifest["bots"].append(copy.deepcopy(manifest["bots"][0]))
        with self.assertRaisesRegex(
            validate_catalog.CatalogValidationError, "duplicate bot key"
        ):
            validate_catalog.validate_bots(manifest)


if __name__ == "__main__":
    unittest.main()
