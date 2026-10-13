"""Explicit local decoder pilot on three synthetic WAVs; inert on import.

Metrics lowercase Latin/Cyrillic words, discard punctuation, and map ё to е.
This never captures audio, downloads dependencies, or sends commands.
"""
import argparse
import datetime
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import re
import socket
import stat
import sys
import time
import uuid
import wave

REPOSITORY = Path(__file__).resolve().parents[5]
REFERENCES = ['Игрок два, отойди назад.', 'Игрок один, атакуй цель.', 'Команда, соберитесь вместе.']
AUDIO_FORMAT = {'sample_rate': 16000, 'sample_width_bytes': 2, 'channels': 1, 'encoding': 'PCM'}
MODEL_REVISION = 'd90ca5fe260221311c53c58e660288d3deb8d356'
MODEL_FILES = {
    'config.json': (2249, 'a73a28cdfe1c43ccc7202fa333d1f89c202477271407ae9a7f19afa52039cac8'),
    'model.bin': (75538270, 'dcb76c6586fc06cbdac6dd21f14cfd129cc4cdd9dce19bf4ffa62e59cbe6e6d1'),
    'tokenizer.json': (2203239, 'fb7b63191e9bb045082c79fd742a3106a12c99513ab30df4a0d47fa6cb6fd0ab'),
    'vocabulary.txt': (459861, '34ce3fe1c5041027b3f8d42912270993f986dbc4bb34cf27f951e34a1e453913'),
}
EXPECTED_VERSIONS = {'faster-whisper': '1.2.1', 'ctranslate2': '4.8.2',
                     'onnxruntime': '1.31.0', 'av': '18.0.0', 'numpy': '2.5.4',
                     'huggingface-hub': '2.2.0', 'tokenizers': '0.23.3'}


def checked_path(path, repository):
    root = Path(os.path.abspath(repository))
    actual = Path(os.path.abspath(path if Path(path).is_absolute() else root / path))
    try:
        relative = actual.relative_to(root)
    except ValueError as error:
        raise ValueError('Synthetic path escapes the repository') from error
    for candidate in [root] + [root.joinpath(*relative.parts[:n]) for n in range(1, len(relative.parts) + 1)]:
        try:
            info = candidate.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Synthetic paths refuse links/reparse points')
    return actual


def read_local(path, repository, limit):
    actual = checked_path(path, repository)
    if not actual.is_file():
        raise ValueError('Required local input is not a file')
    with actual.open('rb') as stream:
        payload = stream.read(limit + 1)
    if len(payload) > limit:
        raise ValueError('Local input exceeds its bounded size')
    return payload


def validate_receipt(path, repository=REPOSITORY):
    root = Path(os.path.abspath(repository))
    actual = checked_path(path, root)
    boundary = root / 'build/dota_coach'
    if (actual.name != 'tts-receipt.json' or actual.parent.parent != boundary or
            re.fullmatch(r'asr-synthetic-20261013-[0-9a-f]{32}', actual.parent.name) is None):
        raise ValueError('Receipt must belong to a direct owned synthetic directory')
    raw = read_local(actual, root, 1024 * 1024)
    receipt = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(receipt, dict):
        raise ValueError('Synthetic receipt must be an object')
    expected = {'stage': 'synthetic_tts', 'source': 'synthetic_system_tts',
                'voice_name': 'Microsoft Irina Desktop', 'voice_culture': 'ru-RU'}
    if (any(receipt.get(key) != value for key, value in expected.items()) or
            receipt.get('tts_completed') is not True or receipt.get('error', 'missing') is not None):
        raise ValueError('Only completed exact Irina synthetic receipts are accepted')
    if 'schema_version' in receipt and (type(receipt['schema_version']) is not int or receipt['schema_version'] != 1):
        raise ValueError('Unexpected synthetic receipt schema version')
    format_header = receipt.get('audio_format')
    if (format_header != AUDIO_FORMAT or not isinstance(format_header, dict) or
            any(type(format_header[key]) is not type(value) for key, value in AUDIO_FORMAT.items())):
        raise ValueError('Synthetic receipt requires 16000 Hz 16-bit mono PCM')
    if 'references' in receipt and receipt['references'] != REFERENCES:
        raise ValueError('Synthetic reference list changed')
    samples = receipt.get('samples')
    if not isinstance(samples, list) or len(samples) != 3:
        raise ValueError('Exactly three synthetic samples are required')
    validated = []
    for index, (sample, reference) in enumerate(zip(samples, REFERENCES), 1):
        name = f'sample-{index:02d}.wav'
        if (not isinstance(sample, dict) or set(sample) != {'name', 'reference', 'bytes', 'sha256'} or
                sample['name'] != name or sample['reference'] != reference or
                type(sample['bytes']) is not int or not 44 < sample['bytes'] <= 5 * 1024 * 1024 or
                not isinstance(sample['sha256'], str) or re.fullmatch(r'[0-9a-f]{64}', sample['sha256']) is None):
            raise ValueError('Synthetic sample fields/reference/coverage changed')
        audio_path = checked_path(actual.parent / name, root)
        payload = read_local(audio_path, root, 5 * 1024 * 1024)
        if len(payload) != sample['bytes'] or hashlib.sha256(payload).hexdigest() != sample['sha256']:
            raise ValueError('Synthetic WAV size/hash changed')
        try:
            with wave.open(io.BytesIO(payload), 'rb') as audio:
                frames = audio.getnframes()
                if (audio.getframerate() != 16000 or audio.getnchannels() != 1 or audio.getsampwidth() != 2 or
                        audio.getcomptype() != 'NONE' or not 0 < frames <= 16000 * 30 or
                        len(audio.readframes(frames)) != frames * 2):
                    raise ValueError('Synthetic WAV is not bounded complete 16 kHz mono PCM16')
        except (wave.Error, EOFError) as error:
            raise ValueError('Malformed synthetic WAV') from error
        validated.append({**sample, 'path': audio_path, 'pcm': {'sample_rate': 16000,
                          'sample_width_bytes': 2, 'channels': 1, 'frames': frames,
                          'duration_seconds': frames / 16000}})
    return {**receipt, 'receipt_path': actual, 'directory': actual.parent,
            'receipt_sha256': hashlib.sha256(raw).hexdigest(), 'samples': validated}


