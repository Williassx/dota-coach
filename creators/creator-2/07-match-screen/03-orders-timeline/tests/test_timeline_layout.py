from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1] / 'src/panorama'


class TimelineLayout(unittest.TestCase):
    def test_exact_plain_label_ids(self):
        tree = ET.parse(BASE / 'layout/custom_game/orders_timeline.xml')
        ids = {node.attrib['id']: node.tag for node in tree.iter() if 'id' in node.attrib}
        self.assertEqual(ids, {'OrdersTimelineRoot': 'Panel', **{name: 'Label' for name in
            ['TimelineTitle', 'TimelineSummary', 'TimelineHint', *['TimelineEvent' + str(i) for i in range(6)]]}})
        for node in tree.iter('Label'):
            self.assertEqual(node.attrib.get('html'), 'false')
            self.assertEqual(node.attrib.get('text'), '')
        self.assertEqual(tree.find(".//*[@id='OrdersTimelineRoot']").attrib.get('visible'), 'false')

    def test_dependencies_are_exact_inert_and_exist(self):
        tree = ET.parse(BASE / 'layout/custom_game/orders_timeline.xml')
        for section, expected in [('scripts', ['scripts/custom_game/orders_timeline_state.js',
                                            'scripts/custom_game/orders_timeline_panel.js']),
                                  ('styles', ['styles/custom_game/orders_timeline.css'])]:
            nodes = list(tree.getroot().find(section))
            self.assertEqual([n.attrib for n in nodes], [{'src': 'file://{resources}/' + s} for s in expected])
            for source in expected: self.assertTrue((BASE / source).is_file())
        for node in tree.iter():
            self.assertFalse((node.text or '').strip())
            self.assertFalse((node.tail or '').strip())
            self.assertFalse(any(key.lower().startswith('on') for key in node.attrib))
        script = (BASE / 'scripts/custom_game/orders_timeline_panel.js').read_text()
        self.assertNotIn('$.', script)


if __name__ == '__main__':
    unittest.main()
