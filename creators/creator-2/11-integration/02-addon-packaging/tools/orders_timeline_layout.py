"""Five fixed inert order-history resources, not a bootstrap or game integration."""
import importlib.util
from pathlib import Path

SOURCE = 'creators/creator-2/07-match-screen/03-orders-timeline/src/panorama/'
TARGET = 'content/panorama/'
MANIFEST = TARGET + 'layout/custom_game/custom_ui_manifest.xml'
LAYOUT = TARGET + 'layout/custom_game/orders_timeline.xml'
SCRIPTS = ('orders_timeline_state.js', 'orders_timeline_panel.js')
ASSETS = {SOURCE + name: TARGET + name for name in (
    'layout/custom_game/custom_ui_manifest.xml', 'layout/custom_game/orders_timeline.xml',
    'styles/custom_game/orders_timeline.css', 'scripts/custom_game/orders_timeline_state.js',
    'scripts/custom_game/orders_timeline_panel.js')}
spec = importlib.util.spec_from_file_location('timeline_shared_xml_policy',
       Path(__file__).with_name('intervention_screen_layout.py'))
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def validate_layout(payload):
    """Shared canonical input validator for standalone and composed source layouts."""
    layout = policy.parse(payload, extra_tags={'Panel': policy.ATTRS['Panel'] | {'visible'}})
    policy.dependencies(layout, SCRIPTS, ('orders_timeline.css',))
    group = layout.find('Panel')
    names = ['TimelineTitle', 'TimelineSummary', 'TimelineHint', *['TimelineEvent' + str(i) for i in range(6)]]
    if (group.attrib != {'id': 'OrdersTimelineRoot', 'class': 'OrdersTimeline', 'visible': 'false'} or
            policy.ids(group) != {'OrdersTimelineRoot': 'Panel', **{name: 'Label' for name in names}} or
            [n.tag for n in group] != ['Label'] * 9 or [n.get('id') for n in group] != names):
        raise ValueError('Exact inert timeline topology required')
    for node, name in zip(group, names):
        expected_class = name if not name.startswith('TimelineEvent') else 'TimelineEvent'
        if node.attrib != {'id': name, 'class': expected_class, 'html': 'false', 'text': ''}:
            raise ValueError('Exact empty plain timeline Labels required')
    return layout


def prepare(repository, recipe, read_source):
    if (not isinstance(recipe, dict) or set(recipe) != {'schema_version', 'kind', 'assets'} or
            type(recipe['schema_version']) is not int or recipe['schema_version'] != 1 or
            recipe['kind'] != 'panorama_source_orders_timeline'):
        raise ValueError('Unsupported order timeline recipe')
    entries = recipe['assets']
    if not isinstance(entries, list) or len(entries) != 5:
        raise ValueError('Exactly five timeline resources required')
    mapping = {}
    for item in entries:
        if (not isinstance(item, dict) or set(item) != {'source', 'target'} or
                not isinstance(item['source'], str) or not isinstance(item['target'], str) or item['source'] in mapping):
            raise ValueError('Unique exact timeline mapping required')
        mapping[item['source']] = item['target']
    if mapping != ASSETS:
        raise ValueError('Fixed timeline mapping required')
    prepared = [(e['source'], e['target'], read_source(repository, e['source'])) for e in entries]
    payloads = {target: raw for _, target, raw in prepared}
    policy.hud_manifest(payloads[MANIFEST], 'orders_timeline.xml')
    # Root visibility is a trusted local extension; old kinds keep the default.
    layout = validate_layout(payloads[LAYOUT])
    reached = {MANIFEST, LAYOUT}
    for include in layout.findall('./scripts/include') + layout.findall('./styles/include'):
        reached.add(TARGET + include.get('src').removeprefix('file://{resources}/'))
    if reached != set(payloads):
        raise ValueError('Every timeline output must be reachable')
    return prepared