def validate_model(repository=REPOSITORY):
    root = Path(os.path.abspath(repository))
    base = checked_path(root / 'build/dota_coach/asr-pilot-20261012', root)
    receipt = json.loads(read_local(base / 'model-download.json', root, 1024 * 1024).decode('utf-8-sig'))
    if not isinstance(receipt, dict) or receipt.get('revision') != MODEL_REVISION:
        raise ValueError('Unexpected pinned model revision')
    records = []
    for name, (size, expected_hash) in MODEL_FILES.items():
        payload = read_local(base / 'model' / name, root, size)
        actual_hash = hashlib.sha256(payload).hexdigest()
        if len(payload) != size or actual_hash != expected_hash:
            raise ValueError('Pinned model file size/hash changed: ' + name)
        records.append({'name': name, 'bytes': size, 'sha256': actual_hash})
    for name in ['deps', 'deps-av18', 'model', 'hf-cache']:
        checked_path(base / name, root)
    return {'revision': MODEL_REVISION, 'model_directory': base / 'model', 'model_files': records}


def normalize_words(text):
    if not isinstance(text, str):
        raise ValueError('Metric text must be a string')
    return re.findall(r'[a-zа-я0-9]+', text.lower().replace('ё', 'е'))


def edit_distance(reference_words, hypothesis_words):
    previous = list(range(len(hypothesis_words) + 1))
    for row, expected in enumerate(reference_words, 1):
        current = [row]
        for column, actual in enumerate(hypothesis_words, 1):
            current.append(min(current[-1] + 1, previous[column] + 1,
                               previous[column - 1] + (expected != actual)))
        previous = current
    return previous[-1]


def compare_words(reference, hypothesis):
    expected, actual = normalize_words(reference), normalize_words(hypothesis)
    if not expected:
        raise ValueError('Normalized reference must contain words')
    distance = edit_distance(expected, actual)
    return {'reference_words': expected, 'hypothesis_words': actual,
            'edit_distance': distance, 'wer': distance / len(expected)}


def fresh_output(parent, repository, prefix):
    destination = checked_path(parent / (prefix + uuid.uuid4().hex), repository)
    destination.mkdir(parents=True, exist_ok=False)
    return destination


