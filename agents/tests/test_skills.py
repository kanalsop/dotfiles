import re
import unittest
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[1] / "skills"
EXPLICIT_ONLY_SKILLS = ("explain-visually", "grilling")


def frontmatter_lines(skill: str) -> list[str]:
    text = (SKILLS_DIR / skill / "SKILL.md").read_text()
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, f"{skill}/SKILL.md has no frontmatter"
    return match.group(1).splitlines()


class ExplicitOnlySkillsTest(unittest.TestCase):
    def test_claude_cannot_invoke_them_on_its_own(self) -> None:
        for skill in EXPLICIT_ONLY_SKILLS:
            with self.subTest(skill=skill):
                self.assertIn("disable-model-invocation: true", frontmatter_lines(skill))

    def test_claude_shows_an_argument_hint_for_the_slash_command(self) -> None:
        for skill in EXPLICIT_ONLY_SKILLS:
            with self.subTest(skill=skill):
                hints = [line for line in frontmatter_lines(skill) if line.startswith("argument-hint: ")]
                self.assertEqual(len(hints), 1)

    def test_codex_disables_implicit_invocation(self) -> None:
        for skill in EXPLICIT_ONLY_SKILLS:
            with self.subTest(skill=skill):
                config = SKILLS_DIR / skill / "agents" / "openai.yaml"
                self.assertEqual(config.read_text(), "policy:\n  allow_implicit_invocation: false\n")

    def test_other_skills_stay_available_to_the_model(self) -> None:
        others = sorted(path.name for path in SKILLS_DIR.iterdir() if path.is_dir())
        for skill in set(others) - set(EXPLICIT_ONLY_SKILLS):
            with self.subTest(skill=skill):
                self.assertNotIn("disable-model-invocation: true", frontmatter_lines(skill))
                self.assertFalse((SKILLS_DIR / skill / "agents" / "openai.yaml").exists())


if __name__ == "__main__":
    unittest.main()
