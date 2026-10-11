"""Fail-closed regression checks for local-only DeckCraft PR authorization."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGENT = (ROOT / "scripts" / "local_agent.py").read_text(encoding="utf-8")
RUN = (ROOT / "scripts" / "run-local.ps1").read_text(encoding="utf-8")
PUBLISH = (ROOT / "scripts" / "approve-pr.ps1").read_text(encoding="utf-8")
SCHEDULE = (ROOT / "scripts" / "enable-schedule.ps1").read_text(encoding="utf-8")
SETUP = (ROOT / "scripts" / "setup-local.ps1").read_text(encoding="utf-8")


class ApprovalGateTests(unittest.TestCase):
    def test_no_cloud_coding_workflows_remain(self):
        self.assertFalse((ROOT / ".github" / "workflows" / "contribute.yml").exists())
        self.assertFalse((ROOT / ".github" / "workflows" / "publish-approved.yml").exists())
        self.assertFalse((ROOT / ".github" / "workflows" / "controller-ci.yml").exists())

    def test_pr_creation_only_in_explicit_publish_command(self):
        self.assertIn("def publish(issue):", AGENT)
        self.assertIn("if not sys.stdin.isatty():", AGENT)
        self.assertIn("input(f\"Type PUBLISH #{issue}", AGENT)
        self.assertIn('"pr", "create"', AGENT)
        self.assertIn('run(args.issue) if args.action == "run" else publish(args.issue)', AGENT)
        self.assertIn("publish --issue $Issue", PUBLISH)
        self.assertNotIn('"pr", "create"', RUN)
        self.assertNotIn('"pr", "create"', SCHEDULE)

    def test_exact_sha_is_checked_before_confirmation(self):
        self.assertIn("remote[0] != sha", AGENT)
        self.assertIn("refs/heads/agent/issue-", AGENT)
        self.assertIn("existing_pr(issue)", AGENT)

    def test_quality_gates_and_review(self):
        self.assertIn('"cargo", "xtask", "ci"', AGENT)
        self.assertIn("from validate_review import check_review", AGENT)
        self.assertIn("if not cargo_ci(", AGENT)
        self.assertIn("scout(issue, require=True)", AGENT)
        self.assertIn("1800", AGENT)
        self.assertIn("len(files) > 20", AGENT)

    def test_schedule_is_windows_local_only(self):
        self.assertIn("New-ScheduledTaskTrigger", SCHEDULE)
        self.assertIn("run-local.ps1", SCHEDULE)
        self.assertNotIn("gh workflow run", SCHEDULE)
        self.assertNotIn("gh pr create", SCHEDULE)

    def test_local_secret_not_in_repository(self):
        self.assertIn("ConvertFrom-SecureString", SETUP)
        self.assertIn("ConvertTo-SecureString", RUN)
        self.assertIn("ZeroFreeBSTR", RUN)
        self.assertIn(".local/", (ROOT / ".gitignore").read_text(encoding="utf-8"))
        self.assertNotIn("OPENAI_API_KEY", AGENT)


if __name__ == "__main__":
    unittest.main()
