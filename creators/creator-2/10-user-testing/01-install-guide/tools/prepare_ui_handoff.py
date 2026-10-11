"""Prepare and verify a source UI handoff. Never install or launch Dota/Workshop Tools."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

REPOSITORY = Path(__file__).resolve().parents[5]
FOUNDATION = 'creators/creator-2/01-foundation/02-panorama-capability/'
PACKAGING = 'creators/creator-2/11-integration/02-addon-packaging/'
SCREENS = {
    'probe': (FOUNDATION + 'bundle-manifest.json', 'panorama_source_probe'),
    'hud': (PACKAGING + 'bundle-manifest.json', 'panorama_source_hud'),
    'preparation': (PACKAGING + 'preparation-manifest.json', 'panorama_source_preparation'),
    'intervention': (PACKAGING + 'intervention-manifest.json', 'panorama_source_intervention'),
    'intervention-screen': (PACKAGING + 'intervention-screen-manifest.json', 'panorama_source_intervention_screen'),
    'voice-text': (PACKAGING + 'voice-text-manifest.json', 'panorama_source_voice_text'),
    'orders-timeline': (PACKAGING + 'orders-timeline-manifest.json', 'panorama_source_orders_timeline'),
    'opponent-roster': (PACKAGING + 'opponent-roster-manifest.json', 'panorama_source_opponent_roster'),
    'match-observation': (PACKAGING + 'match-observation-manifest.json', 'panorama_source_match_observation'),
}


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


TOOLS = REPOSITORY / FOUNDATION / 'tools'
builder = load('ui_handoff_builder', TOOLS / 'build_probe_bundle.py')
sys.path.insert(0, str(TOOLS))
try:
    verifier = load('ui_handoff_verifier', TOOLS / 'verify_probe_bundle.py')
finally:
    sys.path.pop(0)


def git_metadata(root):
    def query(*arguments):
        return subprocess.run(['git', '--no-optional-locks', '-C', str(root), *arguments],
                              check=True, capture_output=True, text=True, timeout=5).stdout.strip()
    try:
        if Path(query('rev-parse', '--show-toplevel')).resolve() != root:
            return {'head': None, 'dirty': None, 'status': 'not_repo_root'}
        return {'head': query('rev-parse', 'HEAD'),
                'dirty': bool(query('status', '--porcelain', '--untracked-files=normal')), 'status': 'recorded'}
    except (OSError, subprocess.SubprocessError):
        return {'head': None, 'dirty': None, 'status': 'unavailable'}


def prepare_handoff(repository, screen='probe', bundle=None):
    root = Path(repository).resolve()
    if not isinstance(screen, str) or screen not in SCREENS:
        raise ValueError('Unknown source screen')
    relative, expected_kind = SCREENS[screen]
    raw = builder.read_source(root, relative)
    if len(raw) > builder.MAX_MANIFEST_BYTES:
        raise ValueError('Manifest exceeds 256 KiB')
    recipe = json.loads(raw.decode('utf-8'))
    if not isinstance(recipe, dict) or recipe.get('kind') != expected_kind:
        raise ValueError('Recipe kind must match the selected screen')
    if bundle is None:
        built = subprocess.run([sys.executable, str(TOOLS / 'build_probe_bundle.py'), '--repository', str(root),
                                '--manifest', str(root / relative)], capture_output=True, text=True)
        if built.returncode:
            raise ValueError('Source build failed: ' + built.stderr.strip()[:400])
        bundle = Path(json.loads(built.stdout)['output'])
    else:
        bundle = Path(bundle)
    bundle = Path(os.path.abspath(bundle if bundle.is_absolute() else root / bundle))
    boundary = root / 'build/dota_coach'
    if not bundle.is_relative_to(boundary) or bundle == boundary:
        raise ValueError('Bundle must be inside build/dota_coach')
    builder.check_ancestors(root, bundle)
    report_file = bundle.with_name(bundle.name + '.handoff.json')
    builder.check_ancestors(root, report_file, allow_missing=True)
    if report_file.exists() or report_file.is_symlink():
        raise FileExistsError('Existing handoff report is preserved')
    report_relative = (bundle / 'bundle-report.json').relative_to(root).as_posix()
    before = builder.read_source(root, report_relative)
    verified = verifier.verify_bundle(root, recipe, bundle)
    after = builder.read_source(root, report_relative)
    if before != after:
        raise ValueError('Bundle report changed during verification')
    bundle_report = json.loads(after.decode('utf-8'))
    report = {
        'schema_version': 1, 'stage': 'source_only',
        'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'screen': screen, 'kind': expected_kind, 'recipe': relative,
        'bundle': bundle.relative_to(root).as_posix(),
        'bundle_report_sha256': hashlib.sha256(after).hexdigest(),
        'manifest_sha256': bundle_report['manifest_sha256'], 'assets': bundle_report['assets'],
        'source_verification': verified, 'platform': sys.platform, 'python': sys.version.split()[0],
        'git': git_metadata(root), 'installation_performed': False, 'native_destination': None,
        'native_checks': {name: 'not_run' for name in ('source2_compile', 'scene_start', 'layout_hittest',
                          'microphone_asr', 'server_commands', 'manual_ai_return', 'second_owner_review')},
        'guide': 'creators/creator-2/10-user-testing/01-install-guide/notes/install-guide.md',
    }
    # Report is deliberately outside the bundle: its integrity policy stays exact.
    with report_file.open('x', encoding='utf-8') as handle:
        handle.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return {'report': report_file.relative_to(root).as_posix(), 'bundle': report['bundle'],
            'source_verified': True, 'source2_compiled': False, 'runtime_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=REPOSITORY)
    parser.add_argument('--screen', choices=tuple(SCREENS), default='probe')
    parser.add_argument('--bundle', type=Path, help='Verify an existing bundle; create a new companion report')
    args = parser.parse_args()
    try:
        result = prepare_handoff(args.repository, args.screen, args.bundle)
    except (OSError, ValueError) as error:
        print('Source handoff not completed: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
