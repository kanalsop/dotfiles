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
        other_commands = (
            "Bash(gh pr create:*)",
            "Bash(gh pr edit:*)",
            "Bash(gh pr merge:*)",
            "Bash(gh issue create:*)",
            "Bash(gh issue close:*)",
            "Bash(gh run rerun:*)",
            "Bash(gh repo delete:*)",
            "Bash(gh api:*)",
            "Bash(gh auth token:*)",
            "Bash(gh *:*)",
        )
        for command in other_commands:
            with self.subTest(command=command):
                self.assertNotIn(command, allowed)

    @unittest.skipUnless(shutil.which("codex"), "Codex CLI is required to evaluate command rules")
    def test_codex_rules_allow_only_selected_read_only_github_commands(self) -> None:
        def evaluation(*command: str) -> dict[str, object]:
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
            return json.loads(result.stdout)

        allowed_commands = (
            ("gh", "pr", "list"),
            ("gh", "pr", "view", "17"),
            ("gh", "pr", "diff", "17"),
            ("gh", "pr", "checks", "17"),
            ("gh", "pr", "status"),
            ("gh", "issue", "list"),
            ("gh", "issue", "view", "17"),
            ("gh", "run", "list"),
            ("gh", "run", "view", "17"),
            ("gh", "repo", "view"),
        )
        for command in allowed_commands:
            with self.subTest(command=command):
                self.assertEqual(evaluation(*command).get("decision"), "allow")

        other_commands = (
            ("gh", "pr", "create"),
            ("gh", "pr", "merge", "17"),
            ("gh", "pr", "review", "17"),
            ("gh", "pr", "edit", "17"),
            ("gh", "issue", "create"),
            ("gh", "issue", "close", "17"),
            ("gh", "issue", "edit", "17"),
            ("gh", "run", "rerun", "17"),
            ("gh", "release", "list"),
            ("gh", "repo", "delete", "example/repo"),
            ("gh", "api", "repos/example/repo", "--method", "GET"),
            ("gh", "api", "repos/example/repo", "--method", "POST"),
            ("gh", "auth", "token"),
        )
        for command in other_commands:
            with self.subTest(command=command):
                result = evaluation(*command)
                self.assertNotEqual(result.get("decision"), "allow")
                self.assertEqual(result["matchedRules"], [])


if __name__ == "__main__":
    unittest.main()
