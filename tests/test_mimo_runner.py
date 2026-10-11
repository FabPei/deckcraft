"""Offline checks for MiMo/OpenCode configuration and review safety."""
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "validate_review", ROOT / "scripts" / "validate_review.py"
)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def verdict(events):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / "review.jsonl"
        path.write_text("\n".join(json.dumps(event) for event in events), encoding="utf-8")
        return parser.check_review(path)


class MiMoTests(unittest.TestCase):
    def test_config_keeps_key_out_of_source_and_disables_shell(self):
        path = ROOT / "config" / "opencode-mimo.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        provider = config["provider"]["mimo"]
        self.assertEqual(provider["options"]["apiKey"], "{env:MIMO_API_KEY}")
        self.assertEqual(provider["options"]["baseURL"], "{env:MIMO_BASE_URL}")
        self.assertIn("mimo-v2.6-flash", provider["models"])
        self.assertIn("mimo-v2.6-pro", provider["models"])
        for agent in ("build", "reviewer"):
            self.assertEqual(config["agent"][agent]["permission"]["bash"], "deny")
            self.assertEqual(config["agent"][agent]["permission"]["external_directory"], "deny")
            self.assertEqual(config["agent"][agent]["permission"]["webfetch"], "deny")
        self.assertEqual(config["agent"]["reviewer"]["permission"]["edit"], "deny")

    def test_review_pass(self):
        self.assertTrue(verdict([{"type": "text", "part": {"text": "PASS"}}])[0])

    def test_review_only_passes_exact_verdict(self):
        for text in ("PASS: looks okay", "Probably PASS", "FAIL: no tests", ""):
            with self.subTest(text=text):
                self.assertFalse(verdict([{"type": "text", "part": {"text": text}}])[0])

    def test_review_fails_closed_on_error(self):
        ok, reason = verdict([
            {"type": "error", "error": {"message": "Invalid credentials"}},
            {"type": "text", "part": {"text": "PASS"}},
        ])
        self.assertFalse(ok)
        self.assertIn("error", reason)

    def test_review_fails_closed_if_empty_or_malformed(self):
        self.assertFalse(verdict([])[0])
        with tempfile.TemporaryDirectory() as folder:
            f = pathlib.Path(folder) / "broken.jsonl"
            f.write_text("this is not json\n")
            self.assertFalse(parser.check_review(f)[0])


if __name__ == "__main__":
    unittest.main()
