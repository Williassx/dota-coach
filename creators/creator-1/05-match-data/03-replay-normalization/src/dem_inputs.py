"""Fail-closed local input and provenance checks."""
import dataclasses
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from dem_types import DemImportError, InputSpec, Limits, ImportContext, canonical_json, uint64_decimal

BASE = Path(__file__).resolve().parent.parent
BUILD = BASE.parents[3] / 'build/dota_coach/dem-import-v1'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()


def checked_path(path: Path, *, may_not_exist=False) -> Path:
    raw = str(path)
    if raw.startswith(('\\\\', '//')):
        raise DemImportError(2, 'network_path_not_supported')
    absolute = Path(os.path.abspath(path))
    for component in [*reversed(absolute.parents), absolute]:
        try:
            s = component.lstat()
        except FileNotFoundError:
            if may_not_exist and component == absolute: continue
            raise DemImportError(2, 'missing_path:' + str(component))
        if stat.S_ISLNK(s.st_mode) or getattr(s, 'st_file_attributes', 0) & 0x400:
            raise DemImportError(2, 'reparse_path:' + str(component))
    return absolute


def read_json(path: Path) -> dict:
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d: raise DemImportError(2, 'duplicate_json_key:' + k)
            d[k] = v
        return d
    try:
        if path.stat().st_size > 1024 * 1024: raise DemImportError(2, 'oversize_configuration')
        value = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(DemImportError(2, 'nonfinite_json')))
        if not isinstance(value, dict): raise DemImportError(2, 'object_required')
        return value
    except (OSError, ValueError, UnicodeError) as exc:
        raise DemImportError(2, 'invalid_json:' + str(path)) from exc


def exact_keys(obj, allowed, required):
    if not isinstance(obj, dict) or set(obj) - set(allowed) or set(required) - set(obj):
        raise DemImportError(2, 'unknown_or_missing_config_keys')


def validate_inputs(spec: InputSpec) -> ImportContext:
    try:
        paths = {k: checked_path(getattr(spec, k), may_not_exist=k == 'output')
                 for k in ['input', 'lock', 'config', 'output']}
        if isinstance(spec.match_id, bool) or not isinstance(spec.match_id, int) or spec.match_id <= 0:
            raise DemImportError(2, 'invalid_match_id')
        try: uint64_decimal(spec.match_id)
        except DemImportError as exc: raise DemImportError(2, 'invalid_match_id') from exc
        if type(spec.account_id) is not int or not 0 < spec.account_id < 2**32:
            raise DemImportError(2, 'invalid_account_id')
        spec = dataclasses.replace(spec, **paths)
        config = read_json(spec.config)
        exact_keys(config, ['schema', 'java_home', 'jar_directory', 'fields', 'episode_windows', 'limits'],
                   ['schema', 'java_home', 'jar_directory', 'fields', 'episode_windows', 'limits'])
        if config['schema'] != 'dem-import-config-v1': raise DemImportError(2, 'config_schema')
        fields = config['fields']
        if not isinstance(fields, list) or any(f not in ['raw_position', 'raw_control'] for f in fields) or len(fields) != len(set(fields)):
            raise DemImportError(2, 'unsupported_fields')
        exact_keys(config['limits'], dataclasses.asdict(Limits()), [])
        limits = Limits(**config['limits'])
        if any(type(v) is not int or v <= 0 for v in dataclasses.asdict(limits).values()):
            raise DemImportError(2, 'invalid_limits')
        windows = config['episode_windows']
        if not isinstance(windows, list) or len(windows) > limits.max_windows: raise DemImportError(2, 'invalid_windows')
        ids = set()
        for w in windows:
            exact_keys(w, ['id', 'start_demo_tick', 'end_demo_tick'], ['id', 'start_demo_tick', 'end_demo_tick'])
            if not isinstance(w['id'], str) or not 1 <= len(w['id']) <= 100 or w['id'] in ids:
                raise DemImportError(2, 'window_id')
            ids.add(w['id'])
            if any(type(w[k]) is not int for k in ['start_demo_tick', 'end_demo_tick']) or not 0 <= w['start_demo_tick'] <= w['end_demo_tick']:
                raise DemImportError(2, 'window_interval')
        if not spec.input.is_file() or not 16 <= spec.input.stat().st_size <= limits.max_input_bytes:
            raise DemImportError(2, 'dem_size')
        with spec.input.open('rb') as f:
            if f.read(8) != b'PBDEMS2\x00': raise DemImportError(2, 'unsupported_dem_magic')
        java_home, jars = checked_path(Path(config['java_home'])), checked_path(Path(config['jar_directory']))
        lock = read_json(spec.lock)
        if lock.get('schema') != 'dem-dependencies-v1' or lock.get('parser') != 'Clarity5.0.1' or lock.get('protobuf') != '7.1' or lock.get('jdk_version') != '21.0.12.1+1':
            raise DemImportError(2, 'unsupported_lock')
        pins = lock.get('jars', [])
        if not isinstance(pins, list) or len(pins) != 8: raise DemImportError(2, 'eight_dependency_pins_required')
        hashes = {k: sha256(paths[k]) for k in ['input', 'lock', 'config']}
        jar_paths, names = [], set()
        for pin in pins:
            name = pin['name']
            if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+\.jar', name) or name in names:
                raise DemImportError(2, 'invalid_jar_name')
            names.add(name)
            p = checked_path(jars / name)
            h = sha256(p)
            if p.stat().st_size != pin['bytes'] or h != pin['sha256']: raise DemImportError(2, 'jar_hash:' + name)
            hashes['jar:' + name] = h; jar_paths.append(str(p))
        jdk_files = lock.get('jdk_files')
        if not isinstance(jdk_files, dict) or set(jdk_files) != {'release', 'bin/java.exe', 'bin/javac.exe'}:
            raise DemImportError(2, 'jdk_pins_required')
        for name, expected in jdk_files.items():
            p = checked_path(java_home / name); actual = sha256(p)
            if actual != expected: raise DemImportError(2, 'jdk_hash:' + name)
            hashes['jdk:' + name] = actual
        for p in sorted((BASE / 'src').glob('*')):
            if p.suffix in ['.py', '.java']: hashes['source:' + p.name] = sha256(p)
        schema = BASE / 'notes/dem-schema-v1.json'
        if schema.exists(): hashes['schema'] = sha256(checked_path(schema))
        for name in ['evidence.json', 'observations.json']:
            p = BASE / 'reports/03-native-tick-calibration' / name
            if p.exists(): hashes['calibration:' + name] = sha256(checked_path(p))
        return ImportContext(spec, limits, hashes, {'java_home': str(java_home), 'jars': jar_paths}, config)
    except DemImportError:
        raise
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise DemImportError(2, 'invalid_input:' + str(exc)) from exc


def cache_key(context: ImportContext) -> str:
    return hashlib.sha256(canonical_json({'hashes': context.hashes, 'match_id': str(context.spec.match_id),
                                         'account_id': context.spec.account_id, 'schema': 'dem-import-v1'})).hexdigest()
