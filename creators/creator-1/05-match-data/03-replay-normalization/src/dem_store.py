"""Bounded offline process, validation and Windows no-replace publication."""
import ctypes
import dataclasses
import hashlib
import json
import math
import os
import re
import subprocess
import threading
import time
import uuid
from pathlib import Path
from dem_types import DemImportError, ImportResult, canonical_json, uint64_decimal
from dem_inputs import BASE, BUILD, cache_key, checked_path, read_json, sha256, validate_inputs
from dem_episodes import build_episodes

STREAMS = ('states', 'events', 'gaps')


def calibration_reference(ctx):
    empty = {'status':'unverified','points':[],'whole_native_payload_verified':False}
    evidence_path = BASE/'reports/03-native-tick-calibration/evidence.json'
    observations_path = BASE/'reports/03-native-tick-calibration/observations.json'
    if not evidence_path.exists() or not observations_path.exists(): return empty
    e, observations = read_json(evidence_path), read_json(observations_path)
    if e.get('dem_sha256') != ctx.hashes['input'] or e.get('match_id') != ctx.spec.match_id: return empty
    points = []
    for p in observations['points']:
        if p['comparison']['status'] == 'exact_csv_tick_fields_consistent' and p['decoded_source']['fields']['actor_account_id'] == str(ctx.spec.account_id):
            points.append({'demo_tick':p['native_cursor']['before'],'hud':p['hud_readback'],'png_sha256':p['image']['sha256']})
    if not points: return empty
    return {'status':'scoped_hud_reference','points':points,'client_build':e['client_build'],
            'evidence_sha256':sha256(evidence_path),'observations_sha256':sha256(observations_path),
            'whole_native_payload_verified':False,'actual_pause_verified':False}


def prepare_runtime(ctx):
    receipt = checked_path(BUILD / 'compile-receipt.json')
    compiled = read_json(receipt)
    if compiled.get('schema') != 'dem-compile-v1' or compiled.get('lock_sha256') != ctx.hashes['lock']:
        raise DemImportError(2, 'stale_compile_receipt')
    sources = {p.name: sha256(checked_path(p)) for p in (BASE / 'src').glob('*.java')}
    if compiled.get('sources') != sources: raise DemImportError(2, 'recompile_java_sources')
    paths = sorted((BUILD / 'classes').glob('*.class'))
    actual = {p.name: sha256(checked_path(p)) for p in paths}
    if not actual or compiled.get('classes') != actual or 'TelemetryEmitter.class' not in actual:
        raise DemImportError(2, 'compiled_class_hash')
    ctx.hashes.update({'class:' + k: v for k, v in actual.items()})
    ctx.hashes['compile_receipt'] = sha256(receipt)
    ctx.runtime['classes'] = str(checked_path(BUILD / 'classes'))


def emitter_command(ctx, stage):
    return [str(Path(ctx.runtime['java_home']) / 'bin/java.exe'), '-Xmx' + str(ctx.limits.java_heap_mib) + 'm',
            '-cp', os.pathsep.join([ctx.runtime['classes'], *ctx.runtime['jars']]), 'TelemetryEmitter',
            '--input', str(ctx.spec.input), '--match-id', str(ctx.spec.match_id), '--account-id', str(ctx.spec.account_id),
            '--schema', str(BASE / 'notes/dem-schema-v1.json'), '--staging', str(stage), '--limits-json', str(stage / 'limits.json')]


def promote_no_replace(staging: Path, output: Path) -> None:
    staging, output = checked_path(staging), checked_path(output, may_not_exist=True)
    if output.exists(): raise DemImportError(5, 'destination_exists')
    if os.name != 'nt': raise DemImportError(5, 'atomic_promotion_requires_windows')
    fn = ctypes.WinDLL('kernel32', use_last_error=True).MoveFileExW
    fn.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]; fn.restype = ctypes.c_int
    if not fn(str(staging), str(output), 0): raise DemImportError(5, 'promotion_failed:' + str(ctypes.get_last_error()))