def run_pilot(receipt_path, repository=REPOSITORY):
    root = Path(os.path.abspath(repository))
    started, cpu_started = time.perf_counter(), time.process_time()
    result = {'schema_version': 1, 'stage': 'synthetic_local_decoder_pilot',
              'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'source': 'synthetic_system_tts', 'references': REFERENCES,
              'language_requested': 'ru', 'device': 'cpu', 'compute_type': 'int8', 'cpu_threads': 2,
              'beam_size': 1, 'vad_filter': True, 'preflight_completed': False, 'model_loaded': False,
              'samples': [], 'aggregate': None, 'synthetic_decoder_positive': False,
              'speech_verified': False, 'accuracy_verified': False, 'dota_bridge_verified': False,
              'commands_sent': 0, 'microphone_used': False, 'speakers_used': False,
              'python_socket_attempts': [], 'native_network_monitored': False, 'error': None}
    output = None
    old_path = list(sys.path)
    previous_sockets = {}
    environment = {}
    try:
        receipt = validate_receipt(receipt_path, root)
        output = fresh_output(receipt['directory'], root, 'decoder-')
        model = validate_model(root)
        result['receipt_path'] = str(receipt['receipt_path'])
        result['receipt_sha256'] = receipt['receipt_sha256']
        result['voice_name'] = receipt['voice_name']
        result['model_revision'] = model['revision']
        result['model_files'] = model['model_files']
        result['preflight_completed'] = True
        base = root / 'build/dota_coach/asr-pilot-20261012'
        for key, value in {'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
                           'HF_HUB_DISABLE_TELEMETRY': '1', 'HF_HOME': str(base / 'hf-cache')}.items():
            environment[key] = os.environ.get(key)
            os.environ[key] = value
        for owner, name in [(socket.socket, 'connect'), (socket.socket, 'connect_ex'),
                            (socket, 'create_connection'), (socket, 'getaddrinfo')]:
            previous_sockets[(owner, name)] = getattr(owner, name)
            def denied(*args, _name=name, **kwargs):
                result['python_socket_attempts'].append(_name)
                raise RuntimeError('Python socket access disabled for synthetic local inference')
            setattr(owner, name, denied)
        sys.path[:0] = [str(base / 'deps-av18'), str(base / 'deps')]
        versions = {name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS}
        if versions != EXPECTED_VERSIONS:
            raise ValueError('Local dependency versions differ from the pinned pilot')
        result['versions'] = versions
        from faster_whisper import WhisperModel
        import av
        import faster_whisper
        if not Path(av.__file__).resolve().is_relative_to((base / 'deps-av18').resolve()):
            raise ValueError('PyAV did not load from the pinned av18 overlay')
        if not Path(faster_whisper.__file__).resolve().is_relative_to((base / 'deps').resolve()):
            raise ValueError('faster-whisper did not load from the local pilot')
        result['module_paths'] = {'av': av.__file__, 'faster_whisper': faster_whisper.__file__}
        load_started = time.perf_counter()
        decoder = WhisperModel(str(model['model_directory']), device='cpu', compute_type='int8',
                               cpu_threads=2, num_workers=1, local_files_only=True)
        result['model_loaded'] = True
        result['model_load_seconds'] = round(time.perf_counter() - load_started, 6)
        for sample in receipt['samples']:
            measured = {'name': sample['name'], 'reference': sample['reference'], 'sha256': sample['sha256'],
                        'pcm': sample['pcm'], 'segments': [], 'generator_consumed': False,
                        'decoder_exercised': False, 'comparison': None, 'error': None}
            result['samples'].append(measured)
            sample_started = time.perf_counter()
            try:
                # Recheck the owned WAV immediately before giving its path to the decoder.
                payload = read_local(sample['path'], root, 5 * 1024 * 1024)
                if hashlib.sha256(payload).hexdigest() != sample['sha256']:
                    raise ValueError('Synthetic WAV changed after preflight')
                segments, info = decoder.transcribe(str(sample['path']), language='ru', beam_size=1,
                                                     vad_filter=True, condition_on_previous_text=False)
                for segment in segments:
                    measured['segments'].append({'start': segment.start, 'end': segment.end, 'text': segment.text,
                                                  'avg_logprob': segment.avg_logprob, 'no_speech_prob': segment.no_speech_prob})
                measured['generator_consumed'] = True
                measured['input_duration_seconds'] = info.duration
                measured['duration_after_vad_seconds'] = info.duration_after_vad
                measured['decoder_exercised'] = bool(info.duration_after_vad > 0)
                hypothesis = ' '.join(segment['text'] for segment in measured['segments'])
                measured['comparison'] = compare_words(sample['reference'], hypothesis)
                measured['exact_reference_match'] = measured['comparison']['edit_distance'] == 0
            except Exception as error:
                measured['error'] = type(error).__name__ + ': ' + str(error)
            measured['elapsed_seconds'] = round(time.perf_counter() - sample_started, 6)
        if all(sample['comparison'] is not None and sample['error'] is None for sample in result['samples']):
            count = sum(len(sample['comparison']['reference_words']) for sample in result['samples'])
            edits = sum(sample['comparison']['edit_distance'] for sample in result['samples'])
            result['aggregate'] = {'samples': 3, 'reference_words': count, 'edit_distance': edits,
                                   'wer': edits / count, 'scope': 'only_three_synthetic_references'}
        else:
            result['error'] = 'At least one synthetic sample failed'
        result['synthetic_decoder_positive'] = bool(len(result['samples']) == 3 and all(
            sample['generator_consumed'] and sample['decoder_exercised'] and sample['error'] is None and
            sample['comparison'] is not None and sample['comparison']['hypothesis_words']
            for sample in result['samples']) and not result['python_socket_attempts'])
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        for (owner, name), original in previous_sockets.items():
            setattr(owner, name, original)
        for key, value in environment.items():
            if value is None: os.environ.pop(key, None)
            else: os.environ[key] = value
        sys.path[:] = old_path
    result['elapsed_seconds'] = round(time.perf_counter() - started, 6)
    result['process_cpu_seconds'] = round(time.process_time() - cpu_started, 6)
    if output is None:
        output = fresh_output(root / 'build/dota_coach', root, 'asr-synthetic-refusal-20261013-')
    result_path = checked_path(output / 'asr-result.json', root)
    with result_path.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    return result_path, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    path, result = run_pilot(args.receipt)
    print(json.dumps({'report': str(path), 'synthetic_decoder_positive': result['synthetic_decoder_positive'],
                      'aggregate': result['aggregate'], 'error': result['error'], 'commands_sent': 0}, ensure_ascii=False))
    return 0 if result['error'] is None and result['synthetic_decoder_positive'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
