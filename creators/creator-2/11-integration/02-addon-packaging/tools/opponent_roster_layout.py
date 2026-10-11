"""Fixed inert public-roster resources; neither permission policy nor native compile."""
import importlib.util
from pathlib import Path

SOURCE = 'creators/creator-2/07-match-screen/02-opponent-cards/src/panorama/'
TARGET = 'content/panorama/'
MANIFEST = TARGET + 'layout/custom_game/custom_ui_manifest.xml'
LAYOUT = TARGET + 'layout/custom_game/opponent_roster.xml'
SCRIPTS = ('opponent_roster_state.js', 'opponent_roster_panel.js')
ASSETS = {SOURCE + name: TARGET + name for name in (
    'layout/custom_game/custom_ui_manifest.xml', 'layout/custom_game/opponent_roster.xml',
    'styles/custom_game/opponent_roster.css', 'scripts/custom_game/opponent_roster_state.js',
    'scripts/custom_game/opponent_roster_panel.js')}
spec = importlib.util.spec_from_file_location('opponent_shared_xml_policy',
       Path(__file__).with_name('intervention_screen_layout.py'))
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def plain_label(node, name, style):
    if node.tag != 'Label' or node.attrib != {'id': name, 'class': style, 'html': 'false', 'text': ''}:
        raise ValueError('Exact empty plain opponent Labels required')


def validate_layout(payload):
    """Shared canonical input validator for the standalone and composed packages."""
    layout = policy.parse(payload, extra_tags={'Panel': policy.ATTRS['Panel'] | {'visible'}})
    policy.dependencies(layout, SCRIPTS, ('opponent_roster.css',))
    group = layout.find('Panel')
    if (group.attrib != {'id': 'OpponentRosterRoot', 'class': 'OpponentRoster', 'visible': 'false'} or
            [node.tag for node in group] != ['Label', 'Label', 'Panel']):
        raise ValueError('Exact hidden opponent root topology required')
    plain_label(group[0], 'OpponentRosterStatus', 'OpponentStatus')
    plain_label(group[1], 'OpponentRosterHint', 'OpponentHint')
    strip = group[2]
    if strip.attrib != {'id': 'OpponentCards', 'class': 'OpponentCards'} or len(strip) != 5:
        raise ValueError('Exact five-card opponent strip required')
    for i, card in enumerate(strip):
        if (card.tag != 'Panel' or card.attrib != {'id': 'OpponentCard' + str(i), 'class': 'OpponentCard'} or len(card) != 3):
            raise ValueError('Exact ordered opponent card containers required')
        for node, field in zip(card, ('Name', 'Hero', 'Information')):
            plain_label(node, 'Opponent' + field + str(i), 'Opponent' + field)
    if len(policy.ids(group)) != 24:
        raise ValueError('Every opponent slot must own its three Labels')
    return layout


def prepare(repository, recipe, read_source):
    if (not isinstance(recipe, dict) or set(recipe) != {'schema_version', 'kind', 'assets'} or
            type(recipe['schema_version']) is not int or recipe['schema_version'] != 1 or
            recipe['kind'] != 'panorama_source_opponent_roster'):
        raise ValueError('Unsupported opponent roster recipe')
    entries = recipe['assets']
    if not isinstance(entries, list) or len(entries) != 5:
        raise ValueError('Exactly five opponent resources required')
    mapping = {}
    for item in entries:
        if (not isinstance(item, dict) or set(item) != {'source', 'target'} or
                not isinstance(item['source'], str) or not isinstance(item['target'], str) or item['source'] in mapping):
            raise ValueError('Unique exact opponent mapping required')
        mapping[item['source']] = item['target']
    if mapping != ASSETS:
        raise ValueError('Fixed opponent mapping required')
    prepared = [(item['source'], item['target'], read_source(repository, item['source'])) for item in entries]
    payloads = {target: raw for _, target, raw in prepared}
    policy.hud_manifest(payloads[MANIFEST], 'opponent_roster.xml')
    # This trusted kind permits root visible=false; old parser defaults stay strict.
    layout = validate_layout(payloads[LAYOUT])
    reached = {MANIFEST, LAYOUT}
    for node in layout.findall('./scripts/include') + layout.findall('./styles/include'):
        reached.add(TARGET + node.get('src').removeprefix('file://{resources}/'))
    if reached != set(payloads):
        raise ValueError('Every opponent output must be reachable')
    return prepared
