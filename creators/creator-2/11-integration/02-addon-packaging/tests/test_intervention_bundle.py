"""Fixed source recipe for the manual-request panel; no native game proof."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

REPOSITORY = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
TOOLS = REPOSITORY / 'creators/creator-2/01-foundation/02-panorama-capability/tools'
LAYOUT = 'content/panorama/layout/custom_game/intervention_request.xml'
MANIFEST = 'content/panorama/layout/custom_game/custom_ui_manifest.xml'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    old = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old
    return module


builder = load('intervention_builder', TOOLS / 'build_probe_bundle.py')
sys.path.insert(0, str(TOOLS))
try:
    verifier = load('intervention_verifier', TOOLS / 'verify_probe_bundle.py')
finally:
    sys.path.pop(0)


class InterventionBundleTests(unittest.TestCase):
    def setUp(self):
        source = TASK / 'intervention-manifest.json'
        self.assertTrue(source.is_file(), 'manual request recipe not implemented')
        self.manifest = json.loads(source.read_text())
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)
        self.output = self.repo / 'build/dota_coach/intervention'
        for item in self.manifest['assets']:
            target = self.repo / item['source']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((REPOSITORY / item['source']).read_bytes())

    def source(self, target):
        return self.repo / next(a['source'] for a in self.manifest['assets'] if a['target'] == target)

    def build(self):
        return builder.build_bundle(self.repo, self.manifest, self.output)

    def reject_xml(self, target, mutate):
        source = self.source(target)
        original = source.read_bytes()
        tree = ET.fromstring(original)
        mutate(tree)
        source.write_bytes(ET.tostring(tree))
        try:
            with self.assertRaises(ValueError):
                self.build()
            self.assertFalse(self.output.exists())
        finally:
            source.write_bytes(original)

    def test_actual_source_roundtrip_six_assets_five_links_no_native_claim(self):
        report = self.build()
        self.assertEqual(report['kind'], 'panorama_source_intervention')
        self.assertEqual(len(report['assets']), 6)
        self.assertFalse(report['source2_compiled'])
        self.assertFalse(report['runtime_verified'])
        for item in self.manifest['assets']:
            self.assertEqual((self.output / item['target']).read_bytes(), (self.repo / item['source']).read_bytes())
        result = verifier.verify_bundle(self.repo, self.manifest, self.output)
        self.assertEqual(result['assets'], 6)
        self.assertEqual(result['xml_resource_links'], 5)
        self.assertFalse(result['runtime_verified'])

    def test_other_existing_source_recipes_and_probe_default_are_unchanged(self):
        self.assertEqual(json.loads(builder.MANIFEST.read_text())['kind'], 'panorama_source_probe')
        for name, count in [('bundle-manifest.json', 13), ('preparation-manifest.json', 15)]:
            manifest = json.loads((TASK / name).read_text())
            self.assertEqual(len(builder.prepare_assets(REPOSITORY, manifest)), count)

    def test_fixed_mapping_rejects_other_library_source_or_remapped_destination(self):
        for key, value in [('source', 'creators/creator-2/02-coach-interface/02-status-orders/src/panorama/scripts/custom_game/orders_panel.js'),
                           ('target', 'content/panorama/scripts/custom_game/renamed.js')]:
            candidate = copy.deepcopy(self.manifest)
            candidate['assets'][-1][key] = value
            with self.assertRaises(ValueError):
                builder.build_bundle(self.repo, candidate, self.output)
            self.assertFalse(self.output.exists())

    def test_missing_extra_duplicate_assets_and_schema_fields_fail_before_output(self):
        for mode in ['missing', 'extra', 'duplicate', 'schema', 'version']:
            candidate = copy.deepcopy(self.manifest)
            if mode == 'missing': candidate['assets'].pop()
            elif mode == 'extra': candidate['assets'].append({'source':'other.js','target':'content/panorama/other.js'})
            elif mode == 'duplicate': candidate['assets'].append(copy.deepcopy(candidate['assets'][0]))
            elif mode == 'schema': candidate['bootstrap'] = True
            else: candidate['schema_version'] = True
            with self.assertRaises(ValueError): builder.build_bundle(self.repo, candidate, self.output)
            self.assertFalse(self.output.exists())

    def test_script_order_and_single_style_are_required(self):
        def reorder(root):
            scripts = root.find('scripts');first=scripts[0];scripts.remove(first);scripts.append(first)
        self.reject_xml(LAYOUT, reorder)
        self.reject_xml(LAYOUT, lambda root: ET.SubElement(root.find('styles'), 'include', {'src':'file://{resources}/styles/custom_game/intervention_request.css'}))

    def test_manifest_is_exact_single_hud_element_without_extra_children_or_attrs(self):
        self.reject_xml(MANIFEST, lambda root: root.set('onload', 'bind()'))
        self.reject_xml(MANIFEST, lambda root: root.find('Panel/CustomUIElement').set('other', 'x'))
        self.reject_xml(MANIFEST, lambda root: ET.SubElement(root.find('Panel'), 'Label'))
        self.reject_xml(MANIFEST, lambda root: ET.SubElement(root.find('Panel/CustomUIElement'), 'Panel'))
        self.reject_xml(MANIFEST, lambda root: root.find('Panel/CustomUIElement').set('layoutfile','file://{resources}/layout/custom_game/coach_hud.xml'))

    def test_body_disallows_inline_events_script_nested_layout_and_resource_src(self):
        for tag in ['run', 'script', 'CustomUIElement']:
            self.reject_xml(LAYOUT, lambda root, tag=tag: ET.SubElement(root.find('Panel'), tag))
        for key, value in [('onactivate','bind()'),('src','https://example.com/x'),('layoutfile','file://{resources}/layout/custom_game/intervention_request.xml')]:
            self.reject_xml(LAYOUT, lambda root, key=key, value=value: root.find('Panel').set(key,value))

    def test_required_ids_plain_labels_and_disabled_single_button(self):
        self.reject_xml(LAYOUT, lambda root: next(root.iter('Label')).set('html','true'))
        self.reject_xml(LAYOUT, lambda root: next(root.iter('Button')).set('enabled','true'))
        self.reject_xml(LAYOUT, lambda root: next(n for n in root.iter() if n.get('id')=='ManualRequestHint').set('id','ManualRequestMode'))
        self.reject_xml(LAYOUT, lambda root: ET.SubElement(root.find('Panel'),'Button',{'enabled':'false'}))

    def test_include_must_be_leaf_exact_src_without_executable_text(self):
        self.reject_xml(LAYOUT, lambda root: ET.SubElement(root.find('scripts/include'),'run'))
        self.reject_xml(LAYOUT, lambda root: root.find('scripts/include').set('extra','x'))
        def text(root): root.find('scripts/include').text='run()'
        self.reject_xml(LAYOUT, text)

    def test_dtd_and_entities_rejected_without_output(self):
        source = self.source(LAYOUT)
        source.write_text('<!DOCTYPE root [<!ENTITY item "x">]>\n' + source.read_text())
        with self.assertRaises(ValueError): self.build()
        self.assertFalse(self.output.exists())

    def test_verifier_rejects_tampered_output_and_changed_current_source(self):
        self.build()
        destination=self.output/'content/panorama/scripts/custom_game/intervention_request_panel.js'
        old=destination.read_bytes();destination.write_bytes(old+b'\nchanged')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo,self.manifest,self.output)
        destination.write_bytes(old)
        source=self.source('content/panorama/styles/custom_game/intervention_request.css')
        source.write_bytes(source.read_bytes()+b'\n/* new source */')
        with self.assertRaises(ValueError): verifier.verify_bundle(self.repo,self.manifest,self.output)

    def test_existing_output_is_preserved(self):
        self.output.mkdir(parents=True);marker=self.output/'keep';marker.write_bytes(b'keep')
        with self.assertRaises(FileExistsError): self.build()
        self.assertEqual(marker.read_bytes(),b'keep')

    def test_manifest_loader_cannot_be_sibling_of_its_panel(self):
        def move(root):
            panel=root.find('Panel');element=panel[0];panel.remove(element);root.append(element)
        self.reject_xml(MANIFEST,move)
