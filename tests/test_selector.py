"""Offline checks for the automatic DeckCraft issue scout."""
import importlib.util
import pathlib
import unittest

path = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "select_issue.py"
spec = importlib.util.spec_from_file_location("select_issue", path)
scout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scout)


class IssueScoutTests(unittest.TestCase):
    def test_closed_issue_reference_in_pr_body(self):
        pr = {"title": "fix: something", "body": "Fixes #69\nCloses #104"}
        self.assertEqual(scout.refs_in_pr(pr), {69, 104})

    def test_parenthesized_issue_in_title(self):
        self.assertIn(93, scout.refs_in_pr({"title": "Bullets fixed (#93)", "body": ""}))

    def test_explicit_pick_ignores_the_scoring_heuristics(self):
        issue = {
            "number": 845,
            "title": "Pdfs file are 50x too large",
            "body": "The attached document produces a 200+Mo pdf while libreoffice produces a 4Mo pdf.",
            "labels": [{"name": "priority: medium"}],
        }
        self.assertIsNone(scout.score(issue))
        picked = scout.choose([issue], set(), explicit=845)
        self.assertEqual([i["number"] for _, i in picked], [845])
        self.assertEqual(scout.choose([issue], set()), [])
        self.assertEqual(scout.choose([issue], {845}, explicit=845), [])

    def test_prefers_high_value_core_bug(self):
        issue = {
            "number": 69,
            "title": "Font weights beyond Regular and Bold",
            "body": "Expected extra weights when importing a PowerPoint presentation.",
            "labels": [],
        }
        self.assertGreater(scout.score(issue), 50)

    def test_rejects_vague_generic_feature_request(self):
        issue = {
            "number": 999,
            "title": "Feature Request: more widgets",
            "body": "Please implement a lot of features with no bounded repro case.",
            "labels": [{"name": "enhancement"}],
        }
        self.assertIsNone(scout.score(issue))

    def test_rejects_crash_driver_bug_without_hardware(self):
        issue = {
            "number": 153,
            "title": "[Windows] GPU crash in DXC driver",
            "body": "Steps to reproduce and log: Device is lost on certain GPUs.",
            "labels": [{"name": "bug"}],
        }
        self.assertIsNone(scout.score(issue))

    def test_internal_blocker_suppresses_repeat(self):
        self.assertEqual(
            scout.CONTROL.match("Agent blocked: upstream #69").group(1), "69"
        )
        self.assertEqual(
            scout.CONTROL.match("PR approval: upstream #104").group(1), "104"
        )


if __name__ == "__main__":
    unittest.main()
