"""Run the canonical source-test catalog; never compile, install or launch Dota."""
import argparse
import concurrent.futures
import datetime
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import subprocess
import sys
import time

REPOSITORY = Path(__file__).resolve().parents[5]
CATALOG = 'creators/creator-2/11-integration/03-end-to-end/suite-catalog.json'
MAX_CATALOG_BYTES = 128 * 1024
SUMMARY_BYTES = 64 * 1024
IDENTITY = re.compile(r'[a-z][a-z0-9-]{0,63}')

# Reuse the existing portable-path, reparse and fresh-output policy.
spec = importlib.util.spec_from_file_location('source_checks_paths', REPOSITORY /
       'creators/creator-2/01-foundation/02-panorama-capability/tools/build_probe_bundle.py')
paths = importlib.util.module_from_spec(spec)
previous = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    spec.loader.exec_module(paths)
finally:
    sys.dont_write_bytecode = previous


def load_catalog(repository):
    root = Path(repository).resolve()
    raw = paths.read_source(root, CATALOG)
    if len(raw) > MAX_CATALOG_BYTES:
        raise ValueError('Suite catalog exceeds 128 KiB')
    data = json.loads(raw.decode('utf-8'))
    if (not isinstance(data, dict) or set(data) != {'schema_version', 'suites'} or
            type(data['schema_version']) is not int or data['schema_version'] != 1 or
            not isinstance(data['suites'], list) or not 1 <= len(data['suites']) <= 64):
        raise ValueError('Suite catalog schema is invalid')
    ids, sources = set(), set()
    for entry in data['suites']:
        if (not isinstance(entry, dict) or set(entry) != {'id', 'framework', 'path'} or
                not isinstance(entry['id'], str) or not IDENTITY.fullmatch(entry['id']) or
                not isinstance(entry['framework'], str) or
                entry['framework'] not in ('node-test', 'python-unittest')):
            raise ValueError('Suite entry is invalid')
        relative = paths.portable_path(entry['path'])
        parts = relative.parts
        if (len(parts) < 5 or parts[0] != 'creators' or parts[1] not in ('creator-1', 'creator-2') or
                parts[4] != 'tests' or entry['id'] in ids or entry['path'] in sources):
            raise ValueError('Suite scope or uniqueness is invalid')
        ids.add(entry['id'])
        sources.add(entry['path'])
        actual = root.joinpath(*parts)
        paths.check_ancestors(root, actual)
        if entry['framework'] == 'node-test':
            if len(parts) != 6 or not parts[-1].endswith('.test.cjs'):
                raise ValueError('Node suite must be a test file')
            paths.read_source(root, entry['path'])
        else:
            if len(parts) != 5 or not actual.is_dir():
                raise ValueError('Python suite must be a tests directory')
            test_count = 0
            # Discover recursively just as unittest does, rejecting linked children.
            for directory, children, files in os.walk(actual, followlinks=False):
                for name in children + files:
                    paths.check_ancestors(root, Path(directory) / name)
                for name in files:
                    if name.startswith('test_') and name.endswith('.py'):
                        paths.read_source(root, (Path(directory) / name).relative_to(root).as_posix())
                        test_count += 1
            if not test_count:
                raise ValueError('Python suite has no test files')
    return data['suites'], hashlib.sha256(raw).hexdigest()


def summarize(framework, text, exit_code):
    text = '\n'.join(text.splitlines())
    passed = 0
    valid = False
    if framework == 'node-test':
        totals = {}
        for field in ('tests', 'pass', 'fail', 'cancelled', 'skipped', 'todo'):
            found = re.findall(r'^# ' + field + r' (\d+)\s*$', text, re.M)
            if len(found) != 1:
                break
            totals[field] = int(found[0])
        if len(totals) == 6:
            passed = totals['pass']
            valid = (totals['tests'] == passed and passed > 0 and
                     all(totals[field] == 0 for field in ('fail', 'cancelled', 'skipped', 'todo')))
    elif framework == 'python-unittest':
        found = re.findall(r'^Ran (\d+) tests? in [^\r\n]+$', text, re.M)
        successes = re.findall(r'^OK\s*$', text, re.M)
        if len(found) == 1 and len(successes) == 1:
            passed = int(found[0])
            valid = passed > 0
    verified = exit_code == 0 and valid
    return {'passed': passed, 'verified': verified,
            'reason': None if verified else ('process_exit' if exit_code != 0 else 'invalid_summary')}


