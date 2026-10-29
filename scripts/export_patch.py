#!/usr/bin/env python3
"""Export a reviewed path allowlist; never copy the worktree or its Git history."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = [
    re.compile(rb'(?:/Users/|/home/)[^\s"\'<>]+'),
    re.compile(rb'(?i)[A-Z]:\\Users\\[^\s"\'<>]+'),
    re.compile(rb'\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{24,}'),
    re.compile(rb'\b(?:ghp_|github_pat_|vcp_)[A-Za-z0-9_]{20,}'),
    re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
]

def git(source, *args, accepted=(0,)):
    result = subprocess.run(['git', '-C', str(source), *args], capture_output=True)
    if result.returncode not in accepted:
        raise RuntimeError('Git command failed: ' + args[0])
    return result.stdout


def snapshot(source, paths):
    result = {}
    for name in paths:
        path = source / name
        if path.is_symlink() or not path.resolve().is_relative_to(source):
            raise ValueError('Symlinks outside the source are not exportable: ' + name)
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path, help='Orca worktree containing reviewed changes')
    parser.add_argument('--output', type=Path, default=ROOT / 'patches' / 'quota-fallback.patch')
    args = parser.parse_args()
    source = args.source.resolve()
    upstream = json.loads((ROOT / 'upstream.json').read_text())
    paths = json.loads((ROOT / 'patch-files.json').read_text())
    if not isinstance(paths, list) or len(paths) != len(set(paths)) or not paths:
        raise ValueError('Invalid export allowlist')
    for name in paths:
        if not isinstance(name, str) or not name.startswith('src/') or '..' in Path(name).parts or Path(name).is_absolute():
            raise ValueError('Invalid allowlist path')
    ancestry = subprocess.run(['git', '-C', str(source), 'merge-base', '--is-ancestor', upstream['baseCommit'], 'HEAD'], capture_output=True)
    if ancestry.returncode != 0:
        raise ValueError('Source HEAD differs from the reviewed upstream ancestry')
    for name in paths:
        blobs = []
        for revision in (upstream['baseCommit'], 'HEAD'):
            result = subprocess.run(['git', '-C', str(source), 'rev-parse', '--verify', revision + ':' + name], capture_output=True)
            blobs.append(result.stdout.strip() if result.returncode == 0 else None)
        if blobs[0] != blobs[1]:
            raise ValueError('Committed allowlist content differs from public base: ' + name)
    before = snapshot(source, paths)
    parts = []
    for name in sorted(paths):
        tracked = git(source, 'ls-files', '--error-unmatch', '--', name, accepted=(0, 1))
        if tracked:
            parts.append(git(source, 'diff', '--no-ext-diff', '--no-textconv', '--binary', upstream['baseCommit'], '--', name))
        elif (source / name).is_file():
            # Relative paths keep machine-specific locations out of the patch headers.
            parts.append(git(source, 'diff', '--no-index', '--no-ext-diff', '--no-textconv', '--', os.devnull, name, accepted=(0, 1)))
    patch = b''.join(parts)
    if before != snapshot(source, paths):
        raise RuntimeError('Source changed while exporting; retry after the edit settles')
    if not patch:
        raise ValueError('No changes in allowlisted files')
    if b'GIT binary patch' in patch:
        raise ValueError('Binary files are not permitted in this source release')
    for pattern in PRIVATE:
        if pattern.search(patch):
            raise ValueError('Potential private data detected; review source before exporting')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(patch)
    manifest = {'upstream': upstream, 'patchSha256': hashlib.sha256(patch).hexdigest(),
                'paths': before, 'status': 'development-preview-not-production-enabled'}
    args.output.with_suffix('.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Exported {len(paths)} allowlisted paths; SHA-256 {manifest["patchSha256"]}')

if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
