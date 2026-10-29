---
name: quota-fallback
description: Resume quota-limited agent work through an approved API credit route after the user confirms enabling a spending cutoff. Use for supervised Claude or Codex quota fallback, not unrelated skills or transient errors.
---

# Supervised quota fallback

Use this workflow when an authorized task needs API credit fallback after confirmed subscription exhaustion. Keep the current owner and reconcile any running or uncertain execution before resuming. Preserve requested models, approvals, and local fallback ordering.

## User-confirmed spending cutoff

Before the first API execution in this skill invocation:

1. Identify the provider, account/project, intended work, and existing budget from context. Read available credit eligibility, balance and expiry evidence without exposing secrets. If essential scope is missing, include it in the confirmation request.
2. Ask the user to enable the actual spending cutoff for that account/project, keep automatic recharge off, and confirm completion. Explain known enforcement delay once when relevant; do not claim zero overspend is guaranteed. A notification-only budget is not the requested cutoff. Do not invent a budget or enable billing settings yourself without authorization.
3. Use a concise prompt such as: “이번 작업에 사용할 [공급자·계정/프로젝트]의 과금차단기를 활성화하고 자동 충전을 꺼주세요. 적용하셨으면 ‘올렸어, 진행해’라고 알려주세요.” State the already agreed budget when one exists. Explain that this confirmation is required by this skill's user-confirmed spending-cutoff workflow.
4. Wait for an actual affirmative user reply. “올렸어”, “설정했어”, or equivalent confirmation in that clearly stated scope permits execution. The request to adopt this workflow, an agent-written note, elapsed time, or a preselected option is not confirmation that a cutoff was enabled.
5. Record the user's confirmation, time, provider/account/project, work scope and known budget as `user_confirmed`, not `provider_verified`. Proceed with eligible API execution without demanding an unattainable atomic-debit proof or repeatedly asking for the same confirmation within the approved scope. An existing explicit confirmation for that same scope can be reused while still applicable.

If the provider/account/project, budget or task scope changes, or the user revokes confirmation, obtain a new scoped confirmation. If current evidence contradicts the confirmation (for example, the cutoff is still off), report the concrete mismatch and resolve it before execution. Product-ineligible credits, exhausted/expired credits, invalid authentication and running/unknown work remain blockers; spending-cutoff confirmation does not change those facts. Do not demand screenshots or keys in chat.

## Execution and boundaries

- Use existing authorized credentials through supported provider interfaces; preserve subscription authentication and permissions.
- Respect the agreed budget; never enable automatic recharge, purchase credits, or authorize paid overflow by inference.
- Resume once with the original task/checkpoint; track acceptance separately from completion. Stop on budget/credit exhaustion or an uncertain dispatch, rather than replaying it through another route.
- No confirmation means no dependent API execution. Read-only discovery and preparation may continue.
- This is a supervised skill approval workflow. It does not enable Orca's unattended native fallback, fabricate a `billingProof`, or bypass the native controller's independent evidence checks. Use only a supported supervised execution path and report if none is available.
