import json
import shutil
import subprocess
import unittest
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[1]
CLAUDE_SETTINGS = AGENTS_DIR / "claude" / "settings.json"
CODEX_RULES = AGENTS_DIR / "codex" / "rules" / "default.rules"


class CommandRulesTest(unittest.TestCase):
    def test_claude_allows_read_only_github_commands_only(self) -> None:
        settings = json.loads(CLAUDE_SETTINGS.read_text())
        allowed = settings["permissions"]["allow"]

        self.assertIn("Bash(gh pr list:*)", allowed)
        self.assertIn("Bash(gh pr view:*)", allowed)
        self.assertNotIn("Bash(gh pr create:*)", allowed)
        self.assertNotIn("Bash(gh pr merge:*)", allowed)

    @unittest.skipUnless(shutil.which("codex"), "Codex CLI is required to evaluate command rules")
    def test_codex_rules_allow_listing_but_not_mutating_pull_requests(self) -> None:
        def decision(*command: str) -> str:
            result = subprocess.run(
                [
                    "codex",
                    "execpolicy",
                    "check",
                    "--pretty",
                    "--rules",
                    str(CODEX_RULES),
                    "--",
                    *command,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return json.loads(result.stdout).get("decision", "prompt")

        self.assertEqual(decision("gh", "pr", "list"), "allow")
        self.assertNotEqual(decision("gh", "pr", "merge", "17"), "allow")


if __name__ == "__main__":
    unittest.main()
