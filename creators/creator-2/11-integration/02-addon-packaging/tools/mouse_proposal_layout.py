"""Fixed inert mouse-proposal resources; neither permission policy nor native compile."""
import importlib.util
from pathlib import Path

SOURCE = 'creators/creator-2/05-intervention-ui/02-mouse-targeting/src/panorama/'
TARGET = 'content/panorama/'
MANIFEST = TARGET + 'layout/custom_game/custom_ui_manifest.xml'
LAYOUT = TARGET + 'layout/custom_game/mouse_proposal.xml'
SCRIPTS = ('mouse_proposal_state.js', 'mouse_proposal_panel.js')
ASSETS = {SOURCE + name: TARGET + name for name in (
    'layout/custom_game/custom_ui_manifest.xml', 'layout/custom_game/mouse_proposal.xml',
    'styles/custom_game/mouse_proposal.css', 'scripts/custom_game/mouse_proposal_state.js',
    'scripts/custom_game/mouse_proposal_panel.js')}
spec = importlib.util.spec_from_file_location('mouse_shared_xml_policy',
       Path(__file__).with_name('intervention_screen_layout.py'))
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def validate_layout(payload):
    """Validate canonical input without changing older XML policies."""
    layout = policy.parse(payload, extra_tags={'Panel': policy.ATTRS['Panel'] | {'visible'}})
    policy.dependencies(layout, SCRIPTS, ('mouse_proposal.css',))
    group = layout.find('Panel')
    names = ('MouseActor', 'MouseAction', 'MouseTarget', 'MouseState', 'MouseLease', 'MouseHint')
    if (group.attrib != {'id': 'MouseProposalRoot', 'class': 'MouseProposal', 'visible': 'false'} or len(group) != 6):
        raise ValueError('Exact hidden mouse proposal root required')
    for node, name in zip(group, names):
        if node.tag != 'Label' or node.attrib != {'id': name, 'class': name, 'html': 'false', 'text': ''}:
            raise ValueError('Six exact ordered empty plain mouse Labels required')
    if len(policy.ids(group)) != 7:
        raise ValueError('Exact seven mouse proposal IDs required')
    return layout


def prepare(repository, recipe, read_source):
    if (not isinstance(recipe, dict) or set(recipe) != {'schema_version', 'kind', 'assets'} or
            type(recipe['schema_version']) is not int or recipe['schema_version'] != 1 or
            recipe['kind'] != 'panorama_source_mouse_proposal'):
        raise ValueError('Unsupported mouse proposal recipe')
    entries = recipe['assets']
    if not isinstance(entries, list) or len(entries) != 5:
        raise ValueError('Exactly five mouse proposal resources required')
    mapping = {}
    for item in entries:
        if (not isinstance(item, dict) or set(item) != {'source', 'target'} or
                not isinstance(item['source'], str) or not isinstance(item['target'], str) or item['source'] in mapping):
            raise ValueError('Unique exact mouse proposal mapping required')
        mapping[item['source']] = item['target']
    if mapping != ASSETS:
        raise ValueError('Fixed mouse proposal mapping required')
    prepared = [(item['source'], item['target'], read_source(repository, item['source'])) for item in entries]
    payloads = {target: raw for _, target, raw in prepared}
    policy.hud_manifest(payloads[MANIFEST], 'mouse_proposal.xml')
    # This trusted kind permits root visible=false; old parser defaults stay strict.
    layout = validate_layout(payloads[LAYOUT])
    reached = {MANIFEST, LAYOUT}
    for node in layout.findall('./scripts/include') + layout.findall('./styles/include'):
        reached.add(TARGET + node.get('src').removeprefix('file://{resources}/'))
    if reached != set(payloads):
        raise ValueError('Every mouse proposal output must be reachable')
    return prepared
