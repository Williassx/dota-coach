"""Source graph only; no native layout or input evidence."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

PANORAMA = Path(__file__).resolve().parents[1] / 'src/panorama'

class MouseLayout(unittest.TestCase):
    def test_seven_ids_six_empty_plain_labels_no_handlers(self):
        root = ET.parse(PANORAMA / 'layout/custom_game/mouse_proposal.xml').getroot()
        panel = root.find('Panel')
        self.assertEqual(panel.attrib, {'id':'MouseProposalRoot','class':'MouseProposal','visible':'false'})
        names = ['MouseActor','MouseAction','MouseTarget','MouseState','MouseLease','MouseHint']
        self.assertEqual(len(panel),6)
        for node, name in zip(panel,names):
            self.assertEqual(node.tag,'Label')
            self.assertEqual(node.attrib,{'id':name,'class':name,'html':'false','text':''})
            self.assertEqual(len(node),0)
        self.assertEqual(len([n for n in root.iter() if 'id' in n.attrib]),7)
        self.assertFalse(any(k.startswith('on') for n in root.iter() for k in n.attrib))

    def test_ordered_existing_dependencies_and_inert_loader(self):
        root = ET.parse(PANORAMA / 'layout/custom_game/mouse_proposal.xml').getroot()
        self.assertEqual([n.tag for n in root],['styles','scripts','Panel'])
        self.assertEqual([n.get('src') for n in root.find('scripts')],
            ['file://{resources}/scripts/custom_game/'+n for n in ['mouse_proposal_state.js','mouse_proposal_panel.js']])
        for n in root.findall('./scripts/include')+root.findall('./styles/include'):
            self.assertTrue((PANORAMA / n.get('src').removeprefix('file://{resources}/')).is_file())
        loader=ET.parse(PANORAMA/'layout/custom_game/custom_ui_manifest.xml').getroot()
        self.assertEqual(loader.find('.//CustomUIElement').attrib,
            {'type':'Hud','layoutfile':'file://{resources}/layout/custom_game/mouse_proposal.xml'})

if __name__=='__main__': unittest.main()