def iter_rows(path, limits):
    checked_path(path)
    with path.open('rb') as f:
        while True:
            line = f.readline(limits.max_line_bytes + 1)
            if not line: break
            if len(line) > limits.max_line_bytes: raise DemImportError(6, 'line_limit')
            if not line.endswith(b'\n'): raise DemImportError(4, 'truncated_jsonl')
            try:
                row = json.loads(line, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
            except (ValueError, UnicodeError) as exc: raise DemImportError(4, 'invalid_jsonl') from exc
            if not isinstance(row, dict): raise DemImportError(4, 'record_object_required')
            yield row


def validate_streams(stage, ctx):
    counts = {}; hashes = {}
    calibration = calibration_reference(ctx)
    expected_points = {p['demo_tick']:p['hud'] for p in calibration['points']}
    found_points = set()
    for stream in STREAMS:
        p = stage / (stream + '.jsonl'); count = 0; last_tick = -1
        for r in iter_rows(p, ctx.limits):
            if r.get('seq') != count or type(r.get('seq')) is not int: raise DemImportError(4, 'sequence:' + stream)
            tick = r.get('demo_tick') if stream != 'gaps' else r.get('start_demo_tick')
            if type(tick) is not int or tick < last_tick: raise DemImportError(4, 'tick_order:' + stream)
            last_tick = tick; count += 1
            if count > (ctx.limits.max_events if stream == 'events' else ctx.limits.max_states * (2 if stream == 'gaps' else 1)):
                raise DemImportError(6, 'record_limit:' + stream)
            if stream == 'states':
                try:
                    actor = r['actor']; resources = r['resources']; clock = r['clock']
                    if type(actor['account32']) is not int or actor['account32'] != ctx.spec.account_id:
                        raise DemImportError(3, 'output_actor_mismatch')
                    steam = uint64_decimal(actor['steam64'])
                    if not isinstance(actor['steam64'], str) or int(steam) & 0xffffffff != ctx.spec.account_id:
                        raise DemImportError(3, 'output_steam_mismatch')
                    if r.get('knowledge_scope') != 'spectator_research': raise DemImportError(4, 'knowledge_scope')
                    for key in ['hp', 'max_hp', 'mana', 'max_mana']:
                        v = resources[key]
                        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v): raise DemImportError(4, 'nonfinite_resources')
                        if key in ['hp', 'max_hp'] and (type(v) is not int or not -2**31 <= v < 2**31): raise DemImportError(4, 'resource_int32')
                    for key in ['full_handle', 'index', 'serial']:
                        if type(actor[key]) is not int or actor[key] < 0: raise DemImportError(4, 'actor_reference')
                    seconds = clock['game_seconds']
                    if seconds is not None and (type(seconds) not in (int, float) or not math.isfinite(seconds)):
                        raise DemImportError(4, 'nonfinite_clock')
                    if r.get('raw_state64') is not None: uint64_decimal(r['raw_state64'])
                    if tick in expected_points:
                        hud = expected_points[tick]
                        if any(abs(resources[k]-hud[k])>1 for k in ['hp','max_hp','mana','max_mana']) or seconds is None or math.floor(seconds) != hud['clock_seconds']:
                            raise DemImportError(4, 'native_calibration_mismatch')
                        found_points.add(tick)
                except (KeyError, TypeError) as exc: raise DemImportError(4, 'state_schema') from exc
            elif stream == 'events':
                if r.get('knowledge_scope') != 'spectator_research' or r.get('actor_link') not in ['candidate_name_only', 'unresolved', 'full_reference']:
                    raise DemImportError(4, 'event_schema')
                if r.get('actor_link') == 'full_reference' and r.get('full_entity_reference') is None:
                    raise DemImportError(4, 'event_identity_unproven')
            else:
                if type(r.get('end_demo_tick')) is not int or r['end_demo_tick'] < tick or not isinstance(r.get('reason'), str):
                    raise DemImportError(4, 'gap_schema')
        counts[stream] = count; hashes[p.name] = sha256(p)
    if not counts['states']: raise DemImportError(3, 'no_actor_states')
    if found_points != set(expected_points): raise DemImportError(4, 'native_calibration_point_missing')
    return counts, hashes


