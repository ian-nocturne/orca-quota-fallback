import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('export_patch', Path(__file__).with_name('export_patch.py'))
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source = self.root / 'source'
        self.release = self.root / 'release'
        self.source.mkdir()
        self.release.mkdir()
        self.run_git('init', '-q')
        self.run_git('config', 'user.name', 'Fixture')
        self.run_git('config', 'user.email', 'fixture@example.invalid')
        (self.source / 'src').mkdir()
        (self.source / 'src/policy.ts').write_text('export const enabled = false\n')
        self.run_git('add', '.')
        self.run_git('commit', '-qm', 'fixture')
        self.base = self.run_git('rev-parse', 'HEAD').strip()
        (self.release / 'upstream.json').write_text(json.dumps({'baseCommit': self.base}))
        (self.release / 'patch-files.json').write_text(json.dumps(['src/policy.ts', 'src/new.ts']))
        (self.source / 'src/policy.ts').write_text('export const enabled = true\n')
        (self.source / 'src/new.ts').write_text('export const fresh = true\n')
        self.output = self.release / 'out.patch'

    def run_git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.source), *args], text=True)

    def export(self):
        with patch.object(exporter, 'ROOT', self.release), patch.object(sys, 'argv', [
            'export_patch.py', '--source', str(self.source), '--output', str(self.output)
        ]), contextlib.redirect_stdout(io.StringIO()):
            exporter.main()

    def test_exports_only_allowlist_and_applies(self):
        (self.source / 'private.txt').write_text('do not export')
        self.export()
        content = self.output.read_text()
        self.assertIn('src/new.ts', content)
        self.assertNotIn('private.txt', content)
        self.assertNotIn(str(self.root), content)
        self.run_git('apply', '--reverse', '--check', str(self.output))

    def test_rejects_potential_key_without_output(self):
        (self.source / 'src/new.ts').write_text('const secret = "' + 'sk-' + 'x' * 32 + '"')
        with self.assertRaisesRegex(ValueError, 'private data'):
            self.export()
        self.assertFalse(self.output.exists())

    def test_rejects_mismatched_base(self):
        (self.release / 'upstream.json').write_text(json.dumps({'baseCommit': '0' * 40}))
        with self.assertRaisesRegex(ValueError, 'differs'):
            self.export()

    def test_rejects_traversal(self):
        (self.release / 'patch-files.json').write_text(json.dumps(['src/../../private.txt']))
        with self.assertRaisesRegex(ValueError, 'allowlist path'):
            self.export()

    def test_rejects_unreviewed_committed_allowlist_changes(self):
        self.run_git('add', 'src/policy.ts')
        self.run_git('commit', '-qm', 'unreviewed local change')
        with self.assertRaisesRegex(ValueError, 'Committed allowlist content differs'):
            self.export()

    def test_rejects_source_race(self):
        with patch.object(exporter, 'snapshot', side_effect=[{'src/policy.ts': 'a'}, {'src/policy.ts': 'b'}]):
            with self.assertRaisesRegex(RuntimeError, 'changed while exporting'):
                self.export()
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
