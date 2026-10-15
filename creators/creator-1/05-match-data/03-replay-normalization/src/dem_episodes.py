"""Deterministic research index. No inferred commands, intent or enum labels."""
import heapq
import time
from dem_types import DemImportError, EpisodeResult, canonical_json
from dem_inputs import sha256

ORDINARY_CONTROL_STEP_DEMO_TICKS = 900


def build_episodes(states, events, gaps, windows, output_dir, limits):
    ids = [w['id'] for w in windows]
    if len(ids) != len(set(ids)) or len(ids) > limits.max_windows: raise DemImportError(2, 'duplicate_or_excess_windows')
    for w in windows:
        if not 0 <= w['start_demo_tick'] <= w['end_demo_tick']: raise DemImportError(2, 'window_interval')
    ordered = sorted(windows, key=lambda w: (w['start_demo_tick'], w['id']))
    def tagged(stream, rows):
        for row in rows:
            yield (row['start_demo_tick'] if stream == 'gaps' else row['demo_tick'], stream, row['seq'], row)
    merged = heapq.merge(tagged('states',states), tagged('events',events), tagged('gaps',gaps), key=lambda x:x[:3])
    entries = []; index_bytes = 0; window_bytes = 0; window_count = 0; next_control = None
    signature = None; pending_gap = None; cursor = 0; active = []
    base_bytes = sum(p.stat().st_size for p in output_dir.iterdir() if p.is_file())
    deadline = time.monotonic() + limits.timeout_seconds
    def add(entry):
        nonlocal index_bytes
        if len(entries) >= limits.max_index_entries: raise DemImportError(6, 'index_entry_limit')
        index_bytes += len(canonical_json(entry))
        if base_bytes + index_bytes + window_bytes + 512 > limits.max_output_bytes: raise DemImportError(6, 'index_byte_limit')
        entries.append(entry)
    writer = (output_dir/'windows.jsonl').open('xb') if windows else None
    try:
        for tick,stream,seq,row in merged:
            if time.monotonic() > deadline: raise DemImportError(6, 'episode_timeout')
            while cursor < len(ordered) and ordered[cursor]['start_demo_tick'] <= tick:
                active.append(ordered[cursor]); cursor += 1
            active = [w for w in active if w['end_demo_tick'] >= tick]
            matching = sorted(w['id'] for w in active)
            if writer and matching:
                line = canonical_json({'stream':stream,'seq':seq,'window_ids':matching,'record':row})
                if len(line)>limits.max_line_bytes: raise DemImportError(6, 'window_line_limit')
                window_bytes += len(line)
                if base_bytes+index_bytes+window_bytes+512>limits.max_output_bytes: raise DemImportError(6, 'window_byte_limit')
                writer.write(line); window_count += 1
            if stream == 'gaps':
                key = (row.get('reason'), row.get('binding_epoch'))
                if pending_gap and pending_gap['_key'] != key:
                    pending_gap.pop('_key'); add(pending_gap); pending_gap = None
                if pending_gap:
                    pending_gap['end_demo_tick'] = row['end_demo_tick']; pending_gap['sample_count'] += 1
                else:
                    pending_gap = {'kind':'gap_samples','demo_tick':tick,'end_demo_tick':row['end_demo_tick'],
                                   'reason':row['reason'],'binding_epoch':row.get('binding_epoch'),'sample_count':1,'_key':key}
            elif stream == 'states':
                if pending_gap and (pending_gap['reason'] != 'clock_unknown' or row['clock']['game_seconds'] is not None):
                    pending_gap.pop('_key'); add(pending_gap); pending_gap = None
                current = (row['binding_epoch'],row['clock_epoch'],row.get('raw_life_state'),row.get('raw_state64'))
                if current != signature:
                    add({'kind':'raw_state_change','demo_tick':tick,'state_seq':seq,'binding_epoch':row['binding_epoch'],
                         'clock_epoch':row['clock_epoch'],'life_state_raw':row.get('raw_life_state'),'state64_raw':row.get('raw_state64'),
                         'semantics_verified':False})
                    signature = current
                if next_control is None or tick >= next_control:
                    add({'kind':'ordinary_control_sample','demo_tick':tick,'state_seq':seq,'game_seconds':row['clock']['game_seconds']})
                    next_control = tick + ORDINARY_CONTROL_STEP_DEMO_TICKS
            elif row.get('type') in ['DOTA_COMBATLOG_DEATH','DOTA_COMBATLOG_MODIFIER_ADD','DOTA_COMBATLOG_MODIFIER_REMOVE']:
                add({'kind':'named_event_candidate','demo_tick':tick,'event_seq':seq,'type':row['type'],
                     'target':row.get('target'),'inflictor':row.get('inflictor'),'actor_link':row.get('actor_link','unresolved')})
        if pending_gap:
            pending_gap.pop('_key'); add(pending_gap)
    finally:
        if writer: writer.close()
    entries.sort(key=lambda e:(e['demo_tick'], e['kind'], e.get('state_seq',e.get('event_seq',-1))))
    path = output_dir/'episodes.json'
    data = canonical_json({'schema':'dem-episode-index-v1','ordinary_control_step_demo_ticks':ORDINARY_CONTROL_STEP_DEMO_TICKS,
                           'knowledge_scope':'spectator_research','interpolation':False,'entries':entries})
    if base_bytes+len(data)+window_bytes > limits.max_output_bytes: raise DemImportError(6, 'episode_byte_limit')
    with path.open('xb') as f: f.write(data)
    hashes = {path.name:sha256(path)}
    if windows: hashes['windows.jsonl'] = sha256(output_dir/'windows.jsonl')
    return EpisodeResult(len(entries),window_count,hashes)
