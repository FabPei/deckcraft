"""Regression tests: optional clones never block a local agent run."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "scripts" / "local_agent.py").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location(
    "local_agent", ROOT / "scripts" / "local_agent.py"
)
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


class OptionalCloneTests(unittest.TestCase):
    def test_standards_clone_is_optional_in_prepare(self):
        self.assertIn(
            'clone_optional("https://github.com/storytold/craftrules.git", RULES)',
            SOURCE,
        )
        # The build-critical font checkout stays fail-closed.
        self.assertIn(
            'clone_once("https://github.com/storytold/craft-fonts.git", FONTS)',
            SOURCE,
        )

    def test_unreachable_optional_clone_does_not_raise(self):
        def failing_clone(url, directory):
            raise agent.Stopped("git exited with status 128")

        original = agent.clone_once
        agent.clone_once = failing_clone
        try:
            agent.clone_optional("https://example.invalid/rules.git", pathlib.Path("nowhere"))
        finally:
            agent.clone_once = original

    def test_working_optional_clone_is_not_swallowed(self):
        calls = []

        def ok_clone(url, directory):
            calls.append(url)

        original = agent.clone_once
        agent.clone_once = ok_clone
        try:
            agent.clone_optional("https://example.invalid/rules.git", pathlib.Path("nowhere"))
        finally:
            agent.clone_once = original
        self.assertEqual(calls, ["https://example.invalid/rules.git"])


if __name__ == "__main__":
    unittest.main()
