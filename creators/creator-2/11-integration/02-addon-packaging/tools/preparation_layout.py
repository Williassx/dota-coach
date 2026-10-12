"""Exact source recipe and deterministic Panorama preparation composition."""
import copy
import hashlib
import xml.etree.ElementTree as ET

BASE = 'creators/creator-2/'
BINDING = BASE + '11-integration/01-ui-binding/src/panorama/'
TARGET = 'content/panorama/'
LAYOUT = TARGET + 'layout/custom_game/coach_preparation.xml'
UI_MANIFEST = TARGET + 'layout/custom_game/custom_ui_manifest.xml'
MODULES = (
    ('01-team-picker', 'team_picker.xml', 'TeamPickerRoot', 'CoachPreparationTeamHost',
     'team_picker.css', ('team_picker_state.js', 'team_picker_panel.js')),
    ('02-hero-role-picker', 'hero_role_picker.xml', 'HeroRoleRoot', 'CoachPreparationHeroHost',
     'hero_role_picker.css', ('hero_role_state.js', 'hero_role_panel.js')),
    ('03-tactics-morale', 'preparation_picker.xml', 'PreparationRoot', 'CoachPreparationTacticsHost',
     'preparation_picker.css', ('preparation_state.js', 'preparation_panel.js')),
)
SCRIPTS = ('preparation_panel_port.js', 'team_picker_state.js', 'team_picker_panel.js',
           'hero_role_state.js', 'hero_role_panel.js', 'preparation_state.js',
           'preparation_panel.js', 'preparation_flow_state.js', 'preparation_binding.js')
STYLES = ('team_picker.css', 'hero_role_picker.css', 'preparation_picker.css', 'coach_preparation.css')
INPUTS = [{'source': BASE + '04-preparation-ui/' + module + '/src/panorama/layout/custom_game/' + layout,
           'root_id': root_id, 'host_id': host} for module, layout, root_id, host, _, _ in MODULES]
ASSETS = {BINDING + 'layout/custom_game/' + name: TARGET + 'layout/custom_game/' + name
          for name in ('custom_ui_manifest.xml', 'coach_preparation.xml')}
ASSETS[BINDING + 'styles/custom_game/coach_preparation.css'] = TARGET + 'styles/custom_game/coach_preparation.css'
for module, _, _, _, style, scripts in MODULES:
    prefix = BASE + '04-preparation-ui/' + module + '/src/panorama/'
    ASSETS[prefix + 'styles/custom_game/' + style] = TARGET + 'styles/custom_game/' + style
    for name in scripts:
        ASSETS[prefix + 'scripts/custom_game/' + name] = TARGET + 'scripts/custom_game/' + name
for name in ('preparation_panel_port.js', 'preparation_flow_state.js', 'preparation_binding.js'):
    ASSETS[BINDING + 'scripts/custom_game/' + name] = TARGET + 'scripts/custom_game/' + name


def parse_xml(payload, allow_manifest=False):
    text = payload.decode('utf-8-sig')
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        raise ValueError('Preparation XML DTD/entities are unsupported')
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        raise ValueError('Preparation XML cannot be parsed') from error
    if root.tag != 'root':
        raise ValueError('Preparation XML requires one root')
    ids = set()
    for node in root.iter():
        allowed = {'root', 'styles', 'scripts', 'include', 'Panel', 'Label', 'Button'}
        if allow_manifest:
            allowed.add('CustomUIElement')
        if node.tag not in allowed or any(key.lower().startswith('on') for key in node.attrib):
            raise ValueError('Preparation XML must be inert')
        if 'src' in node.attrib and node.tag != 'include':
            raise ValueError('Preparation src references belong only to dependency includes')
        if not allow_manifest and 'layoutfile' in node.attrib:
            raise ValueError('Preparation layout must not create another layout context')
        identity = node.get('id')
        if identity is not None:
            if not identity or identity in ids:
                raise ValueError('Preparation IDs must be nonempty and unique')
            ids.add(identity)
        if node.tag == 'Label' and node.get('html') != 'false':
            raise ValueError('Preparation labels must use plain text')
        if node.tag == 'Button' and node.get('enabled') != 'false':
            raise ValueError('Preparation buttons must start disabled')
    return root


def dependencies(root, scripts, styles):
    if (root.attrib or len(list(root.iter('root'))) != 1 or
            len(list(root.iter('scripts'))) != 1 or len(list(root.iter('styles'))) != 1 or
            len(list(root.iter('include'))) != len(scripts) + len(styles)):
        raise ValueError('Preparation dependency sections must occur only at the top level')
    if [n.tag for n in root] != ['styles', 'scripts', 'Panel']:
        raise ValueError('Preparation layout needs exact styles/scripts/Panel sections')
    for section, names in [('scripts', scripts), ('styles', styles)]:
        nodes = list(root.find(section))
        expected = ['file://{resources}/' + section + '/custom_game/' + name for name in names]
        if (any(n.tag != 'include' or set(n.attrib) != {'src'} or len(n) for n in nodes) or
                [n.get('src') for n in nodes] != expected):
            raise ValueError('Preparation dependencies must preserve exact order')
        if root.find(section).attrib:
            raise ValueError('Preparation dependency sections must not have attributes')


