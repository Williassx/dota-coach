"""Static source graph only, no Source2 compiler or native hit testing."""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

TASK=Path(__file__).resolve().parents[1]
XML=TASK/'src/panorama/layout/custom_game/intervention_request.xml'
CSS=TASK/'src/panorama/styles/custom_game/intervention_request.css'

class InterventionLayoutTests(unittest.TestCase):
    def tree(self):
        self.assertTrue(XML.is_file(),'manual request source XML missing')
        return ET.parse(XML).getroot()
    def test_exact_required_ids_and_plain_labels_disabled_request(self):
        root=self.tree();ids=[n.get('id') for n in root.iter() if n.get('id')]
        self.assertEqual(set(ids),{'ManualRequestRoot','ManualRequestButton'}|{'ManualRequest'+n for n in ['Recipient','Mode','Actor','State','Reason','Message','Hint']})
        self.assertEqual(len(ids),9);self.assertTrue(all(n.get('html')=='false' for n in root.iter('Label')))
        buttons=list(root.iter('Button'));self.assertEqual(len(buttons),1);self.assertEqual(buttons[0].get('enabled'),'false')
    def test_three_definitions_in_dependency_order_and_one_local_style(self):
        root=self.tree();scripts=[n.get('src') for n in root.findall('./scripts/include')]
        self.assertEqual(scripts,['file://{resources}/scripts/custom_game/'+name for name in ['orders_state.js','intervention_request_state.js','intervention_request_panel.js']])
        self.assertEqual([n.get('src') for n in root.findall('./styles/include')],['file://{resources}/styles/custom_game/intervention_request.css'])
        for name in ['intervention_request_state.js','intervention_request_panel.js']:
            self.assertTrue((TASK/'src/panorama/scripts/custom_game'/name).is_file())
        self.assertTrue((TASK.parent.parent/'02-coach-interface/02-status-orders/src/panorama/scripts/custom_game/orders_state.js').is_file())
    def test_no_bootstrap_events_nested_layout_or_native_compilation_claim(self):
        root=self.tree()
        for n in root.iter():
            self.assertNotIn(n.tag.lower(),['run','script','customuielement'])
            self.assertFalse(any(k.lower().startswith('on') for k in n.attrib));self.assertNotIn('layoutfile',n.attrib)
    def test_initial_mode_unavailable_distinct_inactive_and_actor_unknown(self):
        root=self.tree();nodes={n.get('id'):n for n in root.iter()}
        self.assertIn('недоступен',nodes['ManualRequestMode'].get('text',''))
        self.assertNotIn('неактивен',nodes['ManualRequestMode'].get('text',''))
        self.assertIn('Нет адресата',nodes['ManualRequestActor'].get('text',''))
        self.assertIn('Запросить ручное',nodes['ManualRequestHint'].get('text',''))
        self.assertIn('не подключён',nodes['ManualRequestMessage'].get('text',''))
    def test_declared_style_classes_resolve_and_wrapping_source_available(self):
        root=self.tree();self.assertTrue(CSS.is_file(),'manual request CSS missing');css=CSS.read_text()
        classes={n for node in root.iter() for n in node.get('class','').split()}
        defined=set(re.findall(r'\.([A-Za-z][A-Za-z0-9_-]*)',css));self.assertTrue(classes<=defined)
        self.assertIn('white-space: normal',css);self.assertIn('height: fit-children',css)

if __name__=='__main__':unittest.main()
