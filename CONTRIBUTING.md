# Contributing

Work against the exact upstream commit in `upstream.json`. Preserve Orca's license and follow its contributor instructions.

Keep each change focused on quota provenance, lifecycle-safe continuation, authentication isolation, or bounded spending. Update the export allowlist explicitly when adding a source file. Never export an entire local workspace or its Git history.

Cover false-positive errors, stale state, concurrent sends, process crashes, unknown dispatch, account isolation, Stop/shutdown, and exhausted budgets. Use fake providers and credentials in tests. Network calls and real credit consumption are not required for unit tests.

Document implemented versus intended behavior honestly. Do not mark a route operational without evidence that the native host manages its cancellation, ownership, and recovery. Run upstream checks and record any unavailable checks in the pull request.
