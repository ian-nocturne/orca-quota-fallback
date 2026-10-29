# Validation

The base revision is pinned in `upstream.json`. Apply to a clean checkout of `https://github.com/stablyai/orca` at that revision:

```sh
git apply --check /path/to/quota-fallback.patch
git apply /path/to/quota-fallback.patch
```

Install dependencies using the package manager version pinned by upstream. Use a real per-worktree dependency directory; do not run an auto-installing package manager through a `node_modules` symlink to another workspace.

From the patched Orca checkout:

```sh
ORCA_BACKGROUND_LAUNCH=1 ./node_modules/.bin/vitest run --config config/vitest.config.ts src/main/native-chat/quota-fallback-policy.test.ts src/main/native-chat/quota-fallback-ledger.test.ts src/main/native-chat/quota-fallback-native.test.ts src/main/native-chat/quota-fallback-native-launch.test.ts src/main/claude/claude-structured-launch-resolution.test.ts src/main/codex/codex-structured-launch-resolution.test.ts src/main/claude/claude-usage-limits.test.ts src/main/codex/codex-usage-limits.test.ts src/main/native-chat/agent-session-wire/structured-agent-session-queued-action-receipts.test.ts src/main/native-chat/agent-session-wire/structured-conversation-command.test.ts src/main/native-chat/agent-session-wire/structured-agent-session-rewind.test.ts src/main/native-chat/agent-session-wire/structured-agent-session-clear-rewind.test.ts src/main/native-chat/agent-session-wire/structured-conversation-command-child-work.test.ts --maxWorkers=2
pnpm tc:node
pnpm check:changed --maxWorkers=2
```

The native implementation passed all 202 tests in 13 suites using upstream’s `config/vitest.config.ts`, and the Node TypeScript check, changed-file lint, and Git diff whitespace check passed. An independent final rerun of the two native suites passed all 12 tests. These results describe the reviewed development snapshot; changes after that run require revalidation before publication. The complete upstream gate was not completed in that development environment because its shared dependency symlink was incompatible with the package manager’s task-state validation. No full upstream-suite pass is claimed.

Unit tests use simulated execution. They cover native ownership, source fencing, restart replay, Stop during verification or secret retrieval, account binding, expiry, native child cleanup, and authentication routing. They do not prove successful real billing failover or no-paid-overflow enforcement for any account. No production deployment, signed desktop package, mobile verification, or live API execution is claimed.

The release exporter has standalone tests (no network or API calls):

```sh
python3 scripts/test_export_patch.py
```

The initial exporter suite has six passing tests: exact allowlist/application, potential key rejection, wrong-base refusal, path traversal refusal, committed allowlist divergence refusal, and concurrent source edit refusal.

The final 36-file patch applied cleanly to the pinned public base; every resulting source file matched the reviewed worktree. Changed-file oxlint and whitespace checks passed. The patch SHA-256 is recorded in `patches/quota-fallback.json`.

Durability was checked on a POSIX host. If a platform cannot flush the reservation directory, dispatch fails closed; Windows operation is not verified.
