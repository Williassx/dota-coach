import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

class FixtureTests(unittest.TestCase):
 def load(self):
  p=Path(__file__).resolve().parents[1]/'tools/build_native_move_fixture.py'
  self.assertTrue(p.exists(),'native fixture generator missing')
  spec=importlib.util.spec_from_file_location('native_move_test',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 def test_fixture_keeps_canonical_and_adds_only_test_driver_and_layout(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);o=root/'build/dota_coach/native'
   inputs=[('source.xml','content/panorama/layout/custom_game/manual_move.xml',b'<root><scripts><include src="manual_move_panel.js"/></scripts><Panel /></root>',False)]
   inputs += [('source'+str(i),'game/dummy'+str(i),b'payload',False) for i in range(5)]
   inputs += [('generated:manifest',m.bundle.MANIFEST,m.bundle.MANIFEST_BYTES,True)]
   with patch.object(m.bundle,'prepare',return_value=inputs),patch.object(m.bundle.policy,'read_source',return_value=b'// TEST'):
    r=m.build_fixture(root,o)
   self.assertEqual(len(r['assets']),9)
   self.assertTrue((o/'content/panorama/layout/custom_game/manual_move.xml').exists())
   raw=(o/'content/panorama/layout/custom_game/manual_move_fixture.xml').read_text()
   self.assertIn('manual_move_fixture.js',raw)
   self.assertIn('manual_move_panel.js',raw)
 def test_fixture_refuses_existing_output(self):
  m=self.load()
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);o=root/'build/dota_coach/native';o.mkdir(parents=True);(o/'user').write_text('keep')
   with self.assertRaises(FileExistsError):m.build_fixture(root,o)
   self.assertEqual((o/'user').read_text(),'keep')
if __name__=='__main__':unittest.main()
