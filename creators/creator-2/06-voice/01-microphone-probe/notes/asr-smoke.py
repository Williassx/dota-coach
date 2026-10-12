"""Local runtime/VAD experiment on the existing approved three-second clip.

Never captures audio, sends commands, or downloads a model. Not an ordinary test.
"""
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import sys
import time
import uuid


def main():
    repo = Path(__file__).resolve().parents[5]
    base = repo / 'build' / 'dota_coach' / 'asr-pilot-20261012'
    base.resolve().relative_to(repo)
    for path in (repo / 'build', base.parent, base, base / 'deps',
                 base / 'deps-av18', base / 'model'):
        if path.is_symlink() or path.is_junction():
            raise RuntimeError('Redirected experiment directory')
    output = base / ('run-' + uuid.uuid4().hex[:6])
    output.mkdir()
    receipt = json.loads((base / 'model-download.json').read_text(encoding='utf-8'))
    if receipt['revision'] != 'd90ca5fe260221311c53c58e660288d3deb8d356':
        raise RuntimeError('Unexpected model revision')
    for asset in receipt['model_files']:
        if asset['name'] not in ('config.json', 'model.bin', 'tokenizer.json', 'vocabulary.txt'):
            raise RuntimeError('Unexpected model file')
        actual = base / 'model' / asset['name']
        if actual.is_symlink() or actual.is_junction():
            raise RuntimeError('Redirected model file')
        if hashlib.sha256(actual.read_bytes()).hexdigest() != asset['sha256']:
            raise RuntimeError('Model bytes changed')
    audio = repo / 'build/dota_coach/microphone-20261012T160121Z-93f38d/capture.wav'
    audio_hash = hashlib.sha256(audio.read_bytes()).hexdigest()
    if audio_hash != '94ab5c110254af6692377fe983120b3b1cf6319e4526875f9c875d62d6bf9b0e':
        raise RuntimeError('Approved audio changed')
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                      HF_HUB_DISABLE_TELEMETRY='1',
                      HF_HOME=str(base / 'hf-cache'))
    attempts = []

    def deny_network(*args, **kwargs):
        attempts.append('python_socket_operation')
        raise RuntimeError('Python socket access disabled for local inference')

    # Defense and observation at the Python socket layer, not an OS firewall.
    socket.socket.connect = deny_network
    socket.socket.connect_ex = deny_network
    socket.create_connection = deny_network
    socket.getaddrinfo = deny_network
    sys.path.insert(0, str(base / 'deps'))
    # Preserve the failed PyAV19 environment; load the explicitly pinned overlay.
    sys.path.insert(0, str(base / 'deps-av18'))
    result = {'stage': 'local_model_and_vad_smoke', 'schema_version': 1,
              'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'model_revision': receipt['revision'], 'audio_sha256': audio_hash,
              'language_requested': 'ru', 'device': 'cpu', 'compute_type': 'int8',
              'cpu_threads': 2, 'beam_size': 1, 'vad_filter': True,
              'model_loaded': False, 'generator_consumed': False,
              'segments': [], 'speech_verified': False, 'accuracy_verified': False,
              'dota_bridge_verified': False, 'commands_sent': 0,
              'python_socket_attempts': attempts, 'native_network_monitored': False,
              'error': None}
    started, cpu_started = time.perf_counter(), time.process_time()
    try:
        from faster_whisper import WhisperModel
        import ctranslate2
        result['versions'] = {name: importlib.metadata.version(name) for name in receipt['versions']}
        result['cpu_compute_types'] = sorted(ctranslate2.get_supported_compute_types('cpu'))
        model_started = time.perf_counter()
        model = WhisperModel(str(base / 'model'), device='cpu', compute_type='int8',
                             cpu_threads=2, num_workers=1, local_files_only=True)
        result['model_loaded'] = True
        result['model_load_seconds'] = round(time.perf_counter() - model_started, 6)
        inference_started = time.perf_counter()
        segments, info = model.transcribe(str(audio), language='ru', beam_size=1,
                                         vad_filter=True, condition_on_previous_text=False)
        # The generator must be consumed before reporting a completed experiment.
        result['segments'] = [{'start': s.start, 'end': s.end, 'text': s.text,
                               'avg_logprob': s.avg_logprob,
                               'no_speech_prob': s.no_speech_prob} for s in segments]
        result['generator_consumed'] = True
        result['input_duration_seconds'] = info.duration
        result['duration_after_vad_seconds'] = info.duration_after_vad
        result['inference_seconds'] = round(time.perf_counter() - inference_started, 6)
        result['decoder_exercised'] = bool(info.duration_after_vad > 0)
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
    result['elapsed_seconds'] = round(time.perf_counter() - started, 6)
    result['process_cpu_seconds'] = round(time.process_time() - cpu_started, 6)
    result_file = output / 'asr-result.json'
    result_file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'report': result_file.relative_to(repo).as_posix(), **result}, ensure_ascii=False))
    return 0 if result['error'] is None and result['generator_consumed'] and not attempts else 1


if __name__ == '__main__':
    sys.exit(main())
