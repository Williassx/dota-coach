"""Build an isolated camera acceptance fixture; no compilation or native launch."""
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
PACKAGE = 'creators/creator-2/11-integration/02-addon-packaging/'
FIXTURE = 'creators/creator-2/03-map-view/02-camera-overlays/tests/01-native-camera/'
RESOURCE = 'content/panorama/'
MANIFEST = RESOURCE + 'layout/custom_game/custom_ui_manifest.xml'
LAYOUT = RESOURCE + 'layout/custom_game/coach_hud.xml'
DERIVED = RESOURCE + 'layout/custom_game/camera_fixture.xml'
DRIVER = RESOURCE + 'scripts/custom_game/camera_fixture.js'

spec = importlib.util.spec_from_file_location('native_camera_fixed_policy', REPOSITORY /
    'creators/creator-2/01-foundation/02-panorama-capability/tools/build_probe_bundle.py')
policy = importlib.util.module_from_spec(spec)
previous_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    spec.loader.exec_module(policy)
finally:
    sys.dont_write_bytecode = previous_bytecode


def build_fixture(repository: Path, output: Path) -> dict:
    root = repository.resolve()
    destination = policy.output_path(root, output)
    recipe = json.loads(policy.read_source(root, PACKAGE + 'bundle-manifest.json'))
    if recipe.get('kind') != 'panorama_source_hud':
        raise ValueError('Native camera fixture requires the unchanged fixed HUD recipe')
    canonical = policy.prepare_assets(root, recipe)
    native_manifest = policy.read_source(root, FIXTURE + 'custom_ui_manifest.xml')
    driver = policy.read_source(root, FIXTURE + 'camera_fixture.js')
    if b'<!DOCTYPE' in native_manifest.upper() or b'<!ENTITY' in native_manifest.upper():
        raise ValueError('Native camera manifest cannot declare DTD/entities')
    tree = ET.fromstring(native_manifest)
    nodes = list(tree.iter())
    if ([node.tag for node in nodes] != ['root', 'Panel', 'CustomUIElement'] or
            nodes[0].attrib or nodes[1].attrib or
            any((node.text or '').strip() or (node.tail or '').strip() for node in nodes) or
            tree.find('./Panel/CustomUIElement') is None or
            nodes[2].attrib != {'type': 'Hud',
                'layoutfile': 'file://{resources}/layout/custom_game/camera_fixture.xml'}):
        raise ValueError('Native camera fixture requires its exact test Hud manifest')
    canonical_layout = next((source, raw) for source, target, raw in canonical if target == LAYOUT)
    layout = ET.fromstring(canonical_layout[1])
    ET.SubElement(layout.find('./scripts'), 'include',
                  {'src': 'file://{resources}/scripts/custom_game/camera_fixture.js'})
    ET.SubElement(layout.find('./Panel'), 'Label', {
        'id': 'NativeCameraFixtureStatus', 'html': 'false', 'hittest': 'false',
        'text': 'TEST ONLY: native camera API fixture; no server/input authority',
        'style': 'horizontal-align: left; vertical-align: bottom; margin-left: 24px; margin-bottom: 44px; width: 740px; padding: 8px; color: #ffffff; background-color: #18212bf0; font-size: 20px; white-space: normal;'})
    derived = ET.tostring(layout, encoding='utf-8', xml_declaration=True) + b'\n'
    prepared = [(source, target, raw, False) for source, target, raw in canonical if target != MANIFEST]
    prepared += [(FIXTURE + 'custom_ui_manifest.xml', MANIFEST, native_manifest, False),
                 (FIXTURE + 'camera_fixture.js', DRIVER, driver, False),
                 (canonical_layout[0], DERIVED, derived, True)]
    if len(prepared) != 15 or len({target.casefold() for _, target, _, _ in prepared}) != 15:
        raise ValueError('Native camera fixture requires exactly15 unique outputs')
    # All source reads and structural checks finish before creating output parents.
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
    report = {'schema_version': 1, 'fixture_type': 'native_camera_test_only',
              'canonical_inputs': len(canonical), 'assets': assets,
              'canonical_input_hashes': [{'source': source, 'target': target,
                 'sha256': hashlib.sha256(raw).hexdigest()} for source, target, raw in canonical],
              'source2_compiled': False, 'runtime_verified': False,
              'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (destination / 'native-fixture-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=REPOSITORY)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = args.output or args.repository / 'build/dota_coach' / (
        'native-camera-' + stamp + '-' + secrets.token_hex(3))
    try:
        report = build_fixture(args.repository, output)
    except (OSError, ValueError, ET.ParseError) as error:
        print('Native camera fixture build refused: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps({'fixture_type': report['fixture_type'], 'assets': len(report['assets']),
                      'output': str(output), 'source2_compiled': False, 'runtime_verified': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
