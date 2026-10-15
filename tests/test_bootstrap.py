import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOL = "openai/gpt-6.1-sol#high"
FLASH = "opencode-go/deepseek-v4.1-flash"


def _action_matches(pattern, action):
    """Match ``action`` against a permission ``action`` pattern.

    Only opencode's documented wildcard subset is implemented: ``*`` matches
    zero or more characters and ``?`` matches exactly one, while every other
    character matches literally (so brackets are not character classes). These
    are static config checks; opencode's own matcher is never executed.
    """
    expression = "".join(
        ".*" if char == "*" else "." if char == "?" else re.escape(char) for char in pattern
    )
    return re.fullmatch(expression, action) is not None


def _rules_deciding(rules, action):
    """Ordered rules whose action pattern can decide ``action``.

    opencode resolves permission rules with the last matching rule winning, so
    a later rule overrides an earlier one, and an action pattern such as ``ed*``
    or ``*`` that matches ``action`` is included. Rules for unrelated actions
    (for example ``shell``) are ignored. This is a static ordering view of the
    declared rules, not a simulation of opencode's matcher: it asserts what the
    project config declares and cannot prove live enforcement.
    """
    return [rule for rule in rules if _action_matches(rule["action"], action)]


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

    def test_planner_edit_rules_deny_by_default_and_allow_only_markdown(self):
        """Catches any planner edit declaration other than deny-by-default plus Markdown.

        Static config check of the ordered declaration: the blanket deny must
        precede the Markdown allow, ``*.md`` must remain the rule that decides
        Markdown editing, and no later rule (including ``ed*``, ``?`` or ``*``
        action patterns, or an ``ask`` effect) may decide planner editing
        differently. Nested docs are covered only as the declared pattern; that
        matching is not executed here.
        """
        rules = self.config["agents"]["planner"]["permissions"]
        self.assertEqual(
            _rules_deciding(rules, "edit"),
            [
                {"action": "edit", "resource": "*", "effect": "deny"},
                {"action": "edit", "resource": "*.md", "effect": "allow"},
            ],
            "planner editing must stay deny-by-default with Markdown as the only allowed exception",
        )

    def test_planner_delegation_denies_by_default_and_permits_only_implementer_and_reviewer(self):
        """Catches any planner delegation declaration that blocks, widens, or reorders targets.

        Static config check of the ordered declaration: with the last matching
        rule winning, the leading blanket deny keeps every unnamed subagent
        denied, and the two following named allows keep the implementer and
        reviewer available; no later rule (including ``sub*``, ``?`` or ``*``
        action patterns) may target either agent instead.
        """
        rules = self.config["agents"]["planner"]["permissions"]
        self.assertEqual(
            _rules_deciding(rules, "subagent"),
            [
                {"action": "subagent", "resource": "*", "effect": "deny"},
                {"action": "subagent", "resource": "implementer", "effect": "allow"},
                {"action": "subagent", "resource": "reviewer", "effect": "allow"},
            ],
            "planner delegation must deny all subagents by default and leave only implementer and reviewer available",
        )

    def test_reviewer_edit_deny_stays_the_effective_rule(self):
        """Catches any reviewer declaration other than a blanket edit denial.

        Static config check: the reviewer's order-sensitive edit decision must
        stay exactly one blanket deny, so a later edit allow, an ``ed*``, ``?``
        or ``*`` action pattern, or any other effect is rejected rather than
        merely checked for the presence of a deny entry.
        """
        rules = self.config["agents"]["reviewer"]["permissions"]
        self.assertEqual(
            _rules_deciding(rules, "edit"),
            [{"action": "edit", "resource": "*", "effect": "deny"}],
            "the reviewer's blanket edit denial must remain the only rule deciding editing",
        )

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
