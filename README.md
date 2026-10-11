# DeckCraft contribution automation

This **public controller repository** automates contributions to the original [storytold/deckcraft](https://github.com/storytold/deckcraft). This repo is **not** the upstream source code. Changes are prepared in a fresh upstream checkout, published as branches to [FabPei/deckcraft-contrib](https://github.com/FabPei/deckcraft-contrib), and proposed upstream **only after manual approval**.

## One-time setup

1. ✅ Public, genuine fork: [FabPei/deckcraft-contrib](https://github.com/FabPei/deckcraft-contrib) (parent: `storytold/deckcraft`).
2. Open [Settings → Secrets and variables → Actions](https://github.com/FabPei/deckcraft/settings/secrets/actions) and create:
   - **`MIMO_API_KEY`** — your Xiaomi MiMo API key. No OpenAI/Codex API key is required.
   - **`CONTRIBUTION_TOKEN`** — separate GitHub personal access token with permission to write branches in your public contribution fork and create pull requests to the original public upstream. Do not paste either key into GitHub issues, commit messages or chat.
3. For a regular *pay-as-you-go* Xiaomi MiMo key (`sk-...`), the official OpenAI-compatible base URL is already the default: `https://api.xiaomimimo.com/v1`.
   - For a **MiMo Token Plan** key (`tp-...`, `ttp-...`), add a GitHub **Actions variable** (not secret) `MIMO_BASE_URL` containing the **exact OpenAI-compatible base URL from your MiMo subscription dashboard**, e.g. a `https://token-plan-...xiaomimimo.com/v1` URL. The standard pay-as-you-go endpoint will **not** work with a Token Plan key.
   - If using another MiMo API reseller, consult that provider's documented endpoint and model IDs first; this controller defaults to Xiaomi's official platform.
4. Optional Actions variables:
   - `MIMO_MODEL`: `mimo-v2.6-flash` (default) or `mimo-v2.6-pro`. Start with Flash for small, bounded fixes.
   - `MIMO_REVIEW_MODEL`: reviewer model; defaults to `MIMO_MODEL`.
   - `CONTRIBUTION_REPO`: defaults to `FabPei/deckcraft-contrib`.
5. Start one run from [Actions → DeckCraft contribution agent → Run workflow](https://github.com/FabPei/deckcraft/actions/workflows/contribute.yml). The schedule runs Monday, Wednesday and Friday at 06:17 UTC after setup.
6. Review the created **`PR approval: upstream #N`** issue in this repository, the actual fork branch, and its Rust quality-gate results.
7. When you explicitly approve an upstream pull request, manually start [Publish approved DeckCraft PR](https://github.com/FabPei/deckcraft/actions/workflows/publish-approved.yml) and enter the issue number. The publisher verifies that the fork branch still matches the approved commit SHA.

## Architecture and security

- `scripts/select_issue.py`: chooses one reproducible upstream bug that has no active upstream PR or existing agent branch. The issue text is treated as untrusted data.
- `config/opencode-mimo.json`: MiMo provider using **OpenCode** (the official Xiaomi-documented integration). Configuration contains **environment variable placeholders only**, never an API key.
- `.github/workflows/contribute.yml`: the scheduled agent. Installs `opencode-ai`, runs a restricted editing agent, deterministic `cargo xtask ci`, one bounded repair attempt, then a separate read-only MiMo reviewer. It can push a candidate branch to your fork and create an approval issue but **cannot create an upstream pull request**.
- `scripts/validate_review.py`: rejects missing, malformed, errored or non-PASS review output from OpenCode.
- `.github/workflows/publish-approved.yml`: the **only** PR creation path, triggered **manually**. It checks the exact previously approved SHA.
- `tests/` and `controller-ci.yml`: offline correctness tests for the scout, reviewer parser, and PR approval security gates.

The coding agent has read/edit access to the temporary working tree **without shell, network fetch, external-directory or task tools**. Only separate deterministic GitHub Actions steps can run Rust tests and push code, and API credentials are not provided to the test or push subprocesses that do not need them. Like any LLM-based agent, the system is not immune to malicious repository content or model mistakes; validate each candidate before authorizing a PR.

## Costs and limitations

- **No OpenAI API charges.** Xiaomi MiMo usage is charged against your API account or Token Plan, depending on your key. A ChatGPT subscription has no bearing on this.
- One issue per run, one concurrent agent workflow, bounded model execution and at most one repair attempt. Rust CI may be slow, and a 55-minute GitHub Actions job limit applies.
- GitHub-hosted Actions minutes may be billed according to your repository and GitHub plan.
- After setup, the first end-to-end run must still be validated: until a candidate branch + internal approval issue exist, this is a configured pipeline, not a proven autonomous contribution system.
- GitHub maintainers ultimately decide whether an upstream PR is merged.

**No PR gets opened to `storytold/deckcraft` without your manual authorization.**
