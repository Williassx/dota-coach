"""Fixed seven-resource composition using the canonical standalone mouse policy."""
import hashlib
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET

spec = importlib.util.spec_from_file_location('targeting_mouse_policy', Path(__file__).with_name('mouse_proposal_layout.py'))
mouse = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mouse)
policy = mouse.policy
TARGET = mouse.TARGET
LAYOUT = mouse.LAYOUT
EXTRA = {
    'creators/creator-2/03-map-view/03-visibility-targets/src/panorama/scripts/custom_game/targets_state.js': TARGET + 'scripts/custom_game/targets_state.js',
    'creators/creator-2/11-integration/01-ui-binding/src/panorama/scripts/custom_game/mouse_targeting_binding.js': TARGET + 'scripts/custom_game/mouse_targeting_binding.js'}
ASSETS = {**mouse.ASSETS, **EXTRA}
SCRIPTS = ('targets_state.js', 'mouse_proposal_state.js', 'mouse_proposal_panel.js', 'mouse_targeting_binding.js')


def prepare(repository, recipe, read_source):
    if (not isinstance(recipe, dict) or set(recipe) != {'schema_version', 'kind', 'assets'} or
            type(recipe['schema_version']) is not int or recipe['schema_version'] != 1 or
            recipe['kind'] != 'panorama_source_mouse_targeting'):
        raise ValueError('Unsupported mouse targeting recipe')
    entries = recipe['assets']
    if not isinstance(entries, list) or len(entries) != 7:
        raise ValueError('Exactly seven mouse targeting resources required')
    mapping = {}
    for item in entries:
        if (not isinstance(item, dict) or set(item) != {'source', 'target'} or
                not isinstance(item['source'], str) or not isinstance(item['target'], str) or item['source'] in mapping):
            raise ValueError('Unique exact targeting mapping required')
        mapping[item['source']] = item['target']
    if mapping != ASSETS:
        raise ValueError('Fixed targeting mapping required')
    # Reuse every standalone input constraint without expanding its two-script kind.
    original = mouse.prepare(repository, {'schema_version': 1, 'kind': 'panorama_source_mouse_proposal',
        'assets': [item for item in entries if item['source'] in mouse.ASSETS]}, read_source)
    payloads = {target: raw for _, target, raw in original}
    for source, target in EXTRA.items():
        payloads[target] = read_source(repository, source)
    raw = payloads[LAYOUT]
    layout = mouse.validate_layout(raw)
    scope = ET.tostring(layout.find('Panel'))
    scripts = layout.find('scripts')
    scripts.insert(0, ET.Element('include', {'src': 'file://{resources}/scripts/custom_game/' + SCRIPTS[0]}))
    scripts.append(ET.Element('include', {'src': 'file://{resources}/scripts/custom_game/' + SCRIPTS[-1]}))
    source = next(source for source, target in mouse.ASSETS.items() if target == LAYOUT)
    layout.insert(0, ET.Comment(' source=' + source + ' sha256=' + hashlib.sha256(raw).hexdigest() + ' '))
    generated = ET.tostring(layout, encoding='utf-8', xml_declaration=True) + b'\n'
    if len(generated) > 1024 * 1024:
        raise ValueError('Generated targeting layout exceeds 1 MiB')
    checked = policy.parse(generated, extra_tags={'Panel': policy.ATTRS['Panel'] | {'visible'}})
    policy.dependencies(checked, SCRIPTS, ('mouse_proposal.css',))
    if ET.tostring(checked.find('Panel')) != scope or len(policy.ids(checked.find('Panel'))) != 7:
        raise ValueError('Canonical mouse scope must remain unchanged')
    reached = {mouse.MANIFEST, LAYOUT}
    for node in checked.findall('./scripts/include') + checked.findall('./styles/include'):
        reached.add(TARGET + node.get('src').removeprefix('file://{resources}/'))
    if reached != set(payloads):
        raise ValueError('Every targeting output must be reachable')
    payloads[LAYOUT] = generated
    return [(item['source'], item['target'], payloads[item['target']]) for item in entries]
