"""Fixed source composition: canonical public opponents and presentation history."""
import copy
import hashlib
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET

BASE = 'creators/creator-2/'
BINDING = BASE + '11-integration/01-ui-binding/src/panorama/'
OPPONENT = BASE + '07-match-screen/02-opponent-cards/src/panorama/'
HISTORY = BASE + '07-match-screen/03-orders-timeline/src/panorama/'
TARGET = 'content/panorama/'
MANIFEST = TARGET + 'layout/custom_game/custom_ui_manifest.xml'
LAYOUT = TARGET + 'layout/custom_game/coach_match_observation.xml'
SCRIPTS = ('opponent_roster_state.js', 'opponent_roster_panel.js', 'orders_timeline_state.js',
           'orders_timeline_panel.js', 'match_observation_binding.js')
STYLES = ('opponent_roster.css', 'orders_timeline.css', 'coach_match_observation.css')
INPUTS = [
    {'source': OPPONENT + 'layout/custom_game/opponent_roster.xml', 'root_id': 'OpponentRosterRoot', 'host_id': 'MatchOpponentHost'},
    {'source': HISTORY + 'layout/custom_game/orders_timeline.xml', 'root_id': 'OrdersTimelineRoot', 'host_id': 'MatchHistoryHost'}]
ASSETS = {BINDING + 'layout/custom_game/match_observation_manifest.xml': MANIFEST,
          BINDING + 'layout/custom_game/coach_match_observation.xml': LAYOUT,
          BINDING + 'styles/custom_game/coach_match_observation.css': TARGET + 'styles/custom_game/coach_match_observation.css',
          BINDING + 'scripts/custom_game/match_observation_binding.js': TARGET + 'scripts/custom_game/match_observation_binding.js'}
for prefix, style, scripts in [(OPPONENT, STYLES[0], SCRIPTS[:2]), (HISTORY, STYLES[1], SCRIPTS[2:4])]:
    ASSETS[prefix + 'styles/custom_game/' + style] = TARGET + 'styles/custom_game/' + style
    for name in scripts:
        ASSETS[prefix + 'scripts/custom_game/' + name] = TARGET + 'scripts/custom_game/' + name


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


opponent = load('match_opponent_policy', 'opponent_roster_layout.py')
history = load('match_history_policy', 'orders_timeline_layout.py')
policy = opponent.policy


def shell(root, composed=False):
    outer = root.find('Panel')
    if (outer is None or outer.attrib != {'class': 'CoachMatchObservationCanvas',
            'hittest': 'false', 'hittestchildren': 'true'} or
            len(outer) != 1 or outer[0].tag != 'Panel'):
        raise ValueError('Exact anonymous match canvas required')
    group = outer[0]
    if (group.attrib != {'id': 'CoachMatchObservation', 'class': 'CoachMatchObservation', 'visible': 'false',
                         'hittest': 'false', 'hittestchildren': 'true'} or
            [node.tag for node in group] != ['Label', 'Panel', 'Panel'] or
            group[0].attrib != {'id': 'MatchObservationStatus', 'class': 'MatchObservationStatus', 'html': 'false',
                                'text': '', 'hittest': 'false'}):
        raise ValueError('Exact hidden match shell/status required')
    hosts = list(group)[1:]
    for host, item in zip(hosts, INPUTS):
        if host.attrib != {'id': item['host_id'], 'class': item['host_id'], 'hittest': 'false', 'hittestchildren': 'true'}:
            raise ValueError('Exact ordered match hosts required')
        if (not composed and len(host)) or (composed and (len(host) != 1 or host[0].tag != 'Panel' or host[0].get('id') != item['root_id'])):
            raise ValueError('Match hosts must contain exactly their declared scope')
    return hosts


def prepare(repository, recipe, read_source):
    if (not isinstance(recipe, dict) or set(recipe) != {'schema_version', 'kind', 'assets', 'layout_inputs'} or
            type(recipe['schema_version']) is not int or recipe['schema_version'] != 1 or
            recipe['kind'] != 'panorama_source_match_observation'):
        raise ValueError('Unsupported match observation recipe')
    entries = recipe['assets']
    if not isinstance(entries, list) or len(entries) != 10:
        raise ValueError('Exactly ten match resources required')
    mapping = {}
    for item in entries:
        if (not isinstance(item, dict) or set(item) != {'source', 'target'} or
                not isinstance(item['source'], str) or not isinstance(item['target'], str) or item['source'] in mapping):
            raise ValueError('Unique exact match mapping required')
        mapping[item['source']] = item['target']
    if mapping != ASSETS or recipe['layout_inputs'] != INPUTS:
        raise ValueError('Fixed match mapping and two input scopes required')
    prepared = [(e['source'], e['target'], read_source(repository, e['source'])) for e in entries]
    payloads = {target: raw for _, target, raw in prepared}
    policy.hud_manifest(payloads[MANIFEST], 'coach_match_observation.xml')
    extra = {'Panel': policy.ATTRS['Panel'] | {'visible'}}
    root = policy.parse(payloads[LAYOUT], extra_tags=extra)
    policy.dependencies(root, SCRIPTS, STYLES)
    hosts = shell(root)
    scopes = []
    for item, host, validator in zip(INPUTS, hosts, (opponent.validate_layout, history.validate_layout)):
        raw = read_source(repository, item['source'])
        source = validator(raw)
        scope = source.find('Panel')
        scopes.append(scope)
        host.append(copy.deepcopy(scope))
        root.insert(0, ET.Comment(' source=' + item['source'] + ' sha256=' + hashlib.sha256(raw).hexdigest() + ' '))
    generated = ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'
    if len(generated) > 1024 * 1024:
        raise ValueError('Generated match layout exceeds 1 MiB')
    checked = policy.parse(generated, extra_tags=extra)
    policy.dependencies(checked, SCRIPTS, STYLES)
    final_hosts = shell(checked, composed=True)
    for host, source_scope in zip(final_hosts, scopes):
        if ET.tostring(host[0]) != ET.tostring(source_scope):
            raise ValueError('Canonical match scope must remain unchanged')
    if len(policy.ids(checked.find('Panel'))) != 38:
        raise ValueError('Exactly 38 match IDs required')
    reached = {MANIFEST, LAYOUT}
    for node in checked.findall('./scripts/include') + checked.findall('./styles/include'):
        reached.add(TARGET + node.get('src').removeprefix('file://{resources}/'))
    if reached != set(payloads):
        raise ValueError('Every match output must be reachable')
    return [(source, target, generated if target == LAYOUT else raw) for source, target, raw in prepared]