def verify_cache(path: Path, context):
    if not path.exists(): return None
    try:
        checked_path(path)
        receipt = read_json(checked_path(path / 'receipt.json'))
        claimed_digest = receipt.get('receipt_digest')
        content = {k:v for k,v in receipt.items() if k != 'receipt_digest'}
        if claimed_digest != hashlib.sha256(canonical_json(content)).hexdigest():
            raise DemImportError(5, 'cache_receipt_digest')
        if receipt.get('completed') is not True or receipt.get('cache_key') != cache_key(context):
            raise DemImportError(5, 'cache_key_or_completion_mismatch')
        hashes = receipt['data_hashes']
        allowed = {'states.jsonl', 'events.jsonl', 'gaps.jsonl', 'episodes.json', 'windows.jsonl'}
        if not isinstance(hashes, dict) or not set(hashes) <= allowed or not {'states.jsonl','events.jsonl','gaps.jsonl'} <= set(hashes):
            raise DemImportError(5, 'cache_artifact_names')
        if {p.name for p in path.iterdir()} != set(hashes) | {'receipt.json'}: raise DemImportError(5, 'cache_membership')
        for name, expected in hashes.items():
            p = checked_path(path / name)
            if not p.is_file() or sha256(p) != expected: raise DemImportError(5, 'cache_tampered:' + name)
        if receipt.get('provenance') != context.hashes or receipt.get('match_id') != str(context.spec.match_id) or receipt.get('account_id') != context.spec.account_id:
            raise DemImportError(5, 'cache_provenance')
        counts, stream_hashes = validate_streams(path, context)
        if receipt.get('counts') != counts or any(hashes.get(k) != v for k, v in stream_hashes.items()):
            raise DemImportError(5, 'cache_counts')
        summary = receipt.get('parser_summary',{})
        if summary.get('eof') is not True or summary.get('match_id') != str(context.spec.match_id) or summary.get('account_id') != context.spec.account_id or any(summary.get(k) != v for k,v in counts.items()):
            raise DemImportError(5, 'cache_eof_summary')
        if receipt.get('calibration') != calibration_reference(context): raise DemImportError(5, 'cache_calibration_scope')
        if 'episodes.json' not in hashes or receipt.get('capabilities',{}).get('episode_index') is not True:
            raise DemImportError(5, 'cache_episode_index')
        if any(receipt.get(k) is not False for k in ['model_trained','player_fidelity_verified','perception_export_allowed','native_verified']):
            raise DemImportError(5, 'cache_scope')
        return ImportResult('cache_hit', receipt['cache_key'], receipt['counts'], hashes, str(path))
    except DemImportError as exc: raise DemImportError(5, 'invalid_cache:' + exc.reason) from exc
    except (OSError, KeyError, TypeError) as exc: raise DemImportError(5, 'invalid_cache') from exc


def run_child(command, stage, limits):
    overflow = threading.Event()
    environment = {k:v for k,v in os.environ.items() if k.upper() not in {'JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH'}}
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, env=environment)
    def drain(pipe, name):
        total = 0
        try:
            with (stage / name).open('xb') as f:
                while True:
                    chunk = pipe.read(65536)
                    if not chunk: break
                    remaining = max(0, limits.max_stderr_bytes - total)
                    f.write(chunk[:remaining]); total += len(chunk)
                    if total > limits.max_stderr_bytes:
                        overflow.set()
                        try: process.kill()
                        except OSError: pass
                        break
        finally: pipe.close()
    threads = [threading.Thread(target=drain, args=(pipe, name), daemon=True)
               for pipe, name in [(process.stdout, 'stdout.log'), (process.stderr, 'stderr.log')]]
    for t in threads: t.start()
    start = time.monotonic(); error = None
    try:
        while process.poll() is None:
            if overflow.is_set(): error = 'diagnostic_limit'; break
            if time.monotonic() - start > limits.timeout_seconds: error = 'timeout'; break
            total = sum(p.stat().st_size for p in stage.iterdir() if p.is_file())
            if total > limits.max_output_bytes: error = 'output_limit'; break
            time.sleep(0.05)
    finally:
        if process.poll() is None: process.kill()
        process.wait()
        for t in threads: t.join(timeout=5)
    if error or overflow.is_set(): raise DemImportError(6, error or 'diagnostic_limit')
    if any(t.is_alive() for t in threads): raise DemImportError(5, 'pipe_reader_not_closed')
    if process.returncode != 0:
        raise DemImportError(process.returncode if process.returncode in [2,3,4,5,6] else 5, 'emitter_exit:' + str(process.returncode))
    if sum(p.stat().st_size for p in stage.iterdir() if p.is_file()) > limits.max_output_bytes:
        raise DemImportError(6, 'output_limit')


