# Billing evidence and activation

The native controller validates billing evidence before reserving a continuation and again before obtaining its API credential. It checks the evidence expiry again after asynchronous secret retrieval. This validator is implemented; a production evidence collector and debit enforcer are **not included**.

`NativeQuotaFallbackConfig.verify` returns `billingProof` alongside its candidates. A proof binds an evidence ID, exact credit pool, credential reference, source session and source turn to the native product (`orca-claude-native` or `orca-codex-native`). It must establish free-grant funding, product eligibility, disabled auto-recharge, blocked paid overflow, and an atomic maximum debit for that continuation. Evidence must be no more than 60 seconds old, unexpired, and match the requested maximum debit. Candidate expiry is shortened to the proof expiry.

`enforcement: "atomic-run-cap"` describes the required property of an external enforcement mechanism. It is **not the name of an existing provider API** and the validator does not create a cap. Never manufacture this proof from a dashboard snapshot, budget flag, environment variable, or a successful authenticated request. The privileged host adapter must obtain it from an actual enforcement mechanism. A fabricated proof can defeat any caller-supplied evidence contract.

The validator rejects missing proof, alerts, prepaid balance alone, delayed monthly cutoffs, purchased funding, ineligible products, automatic recharge, account/key/turn mismatches, stale evidence, and cap/credit mismatches. Errors hold the continuation; they do not trigger a live test or a less constrained route.

## Current provider boundaries

- [OpenAI spend limits](https://developers.openai.com/api/docs/guides/spend-limits) distinguish alerts from hard limits, but explicitly state enforcement is not instantaneous and recorded spending can exceed a limit. [Prepaid billing](https://help.openai.com/en/articles/8264644-setting-up-and-managing-prepaid-api-billing) also documents delayed cutoff. Neither alone proves an exact per-run debit ceiling.
- [Claude subscriber credits](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers) cover API and Agent SDK use, but exclude Claude Code. The grant's eligibility for the actual integration must be established. An SDK type import or executable filename is insufficient evidence of billing classification.
- Client budgets and the local reservation ledger do not intercept or price every upstream request. Do not equate them with a provider-enforced monetary ceiling. An enforcement adapter must account for concurrent requests, retries, child agents, tools, expiration, and other consumers of the same pool.

The current release remains disabled by default. It does not claim that free-credit-only operation is deployable on every provider account. All automated tests use fake proofs and credentials; no live billing assurance follows from their passing.

## Supervised user confirmation

The optional [skill workflow](skills/quota-fallback/SKILL.md) accepts the user's explicit confirmation that the scoped spending cutoff is enabled as its billing approval gate. It does not require an atomic-cap proof for supervised execution. Record that confirmation as `user_confirmed`; do not claim that it eliminates provider enforcement delay. This workflow is separate from the native automatic controller above, which still requires its structured proof. Changing the workflow itself is not confirmation that a cutoff has been enabled.
