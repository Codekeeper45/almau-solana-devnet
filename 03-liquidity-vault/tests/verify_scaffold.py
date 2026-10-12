#!/usr/bin/env python3
"""Dependency-free checks for the chapter 8 preparation scaffold."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "programs/liquidity_vault/src/lib.rs").read_text()
README = (ROOT / "README.md").read_text()

class ScaffoldChecks(unittest.TestCase):
    def test_required_instruction_and_accounts_exist(self):
        for token in ("pub fn create_vault", "pub fn open_position", "struct VaultConfig", "struct UserPosition", "struct CreateVault", "struct OpenPosition"):
            with self.subTest(token=token):
                self.assertIn(token, SOURCE)

    def test_pda_seeds_and_zero_initial_state(self):
        for token in ('b"config"', 'b"vault-authority"', 'b"share"', 'b"token-vault"', 'b"position"', "total_deposited = 0", "deposited_amount = 0"):
            with self.subTest(token=token):
                self.assertIn(token, SOURCE)

    def test_scope_excludes_later_week_features(self):
        for token in ("pub fn deposit", "pub fn withdraw", "pub fn swap", "pub fn open_clmm_position"):
            with self.subTest(token=token):
                self.assertNotIn(token, SOURCE)
        self.assertIn("не реализованы", README)

    def test_program_id_matches_build_manifest(self):
        import json
        manifest = json.loads((ROOT / 'evidence/manifest.json').read_text())
        match = re.search(r'declare_id!\("([^"]+)"\)', SOURCE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), manifest['program_id'])
        self.assertNotEqual(match.group(1), '11111111111111111111111111111111')
        import hashlib
        self.assertEqual(hashlib.sha256((ROOT / 'evidence/vault.so').read_bytes()).hexdigest(), manifest['sha256'])

if __name__ == "__main__":
    unittest.main(verbosity=2)
