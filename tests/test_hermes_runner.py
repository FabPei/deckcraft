"""Unit and static regression tests for Hermes Agent local-only integration."""
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "scripts" / "local_agent.py").read_text(encoding="utf-8")
spec = importlib.util.spec_from_file_location(
    "validate_review", ROOT / "scripts" / "validate_review.py"
)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def verdict(events):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / "result.jsonl"
        path.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
        return parser.check_review(path)


class HermesTests(unittest.TestCase):
    def test_uses_hermes_cli_and_oneshot_structured_output(self):
        self.assertIn('"hermes", "chat", "--oneshot"', SOURCE)
        self.assertIn('"--format", "stream-json"', SOURCE)
        self.assertIn('"--query-file"', SOURCE)
        self.assertNotIn('"opencode", "run"', SOURCE)

    def test_hermes_tools_are_restricted_by_role(self):
        self.assertIn('toolset = "file" if role == "build" else "todo"', SOURCE)
        self.assertIn('"--toolsets", toolset', SOURCE)
        self.assertNotIn('"--yolo"', SOURCE)
        self.assertNotIn('"--toolsets", "terminal"', SOURCE)

    def test_uses_existing_local_hermes_provider(self):
        setup = (ROOT / "scripts" / "setup-local.ps1").read_text(encoding="utf-8")
        self.assertIn("hermes model", setup)
        self.assertNotIn("opencode-ai", setup)
        run = (ROOT / "scripts" / "run-local.ps1").read_text(encoding="utf-8")
        self.assertNotIn("mimo.dpapi", run)
        self.assertIn("local_agent.py", run)

    def test_review_passes_only_single_terminal_result(self):
        self.assertTrue(verdict([
            {"type": "system", "subtype": "init"},
            {"type": "text", "text": "PASS"},
            {"type": "result", "exit_code": 0, "text": "PASS"},
        ])[0])

    def test_review_fails_on_embedded_pass_text(self):
        for result in ("PASS: likely okay", "Probably PASS", "FAIL: wrong", ""):
            with self.subTest(result=result):
                self.assertFalse(verdict([
                    {"type": "result", "exit_code": 0, "text": result}
                ])[0])

    def test_review_fails_on_model_error(self):
        self.assertFalse(verdict([
            {"type": "result", "exit_code": 1, "text": "PASS"},
        ])[0])
        self.assertFalse(verdict([
            {"type": "result", "exit_code": 0, "text": "PASS", "error": "failed"},
        ])[0])

    def test_review_fails_without_exactly_one_terminal_result(self):
        valid = {"type": "result", "exit_code": 0, "text": "PASS"}
        self.assertFalse(verdict([])[0])
        self.assertFalse(verdict([valid, valid])[0])

    def test_review_fails_on_invalid_stream(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / "broken.jsonl"
            path.write_text("not a json object\n", encoding="utf-8")
            self.assertFalse(parser.check_review(path)[0])


if __name__ == "__main__":
    unittest.main()
