import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "merge_config.py"


def run_merge(source: Path, target: Path, *options: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *options, str(source), str(target)],
        capture_output=True,
        text=True,
        check=True,
    )


class MergeConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write(self, name: str, text: str) -> Path:
        path = self.dir / name
        path.write_text(text)
        return path

    def backups(self, target: Path) -> list[Path]:
        return sorted(self.dir.glob(f"{target.name}.bak.*"))

    def test_json_source_keys_override_and_target_only_keys_survive(self) -> None:
        source = self.write("src.json", json.dumps({"env": {"A": "1"}, "list": ["new"], "flag": True}))
        target = self.write("settings.json", json.dumps({"theme": "auto", "env": {"A": "0", "B": "2"}, "list": ["old", "x"]}))

        run_merge(source, target)

        self.assertEqual(
            json.loads(target.read_text()),
            {"theme": "auto", "env": {"A": "1", "B": "2"}, "list": ["new"], "flag": True},
        )

    def test_missing_target_is_created_from_source_without_backup(self) -> None:
        source = self.write("src.json", json.dumps({"a": 1}))
        target = self.dir / "nested" / "settings.json"

        run_merge(source, target)

        self.assertEqual(json.loads(target.read_text()), {"a": 1})
        self.assertEqual(list(target.parent.glob("*.bak.*")), [])

    def test_changed_target_is_backed_up_with_original_content(self) -> None:
        original = '{"theme": "auto"}'
        source = self.write("src.json", json.dumps({"a": 1}))
        target = self.write("settings.json", original)

        run_merge(source, target)

        [backup] = self.backups(target)
        self.assertEqual(backup.read_text(), original)

    def test_rerun_leaves_target_untouched_and_creates_no_backup(self) -> None:
        source = self.write("src.toml", 'personality = "pragmatic"\n')
        original = '# keep my formatting\npersonality   =   "pragmatic"\n'
        target = self.write("config.toml", original)

        result = run_merge(source, target)

        self.assertEqual(target.read_text(), original)
        self.assertEqual(self.backups(target), [])
        self.assertIn("unchanged", result.stdout)

    def test_dry_run_reports_without_writing(self) -> None:
        source = self.write("src.json", json.dumps({"a": 1}))
        target = self.write("settings.json", "{}")

        result = run_merge(source, target, "--dry-run")

        self.assertEqual(target.read_text(), "{}")
        self.assertEqual(self.backups(target), [])
        self.assertIn("[dry-run]", result.stdout)

    def test_toml_merge_preserves_every_existing_construct(self) -> None:
        existing = """\
model = "gpt"
notify = ["say", "done \\"quoted\\"\\n"]
count = 3
ratio = 0.5

[projects."/Users/me/my app"]
trust_level = "trusted"

[hooks.state."/x/hooks.json:pre_tool_use:0:0"]
trusted_hash = "abc"

[empty]

[mcp_servers.node_repl.env]
NODE = "1"

[tui]
inline = { a = 1, "b c" = [true, false] }

[[skills.config]]
path = "/a"
enabled = false

[[skills.config]]
path = "/b"

[skills.config.extra]
x = 1
"""
        source = self.write("src.toml", '[tui]\nuse_theme_colors = true\n\n[features.multi_agent_v2]\nenabled = true\n')
        target = self.write("config.toml", existing)

        run_merge(source, target)

        expected = tomllib.loads(existing)
        expected["tui"]["use_theme_colors"] = True
        expected["features"] = {"multi_agent_v2": {"enabled": True}}
        self.assertEqual(tomllib.loads(target.read_text()), expected)


if __name__ == "__main__":
    unittest.main()
