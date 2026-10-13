"""Build a separate TEST diagnostic transport fixture, never expand fixed probe policy."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import secrets
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

REPOSITORY = Path(__file__).resolve().parents[5]
BASE = 'creators/creator-2/01-foundation/02-panorama-capability/'
FIXTURE = BASE + 'tests/native-ping/'
C1 = 'creators/creator-1/01-foundation/03-command-contract/src/scripts/vscripts/'
MANIFEST = 'content/panorama/layout/custom_game/custom_ui_manifest.xml'
LAYOUT = 'content/panorama/layout/custom_game/coach_probe.xml'
DERIVED = 'content/panorama/layout/custom_game/ping_fixture.xml'
DRIVER = 'content/panorama/scripts/custom_game/ping_fixture.js'
spec = importlib.util.spec_from_file_location('native_ping_fixed_policy', Path(__file__).with_name('build_probe_bundle.py'))
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def build_fixture(repository: Path, output: Path, variant='flow') -> dict:
    if type(variant) is not str or variant not in ('flow', 'adapter'):
        raise ValueError('Unknown diagnostic fixture variant')
    root = repository.resolve()
    destination = policy.output_path(root, output)
    recipe = json.loads(policy.read_source(root, BASE + 'bundle-manifest.json'))
    if recipe.get('kind') != 'panorama_source_probe':
        raise ValueError('Native ping fixture requires unchanged fixed probe recipe')
    canonical = policy.prepare_assets(root, recipe)
    if len(canonical) != 5:
        raise ValueError('Native ping requires five canonical inputs')
    native_manifest = policy.read_source(root, FIXTURE + 'custom_ui_manifest.xml')
    driver_source = FIXTURE + ('ping_adapter_fixture.js' if variant == 'adapter' else 'ping_fixture.js')
    driver = policy.read_source(root, driver_source)
    if b'<!DOCTYPE' in native_manifest.upper() or b'<!ENTITY' in native_manifest.upper():
        raise ValueError('TEST manifest cannot declare DTD/entities')
    tree = ET.fromstring(native_manifest)
    nodes = list(tree.iter())
    if ([n.tag for n in nodes] != ['root', 'Panel', 'CustomUIElement'] or
            nodes[0].attrib or nodes[1].attrib or
            any((n.text or '').strip() or (n.tail or '').strip() for n in nodes) or
            nodes[2].attrib != {'type': 'Hud', 'layoutfile': 'file://{resources}/layout/custom_game/ping_fixture.xml'}):
        raise ValueError('Native ping requires exact TEST Hud manifest')
    layout = ET.fromstring(next(raw for _, target, raw in canonical if target == LAYOUT))
    scripts = layout.find('scripts')
    for node in list(scripts):
        if variant == 'flow' and node.attrib.get('src') == 'file://{resources}/scripts/custom_game/coach_probe.js':
            scripts.remove(node)
    ET.SubElement(scripts, 'include', {'src': 'file://{resources}/scripts/custom_game/ping_fixture.js'})
    ET.SubElement(layout.find('Panel'), 'Label', {'id': 'NativePingFixtureStatus', 'html': 'false',
        'hittest': 'false', 'text': 'TEST ONLY: diagnostic; no game orders or permission',
        'style': 'horizontal-align: right; vertical-align: top; width: 400px; margin: 30px; padding: 8px; color: #ffffff; background-color: #18212bf0; font-size: 20px; white-space: normal;'})
    derived = ET.tostring(layout, encoding='utf-8', xml_declaration=True) + b'\n'
    prepared = [(source, target, raw, False) for source, target, raw in canonical if target != MANIFEST]
    prepared += [(FIXTURE + 'custom_ui_manifest.xml', MANIFEST, native_manifest, False),
                 (driver_source, DRIVER, driver, False),
                 (next(source for source, target, _ in canonical if target == LAYOUT), DERIVED, derived, True),
                 (C1 + 'diagnostic_ping.lua', 'game/scripts/vscripts/diagnostic_ping.lua', policy.read_source(root, C1 + 'diagnostic_ping.lua'), False),
                 (C1 + 'ping_game_mode.lua', 'game/scripts/vscripts/addon_game_mode.lua', policy.read_source(root, C1 + 'ping_game_mode.lua'), False)]
    if len(prepared) != 9 or len({target.casefold() for _, target, _, _ in prepared}) != 9:
        raise ValueError('Native ping requires exactly nine unique outputs')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.mkdir()
    assets = []
    for source, target, raw, composed in prepared:
        path = destination.joinpath(*PurePosixPath(target).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(raw)
        assets.append({'source': source, 'target': target, 'derived': composed,
                       'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    report = {'schema_version': 1, 'fixture_type': 'native_diagnostic_ping_test_only',
              'canonical_inputs': 5, 'diagnostic_variant': variant, 'assets': assets,
              'canonical_input_hashes': [{'source': source, 'target': target, 'sha256': hashlib.sha256(raw).hexdigest()}
                                         for source, target, raw in canonical],
              'source2_compiled': False, 'runtime_verified': False,
              'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (destination / 'native-fixture-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=REPOSITORY)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--variant', choices=('flow','adapter'), default='flow')
    args = parser.parse_args()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = args.output or args.repository / 'build/dota_coach' / ('native-ping-' + stamp + '-' + secrets.token_hex(3))
    try:
        report = build_fixture(args.repository, output, variant=args.variant)
    except (OSError, ValueError, ET.ParseError) as error:
        print('Native ping fixture refused: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps({'output': str(output), 'assets': len(report['assets']), 'fixture_type': report['fixture_type']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