def validate_graph(payloads, root, manifest):
    elements = list(manifest.iter('CustomUIElement'))
    if ([n.tag for n in manifest.iter()] != ['root', 'Panel', 'CustomUIElement'] or
            manifest.attrib or manifest[0].attrib or
            len(elements) != 1 or set(elements[0].attrib) != {'type', 'layoutfile'} or
            len(list(manifest)) != 1 or manifest[0].tag != 'Panel' or len(manifest[0]) != 1 or
            len(elements) != 1 or elements[0].get('type') != 'Hud' or
            elements[0].get('layoutfile') != 'file://{resources}/layout/custom_game/coach_preparation.xml'):
        raise ValueError('Preparation manifest must load only the preparation HUD')
    edges = {}
    for name, tree in [(UI_MANIFEST, manifest), (LAYOUT, root)]:
        edges[name] = set()
        for node in tree.iter():
            for key, value in node.attrib.items():
                if key not in ('src', 'layoutfile'):
                    continue
                prefix = 'file://{resources}/'
                if not value.startswith(prefix) or TARGET + value[len(prefix):] not in payloads:
                    raise ValueError('Preparation references require declared local resources')
                edges[name].add(TARGET + value[len(prefix):])
    reached, pending = set(), [UI_MANIFEST]
    while pending:
        name = pending.pop()
        if name not in reached:
            reached.add(name); pending.extend(edges.get(name, ()))
    if reached != set(payloads):
        raise ValueError('Preparation graph has unreachable resources')


def prepare(repository, manifest, read_source):
    """Return the same prepared tuples consumed by the existing build/verifier."""
    if (not isinstance(manifest, dict) or set(manifest) != {'schema_version', 'kind', 'assets', 'layout_inputs'} or
            type(manifest['schema_version']) is not int or manifest['schema_version'] != 1 or
            manifest['kind'] != 'panorama_source_preparation'):
        raise ValueError('Unsupported preparation recipe')
    entries = manifest['assets']
    if not isinstance(entries, list) or len(entries) != len(ASSETS):
        raise ValueError('Preparation requires exactly 15 resources')
    mapping = {}
    for entry in entries:
        if (not isinstance(entry, dict) or set(entry) != {'source', 'target'} or
                not isinstance(entry['source'], str) or not isinstance(entry['target'], str) or
                entry['source'] in mapping):
            raise ValueError('Preparation resource mapping must be exact and unique')
        mapping[entry['source']] = entry['target']
    if mapping != ASSETS or manifest['layout_inputs'] != INPUTS:
        raise ValueError('Preparation requires fixed resource mappings and three fixed layout inputs')
    prepared = [(e['source'], e['target'], read_source(repository, e['source'])) for e in entries]
    payloads = {target: payload for _, target, payload in prepared}
    root = parse_xml(payloads[LAYOUT]); dependencies(root, SCRIPTS, STYLES)
    outer = root.find('Panel')
    if (outer.attrib != {'class': 'CoachPreparationCanvas', 'hittest': 'false', 'hittestchildren': 'true'} or
            len(outer) != 1 or outer[0].tag != 'Panel'):
        raise ValueError('Preparation requires an exact anonymous outer panel')
    group = outer[0]
    if group.get('id') != 'CoachPreparationRoot':
        raise ValueError('Preparation shell root is missing')
    statuses = [n for n in group.iter('Label') if n.get('id') == 'CoachPreparationStatus']
    if len(statuses) != 1:
        raise ValueError('Preparation shell status is missing')
    for entry, module in zip(INPUTS, MODULES):
        raw = read_source(repository, entry['source'])
        source_root = parse_xml(raw); dependencies(source_root, module[5], (module[4],))
        panel = source_root.find('Panel')
        if panel.get('id') != entry['root_id']:
            raise ValueError('Preparation input root does not match its scope')
        hosts = [n for n in group.iter('Panel') if n.get('id') == entry['host_id']]
        if len(hosts) != 1 or len(hosts[0]) or (hosts[0].text or '').strip():
            raise ValueError('Preparation composition requires an empty declared host')
        hosts[0].append(copy.deepcopy(panel))
        root.insert(0, ET.Comment(' source=' + entry['source'] + ' sha256=' + hashlib.sha256(raw).hexdigest() + ' '))
    generated = ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'
    if len(generated) > 1024 * 1024:
        raise ValueError('Generated preparation resource exceeds 1 MiB')
    # Reparse without comments, checking cross-module IDs and the full local graph.
    checked = parse_xml(generated); dependencies(checked, SCRIPTS, STYLES)
    payloads[LAYOUT] = generated
    validate_graph(payloads, checked, parse_xml(payloads[UI_MANIFEST], allow_manifest=True))
    return [(source, target, generated if target == LAYOUT else payload) for source, target, payload in prepared]