def assert_unchanged(ctx):
    fresh = validate_inputs(ctx.spec)
    for key, actual in fresh.hashes.items():
        if ctx.hashes.get(key) != actual: raise DemImportError(5, 'input_changed:' + key)
    for name in [k[6:] for k in ctx.hashes if k.startswith('class:')]:
        if sha256(checked_path(BUILD / 'classes' / name)) != ctx.hashes['class:' + name]:
            raise DemImportError(5, 'class_changed')


def run_import(context):
    ctx = context; prepare_runtime(ctx)
    cached = verify_cache(ctx.spec.output, ctx)
    if cached: return cached
    output = checked_path(ctx.spec.output, may_not_exist=True)
    token = uuid.uuid4().hex
    lock = output.parent / ('.' + output.name + '.lock')
    stage = output.parent / ('.' + output.name + '.staging-' + token)
    owned_lock = False; staged = False
    try:
        try:
            with lock.open('x', encoding='utf-8') as f: f.write(token)
            owned_lock = True
        except FileExistsError as exc: raise DemImportError(5, 'output_locked') from exc
        stage.mkdir(); staged = True
        (stage / 'owner.json').write_bytes(canonical_json({'token': token}))
        lim = dataclasses.asdict(ctx.limits); lim['fields'] = ctx.config['fields']
        (stage / 'limits.json').write_bytes(canonical_json(lim))
        run_child(emitter_command(ctx, stage), stage, ctx.limits)
        summary = read_json(checked_path(stage / 'emitter-summary.json'))
        if summary.get('eof') is not True or summary.get('match_id') != str(ctx.spec.match_id) or summary.get('account_id') != ctx.spec.account_id:
            raise DemImportError(4, 'invalid_eof_summary')
        counts, hashes = validate_streams(stage, ctx)
        if any(summary.get(k) != v for k, v in counts.items()): raise DemImportError(4, 'summary_count_mismatch')
        if summary.get('states',0) + summary.get('unassigned',0) != summary.get('real_ticks'):
            raise DemImportError(4, 'real_tick_count_mismatch')
        episode = build_episodes(iter_rows(stage/'states.jsonl',ctx.limits),iter_rows(stage/'events.jsonl',ctx.limits),
                                 iter_rows(stage/'gaps.jsonl',ctx.limits),ctx.config['episode_windows'],stage,ctx.limits)
        hashes.update(episode.data_hashes)
        assert_unchanged(ctx)
        receipt = {'schema':'dem-import-receipt-v1','completed':True,'cache_key':cache_key(ctx), 'match_id':str(ctx.spec.match_id),
                   'account_id':ctx.spec.account_id, 'provenance':ctx.hashes,'counts':counts, 'parser_summary':summary,'data_hashes':hashes,
                   'episode_index':{'entries':episode.index_count,'window_records':episode.window_record_count},
                   'calibration':calibration_reference(ctx),
                   'capabilities':{'actor_resources':True,'episode_index':True,'verified_actor_events':False,'actual_pause_verified':False},
                   'model_trained':False,'player_fidelity_verified':False,'perception_export_allowed':False,'native_verified':False}
        # Preserve internal diagnostics separately; final output contains only declared data + receipt.
        diagnostics = output.parent / ('.' + output.name + '.diagnostics-' + token)
        diagnostics.mkdir()
        for p in list(stage.iterdir()):
            if p.name not in hashes:
                checked_path(p); p.rename(diagnostics / p.name)
        receipt['receipt_digest'] = hashlib.sha256(canonical_json(receipt)).hexdigest()
        (stage / 'receipt.json').write_bytes(canonical_json(receipt))
        if sum(p.stat().st_size for folder in [stage, diagnostics] for p in folder.iterdir() if p.is_file()) > ctx.limits.max_output_bytes:
            raise DemImportError(6, 'receipt_output_limit')
        checked_path(output, may_not_exist=True); checked_path(stage)
        promote_no_replace(stage, output); staged = False
        return ImportResult('imported',receipt['cache_key'],counts,hashes,str(output))
    except DemImportError:
        raise
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise DemImportError(5, 'import_io:' + str(exc)) from exc
    finally:
        if staged:
            # Do not recursively delete anything. Rename only our original, non-reparse staging.
            try:
                checked_path(stage)
                stage.rename(output.parent / ('.' + output.name + '.failed-' + token))
            except (OSError, DemImportError): pass
        if owned_lock:
            try:
                checked_path(lock)
                if lock.read_text(encoding='utf-8') == token: lock.unlink()
            except (OSError, DemImportError): pass
