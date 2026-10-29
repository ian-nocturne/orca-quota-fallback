# Orca Quota Fallback

A development patch for [Orca](https://github.com/stablyai/orca) that distinguishes confirmed subscription exhaustion from transient service errors and prepares bounded continuation through another billing route.

**Status: guarded native integration, disabled unless a host supplies verified billing configuration.** The implementation supports same-provider Claude subscription → Claude API and Codex subscription → OpenAI API continuation through Orca's registered native provider children. Session ownership, personal Stop, shutdown, account binding, and uncertain recovery are handled in the native host path. No production credit verifier, API keys, account configuration, signed application build, or deployment is included.

Antigravity cross-provider handoff is **not implemented**. An unavailable Antigravity execution adapter is reported and skipped so it cannot trap an otherwise verified same-provider API route.

## Behavior

- Accept only the provider's explicit quota error codes; a generic HTTP 429, HTTP 502, timeout, or authentication failure is insufficient.
- Preserve the source session and turn identity, block duplicate continuation, and retain uncertain dispatches for reconciliation.
- Require fresh availability evidence and compatible model requirements.
- Reserve maximum API costs across sessions sharing a credit pool. Do not infer free credits from successful authentication.
- Keep paid overflow disabled and preserve existing approval boundaries.

The supported execution routes are Claude subscription → verified Claude API credit and Codex subscription → verified OpenAI API credit. The policy model can express Antigravity priority, but this release does not execute that handoff.

A trusted host must provide `NativeQuotaFallbackConfig.verify` and `readApiKey`. Verification must be fresh and bound to the exact account, credential reference, model, and enforceable maximum debit. A configured dollar budget or a successful API login does not prove that paid overflow is blocked. In particular, the Codex API route has no CLI USD-cap flag: an externally verified debit cap is required before it is eligible. The default host configuration does not enable automatic spending.

## Apply and validate

This repository distributes an allowlisted patch, not an Orca binary or a copy of a user's workspace. See [VALIDATION.md](VALIDATION.md) for the pinned upstream base and reproducible commands. Review the patch before applying it. Do not enable execution merely because the unit tests pass.

To regenerate from a reviewed Orca worktree:

```sh
python3 scripts/export_patch.py --source /path/to/orca-worktree
```

The exporter rejects a source outside the pinned upstream ancestry, private-path/key patterns, binary payloads, and source changes during export. Its allowlist is `patch-files.json`. Committed content for these paths must match the public base; the export contains reviewed working-tree changes only. That scan is a basic release guard, not a substitute for manual review or a secret scanner.

## Why a native integration?

[LiteLLM](https://docs.litellm.ai/docs/routing) offers API fallback and routing. [CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) connects CLI providers through API interfaces. Orca still needs explicit integration for native session ownership, Stop, shutdown, permission continuity, and recovery. This project explores that application-level integration.

## License

MIT. Orca-derived code retains the upstream copyright in [LICENSE](LICENSE). This project is an independent patch and is not an official Orca release.

## 한국어

확실한 구독 한도 초과에만 반응하는 Orca 자동 전환 개발 패치입니다. 현재 스냅샷은 Claude·Codex의 같은 제공자 API 전환을 Orca native 실행 관리에 연결한 **비활성 기본값의 개발 패치**입니다. Antigravity 교대는 지원하지 않습니다. 운영 활성화에는 현재 크레딧과 실제 최대 차감액·유료 차단을 입증하는 호스트 검증기가 필요하며, 이 저장소에는 그 계정별 설정을 포함하지 않습니다. 인증 정보, 개인 경로, 대화, 작업 데이터는 배포하지 않습니다.
