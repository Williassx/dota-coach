import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parents[3]
TOOL = BASE / 'tools/run_source_checks.py'
CATALOG = 'creators/creator-2/11-integration/03-end-to-end/suite-catalog.json'
PYTHON = 'creators/creator-2/11-integration/03-end-to-end/tests'
NODE = 'creators/creator-2/01-foundation/02-panorama-capability/tests/example.test.cjs'
SPEC = importlib.util.spec_from_file_location('source_checks', TOOL)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class SourceChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.entries = [{'id': 'python-fixture', 'framework': 'python-unittest', 'path': PYTHON},
                        {'id': 'node-fixture', 'framework': 'node-test', 'path': NODE}]
        self.write(PYTHON + '/test_example.py',
                   'import unittest\nclass Example(unittest.TestCase):\n def test_ok(self): self.assertEqual(2+2,4)\n')
        self.write(NODE, "const {test}=require('node:test');test('ok',()=>{});\n")
        self.catalog()

    def write(self, relative, value):
        target = self.root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding='utf-8')

    def catalog(self, entries=None, **extra):
        self.write(CATALOG, json.dumps({'schema_version': 1, 'suites': self.entries if entries is None else entries, **extra}))

    def no_output(self):
        self.assertFalse((self.root / 'build').exists())

    def test_catalog_matches_existing_matrix_and_owns_its_tests(self):
        entries, digest = runner.load_catalog(REPO)
        self.assertEqual(len(entries), 35)
        self.assertEqual(len(digest), 64)
        self.assertIn({'id': 'python-c2-11-03', 'framework': 'python-unittest', 'path': PYTHON}, entries)
        actual_node = {p.relative_to(REPO).as_posix() for p in (REPO / 'creators').rglob('*.test.cjs')}
        self.assertEqual({e['path'] for e in entries if e['framework'] == 'node-test'}, actual_node)
        actual_python = {p.parent.relative_to(REPO).as_posix() for p in (REPO / 'creators').rglob('test_*.py')}
        self.assertEqual({e['path'] for e in entries if e['framework'] == 'python-unittest'}, actual_python)

    def test_catalog_rejects_schema_duplicates_and_extra_commands(self):
        cases = [[], self.entries * 2,
                 [{**self.entries[0], 'argv': ['echo', 'bad']}],
                 [{**self.entries[0], 'framework': 'shell'}],
                 [{**self.entries[0], 'id': '../bad'}],
                 [{**self.entries[1], 'id': self.entries[0]['id']}, self.entries[0]],
                 [{**self.entries[0], 'id': 'other'}, self.entries[0]]]
        for entries in cases:
            with self.subTest(entries=entries):
                self.catalog(entries)
                with self.assertRaises(ValueError): runner.run_checks(self.root)
                self.no_output()
        for payload in ({'schema_version': True, 'suites': self.entries},
                        {'schema_version': 1, 'suites': self.entries, 'extra': 0}, []):
            self.write(CATALOG, json.dumps(payload))
            with self.assertRaises(ValueError): runner.load_catalog(self.root)

    def test_catalog_size_and_json_are_bounded(self):
        for raw in ('{', ' ' * (128 * 1024 + 1)):
            self.write(CATALOG, raw)
            with self.assertRaises(ValueError): runner.run_checks(self.root)
            self.no_output()

    def test_test_paths_are_portable_existing_and_scoped(self):
        for path in ('../outside', '/tmp/test.py', PYTHON.replace('/', '\\'),
                     'creators/creator-2/11-integration/03-end-to-end/tests/../tools',
                     'creators/creator-2/NUL/tests', 'creators/creator-2/missing/tests',
                     'README.md', NODE):
            with self.subTest(path=path):
                self.catalog([{**self.entries[0], 'path': path}])
                with self.assertRaises((ValueError, OSError)): runner.run_checks(self.root)
                self.no_output()
        self.catalog([{**self.entries[1], 'path': PYTHON}])
        with self.assertRaises(ValueError): runner.load_catalog(self.root)

    def test_linked_catalog_test_file_and_nested_directory_are_rejected(self):
        catalogue = self.root / CATALOG
        raw = catalogue.read_bytes()
        actual = self.root / 'actual.json'
        actual.write_bytes(raw)
        catalogue.unlink()
        catalogue.symlink_to(actual)
        with self.assertRaises(ValueError): runner.load_catalog(self.root)
        catalogue.unlink()
        catalogue.write_bytes(raw)
        test = self.root / PYTHON / 'test_example.py'
        outside = self.root / 'outside.py'
        outside.write_bytes(test.read_bytes())
        test.unlink()
        test.symlink_to(outside)
        with self.assertRaises(ValueError): runner.load_catalog(self.root)
        test.unlink()
        test.write_bytes(outside.read_bytes())
        (test.parent / 'nested').symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError): runner.load_catalog(self.root)
        self.no_output()

    def test_strict_node_summary_rejects_skip_cancel_todo_empty_and_exit(self):
        good = '# tests 2\n# pass 2\n# fail 0\n# cancelled 0\n# skipped 0\n# todo 0\n'
        self.assertEqual(runner.summarize('node-test', good, 0)['passed'], 2)
        self.assertTrue(runner.summarize('node-test', good, 0)['verified'])
        bad = ['', good + good, good.replace('# tests 2', '# tests 3'), good.replace('2', '0')]
        bad.extend(good.replace('# ' + field + ' 0', '# ' + field + ' 1')
                   for field in ('fail', 'cancelled', 'skipped', 'todo'))
        for output in bad:
            self.assertFalse(runner.summarize('node-test', output, 0)['verified'])
        self.assertFalse(runner.summarize('node-test', good, 1)['verified'])

    def test_strict_python_summary_rejects_skips_empty_failures_and_exit(self):
        good = 'test_ok ... ok\n\nRan 1 test in 0.001s\n\nOK\n'
        self.assertTrue(runner.summarize('python-unittest', good, 0)['verified'])
        for output in ('', good + good, good.replace('1 test', '0 tests'),
                       good.replace('OK', 'OK (skipped=1)'), good.replace('OK', 'FAILED (failures=1)')):
            self.assertFalse(runner.summarize('python-unittest', output, 0)['verified'])
        self.assertFalse(runner.summarize('python-unittest', good, 1)['verified'])

    def test_summaries_accept_windows_line_endings(self):
        python = 'Ran 1 test in 0.001s\r\n\r\nOK\r\n'
        node = '# tests 1\r\n# pass 1\r\n# fail 0\r\n# cancelled 0\r\n# skipped 0\r\n# todo 0\r\n'
        self.assertTrue(runner.summarize('python-unittest', python, 0)['verified'])
        self.assertTrue(runner.summarize('node-test', node, 0)['verified'])

    def test_parameters_selection_and_missing_tools_fail_before_writes(self):
        for kwargs in ({'jobs': 0}, {'jobs': 8}, {'jobs': True}, {'timeout': 0},
                       {'timeout': float('nan')}, {'timeout': 601}, {'timeout': True},
                       {'suites': ['unknown']}, {'suites': []}, {'suites': ['python-fixture'] * 2}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError): runner.run_checks(self.root, **kwargs)
                self.no_output()
        with patch.object(runner.shutil, 'which', return_value=None):
            with self.assertRaises(ValueError): runner.run_checks(self.root)
        self.no_output()

    def test_real_full_fixture_writes_logs_short_report_and_no_native_claim(self):
        result = runner.run_checks(self.root, jobs=2)
        self.assertTrue(result['verified'])
        self.assertEqual((result['suites'], result['passed_tests'], result['selection']), (2, 2, 'full'))
        report = json.loads((self.root / result['report']).read_text())
        self.assertEqual(len(report['results']), 2)
        self.assertEqual(report['stage'], 'source_only')
        self.assertFalse(report['source2_compiled'])
        self.assertFalse(report['runtime_verified'])
        for row in report['results']:
            self.assertTrue((self.root / row['log']).is_file())
            self.assertGreater(row['log_bytes'], 0)
            self.assertNotIn('stdout', row)
        self.assertEqual(report['results'][0]['argv'][0], sys.executable)
        self.assertIn('--test-reporter=tap', report['results'][1]['argv'])

    def test_partial_selection_does_not_need_node_and_is_reported(self):
        with patch.object(runner.shutil, 'which', return_value=None):
            result = runner.run_checks(self.root, suites=['python-fixture'])
        self.assertEqual((result['suites'], result['passed_tests'], result['selection']), (1, 1, 'partial'))
        self.assertTrue(result['verified'])

    def test_existing_external_and_linked_output_is_preserved(self):
        output = self.root / 'build/dota_coach/existing'
        output.mkdir(parents=True)
        (output / 'keep').write_text('keep')
        with self.assertRaises(FileExistsError): runner.run_checks(self.root, output=output)
        self.assertEqual((output / 'keep').read_text(), 'keep')
        with self.assertRaises(ValueError): runner.run_checks(self.root, output=self.root / 'external')
        linked = output.with_name('linked')
        linked.symlink_to(output, target_is_directory=True)
        with self.assertRaises((ValueError, FileExistsError)): runner.run_checks(self.root, output=linked)
        self.assertEqual(list(output.iterdir()), [output / 'keep'])

    def test_failure_and_zero_tests_create_failed_reports(self):
        for source in ('import unittest\nclass Fail(unittest.TestCase):\n def test_fail(self): self.fail("expected")\n',
                       '# no tests\n',
                       'import unittest\nclass Skip(unittest.TestCase):\n @unittest.skip("expected")\n def test_skip(self): pass\n'):
            self.write(PYTHON + '/test_example.py', source)
            result = runner.run_checks(self.root, suites=['python-fixture'])
            self.assertFalse(result['verified'])
            self.assertEqual(result['failed_suites'], ['python-fixture'])
            self.assertTrue((self.root / result['report']).exists())

    def test_timeout_is_a_failed_suite_with_a_log(self):
        self.write(PYTHON + '/test_example.py', 'import time\ntime.sleep(10)\n')
        result = runner.run_checks(self.root, suites=['python-fixture'], timeout=0.1)
        report = json.loads((self.root / result['report']).read_text())
        self.assertFalse(result['verified'])
        self.assertEqual(report['results'][0]['reason'], 'timeout')
        self.assertIsNone(report['results'][0]['exit_code'])

    def test_timeout_stops_owned_child_processes(self):
        self.write(PYTHON + '/test_example.py',
                   'import subprocess,sys,time\nsubprocess.Popen([sys.executable,"-c",'
                   '"import time;from pathlib import Path;time.sleep(0.6);Path(\'late-child\').write_text(\'late\')"])\n'
                   'time.sleep(10)\n')
        result = runner.run_checks(self.root, suites=['python-fixture'], timeout=0.2)
        self.assertFalse(result['verified'])
        time.sleep(0.7)
        self.assertFalse((self.root / 'late-child').exists())

    def test_cli_list_full_partial_and_failure_exit_codes(self):
        command = [sys.executable, str(TOOL), '--repository', str(self.root)]
        listed = subprocess.run(command + ['--list'], capture_output=True, text=True)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(len(json.loads(listed.stdout)['suites']), 2)
        self.no_output()
        for extra, selection in (([], 'full'), (['--suite', 'python-fixture'], 'partial')):
            result = subprocess.run(command + extra, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(result.stdout)
            self.assertEqual(summary['selection'], selection)
            self.assertLess(len(result.stdout), 700)
        self.write(PYTHON + '/test_example.py', '# no tests\n')
        failed = subprocess.run(command + ['--suite', 'python-fixture'], capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1)
        self.assertFalse(json.loads(failed.stdout)['verified'])
        invalid = subprocess.run(command + ['--suite', 'unknown'], capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, '')


if __name__ == '__main__':
    unittest.main()
