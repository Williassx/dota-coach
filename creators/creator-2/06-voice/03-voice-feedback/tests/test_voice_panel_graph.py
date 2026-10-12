import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


class VoicePanelGraph(unittest.TestCase):
    def setUp(self):
        self.layout = ET.parse(BASE / 'src/panorama/layout/custom_game/voice_text.xml').getroot()

    def test_native_root_anonymous_and_binding_scope_is_inner_panel(self):
        outer = self.layout.find('./Panel')
        self.assertNotIn('id', outer.attrib)
        self.assertEqual(outer.find('./Panel').get('id'), 'VoiceTextRoot')

    def test_dependencies_exact_single_context(self):
        self.assertEqual([n.tag for n in self.layout], ['styles', 'scripts', 'Panel'])
        self.assertEqual([n.attrib for n in self.layout.find('scripts')], [
            {'src': 'file://{resources}/scripts/custom_game/' + name}
            for name in ['roster_cards_state.js', 'voice_text_state.js', 'voice_text_panel.js']])
        self.assertEqual([n.attrib for n in self.layout.find('styles')], [
            {'src': 'file://{resources}/styles/custom_game/voice_text.css'}])

    def test_required_ids_types_unique(self):
        ids = [n.attrib['id'] for n in self.layout.iter() if 'id' in n.attrib]
        expected = {'VoiceTextRoot': 'Panel', 'VoiceTextInput': 'TextEntry',
                    'VoiceTextPreviewButton': 'Button', 'VoiceTextClearButton': 'Button'}
        expected.update({'VoiceText' + name: 'Label' for name in ['Status', 'Normalized', 'Address', 'Action', 'Hint']})
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({n.attrib['id']: n.tag for n in self.layout.iter() if 'id' in n.attrib}, expected)

    def test_plain_labels_disabled_inputs_and_no_loader_events(self):
        for node in self.layout.iter():
            self.assertIn(node.tag, ['root', 'styles', 'scripts', 'include', 'Panel', 'Label', 'TextEntry', 'Button'])
            self.assertFalse(any(k.lower().startswith('on') for k in node.attrib))
            if node.tag == 'Label':
                self.assertEqual(node.attrib['html'], 'false')
            if node.tag in ['Button', 'TextEntry']:
                self.assertEqual(node.attrib['enabled'], 'false')
        self.assertFalse(any(n.tag == 'CustomUIElement' for n in self.layout.iter()))


if __name__ == '__main__':
    unittest.main()
