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

    def test_pr_creation_only_in_the_bounded_publish_command(self):
        self.assertIn("def publish(issue, interactive=True):", AGENT)
        self.assertIn('\"pr\", \"create\"', AGENT)
        self.assertNotIn('\"pr\", \"create\"', RUN)
        self.assertNotIn('\"pr\", \"create\"', SCHEDULE)
        self.assertIn("publish --issue $Issue", PUBLISH)
        # The typed confirmation stays the manual path; unattended publishing is
        # opt-in, budgeted and kill-switchable, and never merges or approves.
        self.assertIn("Type PUBLISH #{issue}", AGENT)
        self.assertIn("def publish_budget():", AGENT)
        self.assertIn('run_parser.add_argument("--publish"', AGENT)
        self.assertIn("publish(issue, interactive=False)", AGENT)
        self.assertNotIn('"pr", "merge"', AGENT)
        self.assertNotIn('"pr", "approve"', AGENT)

    def test_unattended_publish_budget_bounds_the_tracker(self):
        self.assertIn("MAX_OPEN_PRS = 3", AGENT)
        self.assertIn("MAX_NEW_PRS_PER_DAY = 2", AGENT)
        self.assertIn("state=all&sort=created&direction=desc", AGENT)
        self.assertIn("PAUSE = STATE / \"PAUSE\"", AGENT)
        self.assertIn("if PAUSE.exists():", AGENT)

    def test_exact_sha_is_checked_before_confirmation(self):
        self.assertIn("remote[0] != sha", AGENT)
        self.assertIn("refs/heads/agent/issue-", AGENT)
        self.assertIn("existing_pr(issue)", AGENT)

    def test_quality_gates_and_review(self):
        self.assertIn('"cargo", "xtask", "ci"', AGENT)
        self.assertIn("from validate_review import check_run, check_review", AGENT)
        self.assertIn("if not cargo_ci(", AGENT)
        self.assertIn("scout(issue, require=True)", AGENT)
        self.assertIn("1800", AGENT)
        self.assertIn("len(files) > 20", AGENT)

    def test_schedule_is_windows_local_only(self):
        self.assertIn("New-ScheduledTaskTrigger", SCHEDULE)
        self.assertIn("run-local.ps1", SCHEDULE)
        self.assertNotIn("gh workflow run", SCHEDULE)
        self.assertNotIn("gh pr create", SCHEDULE)

    def test_credentials_remain_managed_by_local_hermes(self):
        self.assertIn("hermes model", SETUP)
        self.assertIn('"hermes", "chat"', AGENT)
        self.assertIn(".local/", (ROOT / ".gitignore").read_text(encoding="utf-8"))
        self.assertNotIn("opencode", RUN.lower())
        self.assertNotIn("OPENAI_API_KEY = ", AGENT)
        self.assertNotIn("gh workflow run", AGENT)
        self.assertIn('toolset = "file" if role == "build" else "todo"', AGENT)
        self.assertNotIn("enable-schedule.ps1", SETUP)



if __name__ == "__main__":
    unittest.main()
