"""One bounded native experiment, not the game's microphone backend.

Records three seconds from explicit FIFINE device 0 into a fresh ignored directory.
No capture on import; run only as an intentionally requested microphone experiment.
"""
import ctypes
from ctypes import wintypes
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import uuid
import wave


class Caps(ctypes.Structure):
    _fields_ = [('mid', wintypes.WORD), ('pid', wintypes.WORD),
                ('version', wintypes.DWORD), ('name', wintypes.WCHAR * 32),
                ('formats', wintypes.DWORD), ('channels', wintypes.WORD),
                ('reserved', wintypes.WORD)]


class Format(ctypes.Structure):
    _pack_ = 2
    _fields_ = [('tag', wintypes.WORD), ('channels', wintypes.WORD),
                ('rate', wintypes.DWORD), ('bytes_per_second', wintypes.DWORD),
                ('align', wintypes.WORD), ('bits', wintypes.WORD),
                ('extra', wintypes.WORD)]


class Header(ctypes.Structure):
    _fields_ = [('data', ctypes.c_void_p), ('length', wintypes.DWORD),
                ('recorded', wintypes.DWORD), ('user', ctypes.c_size_t),
                ('flags', wintypes.DWORD), ('loops', wintypes.DWORD),
                ('next', ctypes.c_void_p), ('reserved', ctypes.c_size_t)]


def write_diagnostics(result, result_file, repo, unsafe_cleanup):
    try:
        result_file.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'report': result_file.relative_to(repo).as_posix(), **result}, ensure_ascii=False), flush=True)
    finally:
        if unsafe_cleanup:
            # Logging failure must not unwind and free a possibly queued buffer.
            # End only this diagnostic process; no fallback into caller cleanup.
            os._exit(1)


def main():
    if sys.platform != 'win32':
        raise RuntimeError('This native experiment requires Windows')
    repo = Path(__file__).resolve().parents[5]
    base = repo / 'build' / 'dota_coach'
    base.resolve().relative_to(repo)
    for parent in (repo / 'build', base):
        if parent.is_symlink() or parent.is_junction():
            raise RuntimeError('Redirected output parent')
    base.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = base / ('microphone-' + stamp + '-' + uuid.uuid4().hex[:6])
    output.mkdir()
    result = {'schema_version': 1, 'stage': 'bounded_native_audio_capture',
              'generated_at_utc': stamp, 'device_index': 0, 'device_name': None,
              'rate': 16000, 'channels': 1, 'sample_bytes': 2,
              'requested_seconds': 3, 'api_results': {}, 'audio_recorded': False,
              'speech_verified': False, 'asr_verified': False,
              'dota_bridge_verified': False, 'network_used_by_probe': False,
              'cleanup_verified': False, 'error': None}
    winmm = ctypes.WinDLL('winmm.dll')
    declarations = {
        'waveInGetDevCapsW': [ctypes.c_size_t, ctypes.POINTER(Caps), wintypes.UINT],
        'waveInOpen': [ctypes.POINTER(ctypes.c_void_p), wintypes.UINT,
                       ctypes.POINTER(Format), ctypes.c_size_t,
                       ctypes.c_size_t, wintypes.DWORD],
        'waveInPrepareHeader': [ctypes.c_void_p, ctypes.POINTER(Header), wintypes.UINT],
        'waveInAddBuffer': [ctypes.c_void_p, ctypes.POINTER(Header), wintypes.UINT],
        'waveInStart': [ctypes.c_void_p], 'waveInReset': [ctypes.c_void_p],
        'waveInUnprepareHeader': [ctypes.c_void_p, ctypes.POINTER(Header), wintypes.UINT],
        'waveInClose': [ctypes.c_void_p],
    }
    for name, arguments in declarations.items():
        function = getattr(winmm, name)
        function.argtypes, function.restype = arguments, wintypes.UINT

    def call(name, *arguments):
        code = int(getattr(winmm, name)(*arguments))
        result['api_results'][name] = code
        if code:
            raise RuntimeError(name + ' returned MMRESULT ' + str(code))

    handle = ctypes.c_void_p()
    buffer = ctypes.create_string_buffer(96000)
    header = Header(ctypes.cast(buffer, ctypes.c_void_p), 96000, 0, 0, 0, 0, None, 0)
    prepared = False
    unsafe_cleanup = False
    started = time.perf_counter()
    cpu_started = time.process_time()
    try:
        caps = Caps()
        call('waveInGetDevCapsW', 0, ctypes.byref(caps), ctypes.sizeof(caps))
        result['device_name'] = caps.name
        if 'fifine' not in caps.name.lower():
            raise RuntimeError('Device 0 changed; explicit FIFINE precondition failed')
        fmt = Format(1, 1, 16000, 32000, 2, 16, 0)
        call('waveInOpen', ctypes.byref(handle), 0, ctypes.byref(fmt), 0, 0, 0)
        call('waveInPrepareHeader', handle, ctypes.byref(header), ctypes.sizeof(header))
        prepared = True
        call('waveInAddBuffer', handle, ctypes.byref(header), ctypes.sizeof(header))
        call('waveInStart', handle)
        deadline = time.perf_counter() + 5
        while not header.flags & 1:
            if time.perf_counter() >= deadline:
                raise TimeoutError('WHDR_DONE not observed within 5 seconds')
            time.sleep(0.02)
        result['bytes_recorded'] = header.recorded
        result['done_observed'] = True
        if header.recorded != 96000:
            raise RuntimeError('Unexpected partial capture')
    except Exception as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
    finally:
        if handle.value:
            # Keep buffer/header alive until reset and unprepare confirm release.
            try:
                call('waveInReset', handle)
                if prepared:
                    call('waveInUnprepareHeader', handle, ctypes.byref(header), ctypes.sizeof(header))
                call('waveInClose', handle)
                result['cleanup_verified'] = True
            except Exception as error:
                unsafe_cleanup = True
                result['cleanup_error'] = type(error).__name__ + ': ' + str(error)
        result['elapsed_seconds'] = round(time.perf_counter() - started, 6)
        result['process_cpu_seconds'] = round(time.process_time() - cpu_started, 6)
    if not result['error'] and result['cleanup_verified']:
        audio = output / 'capture.wav'
        with wave.open(str(audio), 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(buffer.raw[:header.recorded])
        result['audio_recorded'] = True
        result['wav'] = audio.relative_to(repo).as_posix()
        result['wav_bytes'] = audio.stat().st_size
        result['wav_sha256'] = hashlib.sha256(audio.read_bytes()).hexdigest()
    result_file = output / 'capture-result.json'
    write_diagnostics(result, result_file, repo, unsafe_cleanup)
    return 0 if result['audio_recorded'] and result['cleanup_verified'] else 1


if __name__ == '__main__':
    sys.exit(main())
