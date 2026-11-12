import tomllib
import unittest
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "codex" / "config.toml"


class CodexConfigTest(unittest.TestCase):
    def test_esa_profile_limits_sandbox_network_to_the_esa_api(self) -> None:
        config = tomllib.loads(CONFIG.read_text())

        self.assertTrue(config["features"]["network_proxy"]["enabled"])
        self.assertEqual(config["default_permissions"], "esa_read")
        self.assertEqual(config["permissions"]["esa_read"]["extends"], ":workspace")
        self.assertTrue(config["permissions"]["esa_read"]["network"]["enabled"])
        self.assertEqual(config["permissions"]["esa_read"]["network"]["mode"], "limited")
        self.assertEqual(
            config["permissions"]["esa_read"]["network"]["domains"],
            {"api.esa.io": "allow"},
        )


if __name__ == "__main__":
    unittest.main()
