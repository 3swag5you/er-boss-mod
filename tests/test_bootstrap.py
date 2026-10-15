import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOL = "openai/gpt-6.1-sol#high"
FLASH = "opencode-go/deepseek-v4.1-flash"


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "opencode.json").read_text())

    def test_models_modes_and_explicit_commands(self):
        self.assertEqual(self.config["default_agent"], "planner")
        for role, model, mode in [
            ("planner", SOL, "primary"),
            ("implementer", FLASH, "subagent"),
            ("reviewer", SOL, "subagent"),
        ]:
            agent = self.config["agents"][role]
            self.assertEqual(agent["model"], model)
            self.assertEqual(agent["mode"], mode)
            name = {"planner": "er-plan", "implementer": "er-implement", "reviewer": "er-review"}[role]
            command = self.config["commands"][name]
            self.assertEqual(command["agent"], role)
            self.assertEqual(command["model"], model)
            self.assertEqual(command["subagent"], role != "planner")
            self.assertIn("$ARGUMENTS", command["template"])

    def test_role_permissions(self):
        for role in ("implementer", "reviewer"):
            rules = self.config["agents"][role]["permissions"]
            child_rules = [r for r in rules if r["action"] == "subagent"]
            self.assertEqual(child_rules[-1], {"action": "subagent", "resource": "*", "effect": "deny"})
        rules = self.config["agents"]["reviewer"]["permissions"]
        self.assertIn({"action": "edit", "resource": "*", "effect": "deny"}, rules)
        shell = [r for r in rules if r["action"] == "shell"]
        self.assertEqual(shell[0], {"action": "shell", "resource": "*", "effect": "ask"})
        expected = {"git status --short --branch", "git diff --", "git diff --cached --", "git diff --check", "git diff --cached --check", "git log -5 --oneline", "git ls-files"}
        self.assertEqual({r["resource"] for r in shell[1:]}, expected)
        self.assertTrue(all(r["effect"] == "allow" for r in shell[1:]))
        self.assertIn("Do not mutate", self.config["agents"]["reviewer"]["system"])

    def test_scope_and_existing_session_guidance(self):
        for filename in ("README.md", "AGENTS.md"):
            text = (ROOT / filename).read_text()
            self.assertIn("Mod planning is deferred", text)
            self.assertIn(SOL, text)
            self.assertIn(FLASH, text)
        readme = (ROOT / "README.md").read_text()
        self.assertIn("existing session", readme)
        self.assertIn("/er-plan", readme)
        self.assertIn("authentication", readme)
        self.assertNotIn("warming", self.config)
        for name in ("package.json", "pyproject.toml", "Cargo.toml", "CMakeLists.txt"):
            self.assertFalse((ROOT / name).exists())

    def test_sensitive_paths_are_ignored(self):
        paths = [".env", ".env.local", "game/example.bin", "assets/game/example.bin", "saves/example.sl2", "backup/example.sl2.bak", "build/output.bin", "dist/mod.zip", "tests/__pycache__/test.pyc"]
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin"],
            cwd=ROOT, input="\n".join(paths) + "\n", text=True,
            capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(set(result.stdout.splitlines()), set(paths))


if __name__ == "__main__":
    unittest.main()
