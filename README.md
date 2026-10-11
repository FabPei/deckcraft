# DeckCraft Contribution Automation

Public control repository for automated contributions to [storytold/deckcraft](https://github.com/storytold/deckcraft). **This is not a copy/fork of DeckCraft's source code.**

## Safety contract

- The scout selects eligible upstream bugs with no existing upstream PR.
- Codex edits a disposable checkout of upstream, obeys the upstream `AGENTS.md`, and runs validation.
- Finished work is pushed to a separate **public, genuine GitHub fork** on an `agent/issue-N` branch.
- An issue in **this** public controller repository contains the review/approval report.
- **No upstream pull request is opened automatically.** Only a manually dispatched `Publish approved PR` workflow can create one.
- No automated merging, no write access to upstream, no unconditional force push.
- If tests fail, the candidate is not submitted.

## One-time setup

1. Create a **public fork** of `storytold/deckcraft` named `FabPei/deckcraft-contrib` (use GitHub's **Fork**, not **New repository**). The name `FabPei/deckcraft` is already occupied by this private controller. Leave the parent/official upstream relationship intact.
2. Add repository **Actions secrets** to this private controller:
   - `OPENAI_API_KEY`: key billed for Codex runs.
   - `CONTRIBUTION_TOKEN`: GitHub PAT authorized to push branches to your public fork and open PRs against upstream. Do not paste it in chat or files. A classic token with `public_repo` scope is the straightforward option; limit exposure and rotate as appropriate.
3. Optional **Actions variable** `CONTRIBUTION_REPO` set to `FabPei/deckcraft-contrib` (this is also the default).
4. Ensure Actions are enabled; run **Actions → DeckCraft contribution agent → Run workflow** to test. Scheduled runs occur Monday, Wednesday and Friday at 06:17 UTC; a run with missing secrets or fork skips coding safely.
5. Review the newly created issue `PR approval: upstream #N` in this repository, inspect the branch, diff and test evidence.
6. When you approve, run **Actions → Publish approved DeckCraft PR → Run workflow**, entering the issue number. That explicit manual dispatch is the sole PR-creation path.

## How it works

`scripts/select_issue.py` pulls upstream issues, upstream PRs and existing branches in your contribution fork. It prioritizes user-facing reproducible bugs and avoids overlap with current PRs. The coding action uses the official `openai/codex-action` with workspace-only permissions. Cargo checks run independently of the model. After a single automatic repair attempt, a separate read-only Codex review checks the patch. Only when validation and review pass does a dedicated publishing step push code to the fork and create an **controller** approval issue.

The controller does not make promises of successful automation if secrets, a public fork, runner time or model access are unavailable. Check the GitHub Actions log.

## Costs and guardrails

- One candidate per execution; at most one active workflow at a time; max 55 minutes per run.
- Three scheduled runs per week instead of hourly. Manual dispatch is available.
- Uses GitHub-hosted Linux runners (minutes may be billed for this private repo) plus API token charges.
- No API key reaches Codex shell scripts; credentials are supplied only to the official Codex action and post-review git-push step.
- Model choice can be changed via `CODEX_MODEL` Action variable; the default is chosen by the official action.
- Prefer a local/self-hosted runner if recurring Actions minutes become material, after verifying its isolation and toolchain.
- Maintainer responses and PR merge decisions remain upstream's responsibility.

See [AGENTS.md](AGENTS.md) for agent policy.