def run_suite(root, target, entry, node, timeout, taskkill=None):
    argv = ([node, '--test', '--test-reporter=tap', entry['path']] if entry['framework'] == 'node-test'
            else [sys.executable, '-m', 'unittest', 'discover', '-s', entry['path'], '-p', 'test_*.py', '-v'])
    log = target / (entry['id'] + '.log')
    started = time.monotonic()
    exit_code, reason = None, None
    with log.open('xb') as handle:
        try:
            options = ({'start_new_session': True} if os.name == 'posix' else
                       {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP})
            process = subprocess.Popen(argv, cwd=root, stdout=handle, stderr=subprocess.STDOUT, **options)
            try:
                exit_code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                reason = 'timeout'
                try:
                    if os.name == 'posix':
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                    else:
                        subprocess.run([taskkill, '/PID', str(process.pid), '/T', '/F'],
                                       stdout=handle, stderr=subprocess.STDOUT,
                                       timeout=5, check=True)
                except (OSError, subprocess.SubprocessError) as error:
                    reason = 'timeout_termination_failed'
                    handle.write(('owned process tree termination failed: ' + str(error) + '\n')
                                 .encode('utf-8', errors='replace'))
                    process.kill()
                process.wait(timeout=5)
        except OSError as error:
            reason = 'process_start'
            handle.write((str(error) + '\n').encode('utf-8', errors='replace'))
    size = log.stat().st_size
    with log.open('rb') as handle:
        handle.seek(max(0, size - SUMMARY_BYTES))
        text = handle.read(SUMMARY_BYTES).decode('utf-8', errors='replace')
    summary = summarize(entry['framework'], text, exit_code)
    if reason:
        summary.update(verified=False, reason=reason)
    return {'id': entry['id'], 'framework': entry['framework'], 'argv': argv,
            'exit_code': exit_code, **summary, 'duration_seconds': round(time.monotonic() - started, 3),
            'log': log.relative_to(root).as_posix(), 'log_bytes': size}


def run_checks(repository, suites=None, jobs=4, timeout=180, output=None):
    root = Path(repository).resolve()
    catalog, digest = load_catalog(root)
    if (type(jobs) is not int or not 1 <= jobs <= 7 or type(timeout) not in (int, float) or
            not math.isfinite(timeout) or not 0 < timeout <= 600):
        raise ValueError('Jobs must be 1..7 and timeout must be finite, positive and at most 600 seconds')
    if suites is not None:
        if (not isinstance(suites, list) or not suites or any(not isinstance(s, str) for s in suites) or
                len(set(suites)) != len(suites) or set(suites) - {e['id'] for e in catalog}):
            raise ValueError('Select unique existing suite IDs')
        selected = [entry for entry in catalog if entry['id'] in suites]
    else:
        selected = catalog
    node = shutil.which('node') if any(e['framework'] == 'node-test' for e in selected) else None
    if node is None and any(e['framework'] == 'node-test' for e in selected):
        raise ValueError('Node is required for selected suites')
    taskkill = shutil.which('taskkill') if os.name == 'nt' else None
    if os.name == 'nt' and taskkill is None:
        raise ValueError('Windows taskkill is required to bound owned child processes')
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    target = paths.output_path(root, Path(output) if output is not None else
                               root / 'build/dota_coach' / ('source-checks-' + stamp + '-' + secrets.token_hex(3)))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(lambda entry: run_suite(root, target, entry, node, timeout, taskkill), selected))
    failed = [row['id'] for row in results if not row['verified']]
    report_file = target / 'source-checks.json'
    summary = {'verified': not failed, 'selection': 'full' if len(selected) == len(catalog) else 'partial',
               'suites': len(results), 'passed_tests': sum(row['passed'] for row in results),
               'failed_suites': failed, 'report': report_file.relative_to(root).as_posix(),
               'source2_compiled': False, 'runtime_verified': False}
    report = {**summary, 'schema_version': 1, 'stage': 'source_only', 'catalog': CATALOG,
              'catalog_sha256': digest, 'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'platform': sys.platform, 'python': sys.version.split()[0], 'jobs': jobs,
              'timeout_seconds': timeout, 'results': results}
    with report_file.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=REPOSITORY)
    parser.add_argument('--suite', action='append', help='Select an ID; repeat for multiple suites')
    parser.add_argument('--list', action='store_true', help='Validate and list the catalog without running tests')
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--timeout', type=float, default=180)
    parser.add_argument('--output', type=Path, help='Fresh child of build/dota_coach; existing results are preserved')
    args = parser.parse_args()
    try:
        if args.list:
            if args.suite:
                raise ValueError('--list cannot be combined with --suite')
            entries, digest = load_catalog(args.repository)
            print(json.dumps({'suites': entries, 'catalog_sha256': digest}, ensure_ascii=False))
            return 0
        result = run_checks(args.repository, args.suite, args.jobs, args.timeout, args.output)
    except (OSError, ValueError) as error:
        print('Source checks not started: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['verified'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
