#!/usr/bin/env python3
"""Regression tests for audit_repository.py."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from audit_repository import audit_repository


class AuditRepositoryTests(unittest.TestCase):
    def test_clean_public_surface_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            (root / "assets" / "demo.gif").write_bytes(b"GIF89a")
            (root / "README.md").write_text(
                "# Example\n\n"
                "A real product.\n\n"
                "![Demo](assets/demo.gif)\n\n"
                "## Install\n\n`example install`\n",
                encoding="utf-8",
            )
            (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
            (root / "SECURITY.md").write_text("# Security\n", encoding="utf-8")

            result = audit_repository(root)

            self.assertEqual(result["readme"]["path"], "README.md")
            self.assertEqual(result["dynamic_media_count"], 1)
            codes = {item["code"] for item in result["findings"]}
            self.assertNotIn("broken-relative-link", codes)
            self.assertNotIn("possible-secret", codes)

    def test_broken_link_local_path_and_secret_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "# Example\n\n"
                "TODO: replace https://example.com\n\n"
                "![Missing](assets/missing.png)\n\n"
                "Local: /Users/example/private/file.txt\n\n"
                "Token: ghp_abcdefghijklmnopqrstuvwxyz012345\n",
                encoding="utf-8",
            )

            result = audit_repository(root)
            codes = {item["code"] for item in result["findings"]}

            self.assertIn("broken-relative-link", codes)
            self.assertIn("local-absolute-path", codes)
            self.assertIn("possible-secret", codes)
            self.assertIn("placeholder-copy", codes)
            self.assertGreater(result["summary"]["errors"], 0)

    def test_missing_readme_is_reported_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = audit_repository(Path(directory))
            codes = {item["code"] for item in result["findings"]}
            self.assertIn("missing-readme", codes)

    def test_git_ignored_media_is_not_counted_as_public(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            (root / "tmp").mkdir()
            (root / "README.md").write_text(
                "# Example\n\n![Public](assets/public.png)\n",
                encoding="utf-8",
            )
            (root / "assets" / "public.png").write_bytes(b"PNG")
            (root / "tmp" / "candidate.gif").write_bytes(b"GIF89a")
            (root / ".gitignore").write_text("tmp/\n", encoding="utf-8")
            subprocess.run(
                ["git", "init", "-q", str(root)],
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "add",
                    "README.md",
                    "assets/public.png",
                    ".gitignore",
                ],
                check=True,
                capture_output=True,
            )

            result = audit_repository(root)

            self.assertEqual(result["public_media_count"], 1)
            self.assertEqual(result["local_only_media_count"], 1)
            self.assertEqual(result["dynamic_media_count"], 0)
            self.assertEqual(result["local_dynamic_media_count"], 1)


if __name__ == "__main__":
    unittest.main()
