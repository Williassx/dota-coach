"""Build an isolated acceptance fixture; never extend a fixed source kind."""
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
FIXTURE = 'creators/creator-2/11-integration/01-ui-binding/tests/native-preparation/'
RESOURCE = 'content/panorama/'
MANIFEST = RESOURCE + 'layout/custom_game/custom_ui_manifest.xml'
LAYOUT = RESOURCE + 'layout/custom_game/coach_preparation.xml'
DERIVED = RESOURCE + 'layout/custom_game/preparation_fixture.xml'
DRIVER = RESOURCE + 'scripts/custom_game/preparation_fixture.js'
RESET_DRIVER = 'creators/creator-2/09-presentation/02-settings-layout/tests/reset_fixture.js'

spec = importlib.util.spec_from_file_location('native_preparation_fixture_fixed_policy',
    REPOSITORY / 'creators/creator-2/01-foundation/02-panorama-capability/tools/build_probe_bundle.py')
policy = importlib.util.module_from_spec(spec)
previous_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
try:
    spec.loader.exec_module(policy)
finally:
    sys.dont_write_bytecode = previous_bytecode


def build_fixture(repository: Path, output: Path, variant: str = 'baseline') -> dict:
    if type(variant) is not str or variant not in ('baseline', 'reset'):
        raise ValueError('Native preparation variant must be exactly baseline or reset')
    root = repository.resolve()
    destination = policy.output_path(root, output)
    recipe = json.loads(policy.read_source(root, PACKAGE + 'preparation-manifest.json'))
    if recipe.get('kind') != 'panorama_source_preparation':
        raise ValueError('Native fixture requires the unchanged fixed preparation recipe')
    canonical = policy.prepare_assets(root, recipe)
    native_manifest = policy.read_source(root, FIXTURE + 'custom_ui_manifest.xml')
    driver_source = RESET_DRIVER if variant == 'reset' else FIXTURE + 'preparation_fixture.js'
    driver = policy.read_source(root, driver_source)
    if b'<!DOCTYPE' in native_manifest.upper() or b'<!ENTITY' in native_manifest.upper():
        raise ValueError('Native fixture manifest cannot declare DTD/entities')
    tree = ET.fromstring(native_manifest)
    nodes = list(tree.iter())
    if ([node.tag for node in nodes] != ['root', 'Panel', 'CustomUIElement'] or
            nodes[0].attrib or nodes[1].attrib or
            any((node.text or '').strip() or (node.tail or '').strip() for node in nodes) or
            tree.find('./Panel/CustomUIElement') is None or
            nodes[2].attrib != {'type': 'Hud',
                'layoutfile': 'file://{resources}/layout/custom_game/preparation_fixture.xml'}):
        raise ValueError('Native fixture requires its exact test Hud manifest')
    layout = ET.fromstring(next(raw for _, target, raw in canonical if target == LAYOUT))
    ET.SubElement(layout.find('./scripts'), 'include',
                  {'src': 'file://{resources}/scripts/custom_game/preparation_fixture.js'})
    ET.SubElement(layout.find('./Panel'), 'Label', {'id': 'NativePreparationFixtureStatus', 'html': 'false',
        'hittest': 'false', 'text': 'TEST ONLY: synthetic draft; no C1/server/input',
        'style': 'horizontal-align: right; vertical-align: top; margin-right: 24px; margin-top: 4px; width: 620px; padding: 4px; color: #ffffff; background-color: #18212bf0; font-size: 18px; white-space: normal;'})
    derived = ET.tostring(layout, encoding='utf-8', xml_declaration=True) + b'\n'
    prepared = [(source, target, raw, target == LAYOUT) for source, target, raw in canonical if target != MANIFEST]
    prepared += [(FIXTURE + 'custom_ui_manifest.xml', MANIFEST, native_manifest, False),
                 (driver_source, DRIVER, driver, False),
                 (next(source for source, target, _ in canonical if target == LAYOUT), DERIVED, derived, True)]
    if len(prepared) != 17 or len({target.casefold() for _, target, _, _ in prepared}) != 17:
        raise ValueError('Native test fixture requires exactly17 unique outputs')
    source_paths = [a['source'] for a in recipe['assets']] + [a['source'] for a in recipe['layout_inputs']]
    source_inputs = [{'source': source, 'sha256': hashlib.sha256(policy.read_source(root, source)).hexdigest()}
                     for source in source_paths]
    input_paths = {a['source'] for a in recipe['layout_inputs']}
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
    report = {'schema_version': 1, 'fixture_type': 'native_preparation_test_only',
              'diagnostic_variant': variant,
              'canonical_outputs': len(canonical), 'assets': assets,
              'canonical_output_hashes': [{'source': source, 'target': target,
                 'sha256': hashlib.sha256(raw).hexdigest()} for source, target, raw in canonical],
              'source_input_hashes': source_inputs,
              'layout_input_hashes': [a for a in source_inputs if a['source'] in input_paths],
              'source2_compiled': False, 'runtime_verified': False,
              'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (destination / 'native-fixture-report.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=REPOSITORY)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--variant', choices=('baseline', 'reset'), default='baseline')
    args = parser.parse_args()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = args.output or args.repository / 'build/dota_coach' / (
        'native-preparation-' + stamp + '-' + secrets.token_hex(3))
    try:
        report = build_fixture(args.repository, output, variant=args.variant)
    except (OSError, ValueError, ET.ParseError) as error:
        print('Native test fixture build refused: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps({'fixture_type': report['fixture_type'], 'assets': len(report['assets']),
                      'output': str(output), 'source2_compiled': False, 'runtime_verified': False}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
