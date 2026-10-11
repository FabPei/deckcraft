"""Static guardrails: a refactor must not accidentally remove the human PR gate."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CODING = (ROOT / ".github/workflows/contribute.yml").read_text(encoding="utf-8")
PUBLISH = (ROOT / ".github/workflows/publish-approved.yml").read_text(encoding="utf-8")


class ApprovalGateTests(unittest.TestCase):
    def test_coding_workflow_never_creates_a_pr(self):
        self.assertNotIn("gh pr create", CODING)
        self.assertNotIn("mcp__GitHub__create_pull_request", CODING)

    def test_pr_publication_is_manually_dispatched_only(self):
        event_block = PUBLISH.split("on:\n", 1)[1].split("\npermissions:", 1)[0]
        self.assertIn("  workflow_dispatch:", event_block)
        self.assertNotIn("  schedule:", event_block)
        self.assertNotIn("  push:", event_block)
        self.assertNotIn("  issue_comment:", event_block)
        self.assertNotIn("  pull_request:", event_block)

    def test_approval_checks_reviewed_commit_sha(self):
        self.assertIn("expected_sha", PUBLISH)
        self.assertIn("actual_sha", PUBLISH)
        self.assertIn('"$expected_sha" != "$actual_sha"', PUBLISH)
        self.assertIn("PR approval: upstream #", PUBLISH)

    def test_contribution_is_bounded(self):
        self.assertRegex(CODING, r"if \[ \"\$files\" -gt 20 \]")
        self.assertRegex(CODING, r"if: steps.ci_final.outputs.passed == 'true'")
        self.assertIn("Independent read-only code review", CODING)
        self.assertIn("Agent blocked: upstream #", CODING)


if __name__ == "__main__":
    unittest.main()
