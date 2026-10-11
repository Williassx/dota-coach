"""Six fixed canonical resources for inert local text preview, never voice capture."""
import importlib.util
from pathlib import Path

BASE = 'creators/creator-2/'
PANEL = BASE + '06-voice/03-voice-feedback/src/panorama/'
TARGET = 'content/panorama/'
MANIFEST = TARGET + 'layout/custom_game/custom_ui_manifest.xml'
LAYOUT = TARGET + 'layout/custom_game/voice_text.xml'
SCRIPTS = ('roster_cards_state.js', 'voice_text_state.js', 'voice_text_panel.js')
ASSETS = {PANEL + name: TARGET + name for name in (
    'layout/custom_game/custom_ui_manifest.xml', 'layout/custom_game/voice_text.xml',
    'styles/custom_game/voice_text.css', 'scripts/custom_game/voice_text_panel.js')}
for library, name in [('02-coach-interface/01-roster-cards', SCRIPTS[0]), ('06-voice/02-recognition-parser', SCRIPTS[1])]:
    ASSETS[BASE + library + '/src/panorama/scripts/custom_game/' + name] = TARGET + 'scripts/custom_game/' + name

# Reuse the single strict XML/dependency policy. Trusted caller adds only TextEntry;
# the old intervention screen calls parse with the unchanged default allowlist.
spec = importlib.util.spec_from_file_location('voice_text_shared_xml_policy', Path(__file__).with_name('intervention_screen_layout.py'))
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def prepare(repository, recipe, read_source):
    if (not isinstance(recipe, dict) or set(recipe) != {'schema_version', 'kind', 'assets'} or
            type(recipe['schema_version']) is not int or recipe['schema_version'] != 1 or
            recipe['kind'] != 'panorama_source_voice_text'):
        raise ValueError('Unsupported voice text recipe')
    entries = recipe['assets']
    if not isinstance(entries, list) or len(entries) != 6:
        raise ValueError('Exactly six voice text resources required')
    mapping = {}
    for item in entries:
        if (not isinstance(item, dict) or set(item) != {'source', 'target'} or
                not isinstance(item['source'], str) or not isinstance(item['target'], str) or item['source'] in mapping):
            raise ValueError('Unique exact source mapping required')
        mapping[item['source']] = item['target']
    if mapping != ASSETS:
        raise ValueError('Fixed voice text mapping required')
    prepared = [(item['source'], item['target'], read_source(repository, item['source'])) for item in entries]
    payloads = {target: raw for _, target, raw in prepared}
    policy.hud_manifest(payloads[MANIFEST], 'voice_text.xml')
    layout = policy.parse(payloads[LAYOUT], extra_tags={'TextEntry': {'id', 'text', 'enabled'}})
    policy.dependencies(layout, SCRIPTS, ('voice_text.css',))
    group = layout.find('Panel')
    expected = {'VoiceTextRoot': 'Panel', 'VoiceTextInput': 'TextEntry',
                'VoiceTextPreviewButton': 'Button', 'VoiceTextClearButton': 'Button'}
    expected.update({'VoiceText' + name: 'Label' for name in ('Status', 'Normalized', 'Address', 'Action', 'Hint')})
    if policy.ids(group) != expected or group.get('id') != 'VoiceTextRoot' or len(group) != 1 or group[0].tag != 'Panel':
        raise ValueError('Exact voice text root and required IDs expected')
    window = group[0]
    if ([n.tag for n in window] != ['Label', 'Label', 'TextEntry', 'Panel', 'Label', 'Label', 'Label', 'Label'] or
            [n.get('id') for n in window] != [None, 'VoiceTextHint', 'VoiceTextInput', None, 'VoiceTextStatus',
                                            'VoiceTextNormalized', 'VoiceTextAddress', 'VoiceTextAction']):
        raise ValueError('Exact voice text window topology required')
    entry = window[2]
    if entry.attrib != {'id': 'VoiceTextInput', 'enabled': 'false', 'text': ''} or len(entry):
        raise ValueError('Input must be an empty disabled leaf TextEntry')
    buttons = window[3]
    if ([n.tag for n in buttons] != ['Button', 'Button'] or
            [n.get('id') for n in buttons] != ['VoiceTextPreviewButton', 'VoiceTextClearButton'] or
            any(len(n) != 1 or n[0].tag != 'Label' for n in buttons)):
        raise ValueError('Two exact inert preview/clear buttons expected')
    reached = {MANIFEST, LAYOUT}
    for include in layout.findall('./styles/include') + layout.findall('./scripts/include'):
        reached.add(TARGET + include.get('src').removeprefix('file://{resources}/'))
    if reached != set(payloads):
        raise ValueError('Every output must be reachable')
    return prepared
