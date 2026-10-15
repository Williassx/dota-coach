import hashlib
import dataclasses
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from dem_types import InputSpec, DemImportError, canonical_json, uint64_decimal
from dem_inputs import validate_inputs, cache_key, sha256, read_json, checked_path


class InputTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.jdk = self.root / 'jdk'
        (self.jdk / 'bin').mkdir(parents=True)
        for name in ['release', 'bin/java.exe', 'bin/javac.exe']:
            (self.jdk / name).write_bytes(name.encode())
        self.jars = self.root / 'jars'
        self.jars.mkdir()
        pins = []
        for i in range(8):
            p = self.jars / f'pin-{i}.jar'
            p.write_bytes(bytes([i]))
            pins.append({'name': p.name, 'bytes': 1, 'sha256': sha256(p)})
        self.lock = self.root / 'lock.json'
        self.lock.write_text(json.dumps({'schema': 'dem-dependencies-v1', 'parser': 'Clarity5.0.1',
            'protobuf': '7.1', 'jdk_version': '21.0.12.1+1', 'jars': pins,
            'jdk_files': {name: sha256(self.jdk / name) for name in ['release', 'bin/java.exe', 'bin/javac.exe']}}))
        self.config = self.root / 'config.json'
        self.config.write_text(json.dumps({'schema': 'dem-import-config-v1', 'java_home': str(self.jdk),
            'jar_directory': str(self.jars), 'fields': [], 'episode_windows': [], 'limits': {}}))
        self.dem = self.root / 'input.dem'
        self.dem.write_bytes(b'PBDEMS2\x00' + b'\x00' * 24)
        self.spec = InputSpec(self.dem, 9042986015, 70388657, self.lock, self.config, self.root / 'out')

    def test_inputs_reject_codec_truncation_duplicate_keys_and_tampered_jar(self):
        validate_inputs(self.spec)
        for bad in [b'\x28\xb5\x2f\xfd', b'PBDEMS2\x00']:
            self.dem.write_bytes(bad)
            with self.assertRaises(DemImportError): validate_inputs(self.spec)
        self.dem.write_bytes(b'PBDEMS2\x00' + b'\x00' * 24)
        (self.jars / 'pin-0.jar').write_bytes(b'changed')
        with self.assertRaises(DemImportError): validate_inputs(self.spec)
        self.config.write_text('{"fields":[],"fields":[]}')
        with self.assertRaises(DemImportError): read_json(self.config)

    def test_lock_duplicate_unknown_config_and_invalid_limit(self):
        original_lock = self.lock.read_text(); original_config = self.config.read_text()
        d = json.loads(original_lock); d['jars'][1] = d['jars'][0]
        self.lock.write_text(json.dumps(d))
        with self.assertRaises(DemImportError): validate_inputs(self.spec)
        self.lock.write_text(original_lock)
        for change in [{'unexpected': True}, {'limits': {'timeout_seconds': 0}}, {'fields': ['world_position']}]:
            d = json.loads(original_config); d.update(change); self.config.write_text(json.dumps(d))
            with self.assertRaises(DemImportError): validate_inputs(self.spec)

    def test_uint64_canonical(self):
        for n in [0, 9007199254740993, 18446744073709551615]: self.assertEqual(uint64_decimal(n), str(n))
        for n in [-1, 18446744073709551616, '01', '+1', True, 1.1]:
            with self.assertRaises(DemImportError): uint64_decimal(n)
        self.assertEqual(canonical_json({'state64': '18446744073709551615'}), b'{"state64":"18446744073709551615"}\n')
        with self.assertRaises(DemImportError): canonical_json({'mana': float('nan')})

    def test_paths_reject_reparse_escape(self):
        with self.assertRaises(DemImportError): checked_path(Path('//server/share/input.dem'))
        with self.assertRaises(DemImportError): checked_path(self.root / 'missing' / 'x')

    def test_cache_key_changes_for_each_provenance_input(self):
        ctx = validate_inputs(self.spec); old = cache_key(ctx)
        for key in list(ctx.hashes):
            saved = ctx.hashes[key]; ctx.hashes[key] = '0' * 64
            self.assertNotEqual(old, cache_key(ctx), key); ctx.hashes[key] = saved
        self.assertEqual(old, cache_key(validate_inputs(self.spec)))

    def test_out_of_range_match_id_is_input_error(self):
        with self.assertRaises(DemImportError) as caught:validate_inputs(dataclasses.replace(self.spec,match_id=2**64))
        self.assertEqual(caught.exception.code,2)


if __name__ == '__main__': unittest.main()
