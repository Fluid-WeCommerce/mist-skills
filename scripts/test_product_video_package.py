"""Guard the binary/runtime and prompt-budget contracts of Product video."""
import json
from pathlib import Path
import re
import struct
import unittest

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / 'marketing/product-video'


class ProductVideoPackageTests(unittest.TestCase):
    def setUp(self):
        manifest = json.loads((ROOT / 'manifest.json').read_text())
        self.entry = next(s for s in manifest['skills'] if s['slug'] == 'marketing/product-video')

    def test_all_runtime_files_are_declared_and_present(self):
        declared = set(self.entry['assets'])
        self.assertEqual(len(declared), len(self.entry['assets']))
        actual = {str(p.relative_to(ROOT)) for folder in ['assets', 'scripts']
                  for p in (SKILL / folder).rglob('*') if p.is_file()}
        self.assertEqual(declared, actual)
        for relative in declared:
            p = ROOT / relative
            self.assertTrue(p.is_file(), relative)
            self.assertGreater(p.stat().st_size, 0, relative)
        frame = (SKILL / 'assets/player/frame.html').read_text()
        import_map = json.loads(re.search(r'<script type="importmap">(.*?)</script>', frame, re.S).group(1))
        for relative in import_map['imports'].values():
            self.assertTrue((SKILL / 'assets/player' / relative).is_file(), relative)

    def test_real_models_and_attribution_travel_together(self):
        for model in ['laptop', 'phone']:
            p = SKILL / 'assets/player/runtime/device-stage' / (model + '.glb')
            magic, version, length = struct.unpack('<4sII', p.read_bytes()[:12])
            self.assertEqual(magic, b'glTF')
            self.assertEqual(version, 2)
            self.assertEqual(length, p.stat().st_size)
            credit = p.with_name(model + '-LICENSE.txt').read_text()
            self.assertIn('CC Attribution 4.0', credit)
            self.assertIn('https://sketchfab.com/', credit)

    def test_guides_are_readable_without_repeating_them_in_every_turn(self):
        reference_bytes = sum((ROOT / p).stat().st_size for p in self.entry['references'])
        self.assertLessEqual(reference_bytes, 16 * 1024)
        guides = list((SKILL / 'assets/guides').glob('*.md'))
        self.assertTrue(guides)
        for p in guides:
            for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
                if target.startswith(('https:', 'http:', '#', 'mailto:')):
                    continue
                self.assertTrue((p.parent / target.split('#')[0]).exists(), str(p) + ': ' + target)


if __name__ == '__main__':
    unittest.main()
