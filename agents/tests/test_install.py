import os
import subprocess
import tempfile
import unittest
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[1]
INSTALL_SCRIPT = AGENTS_DIR / "install.sh"


class InstallTest(unittest.TestCase):
    def test_codex_rules_are_linked_and_removed_with_the_harness(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            env = {**os.environ, "HOME": home}
            target = Path(home) / ".codex" / "rules" / "default.rules"

            subprocess.run(["bash", str(INSTALL_SCRIPT)], env=env, check=True, capture_output=True)

            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), AGENTS_DIR / "codex" / "rules" / "default.rules")

            subprocess.run(
                ["bash", str(INSTALL_SCRIPT), "--uninstall"],
                env=env,
                check=True,
                capture_output=True,
            )

            self.assertFalse(target.exists())
            self.assertFalse(target.is_symlink())


if __name__ == "__main__":
    unittest.main()
