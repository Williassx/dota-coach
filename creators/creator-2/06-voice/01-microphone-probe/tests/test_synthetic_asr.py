"""Pure metric and receipt tests: no TTS, microphone, model load or inference."""

from contextlib import contextmanager
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import sys
import tempfile
import unittest
from unittest import mock
import wave


SOURCE = Path(__file__).parents[1] / 'notes' / 'synthetic-asr.py'
REFERENCES = [
    'Игрок два, отойди назад.',
    'Игрок один, атакуй цель.',
    'Команда, соберитесь вместе.',
]
FORMAT = {'sample_rate': 16000, 'sample_width_bytes': 2, 'channels': 1, 'encoding': 'PCM'}
INFERENCE_PACKAGES = {'faster_whisper', 'ctranslate2', 'av', 'sounddevice', 'pyaudio', 'clr'}


@contextmanager
def no_inference_imports():
    original = __import__

    def guarded(name, *args, **kwargs):
        if name.split('.')[0] in INFERENCE_PACKAGES:
            raise AssertionError('Inference/audio activation forbidden in pure validation: ' + name)
        return original(name, *args, **kwargs)

    with mock.patch('builtins.__import__', side_effect=guarded):
        yield


def load_helper():
    if not SOURCE.is_file():
        raise AssertionError('Missing notes/synthetic-asr.py implementation (expected RED)')
    spec = importlib.util.spec_from_file_location('synthetic_asr_unit', SOURCE)
    helper = importlib.util.module_from_spec(spec)
    with no_inference_imports():
        spec.loader.exec_module(helper)
    return helper


def save_receipt(path, receipt):
    path.write_text(json.dumps(receipt, ensure_ascii=False), encoding='utf-8')


def write_wave(path, channels=1, sample_rate=16000, width=2):
    with wave.open(str(path), 'wb') as audio:
        audio.setnchannels(channels)
        audio.setsampwidth(width)
        audio.setframerate(sample_rate)
        # Short PCM fixture; deliberately not used as positive speech evidence.
        audio.writeframes(b'\x00' * (3200 * channels * width))


def fixture(repository):
    directory = repository / 'build' / 'dota_coach' / ('asr-synthetic-20261013-' + 'a' * 32)
    directory.mkdir(parents=True)
    receipt = {
        'stage': 'synthetic_tts',
        'source': 'synthetic_system_tts',
        'voice_name': 'Microsoft Irina Desktop',
        'voice_culture': 'ru-RU',
        'audio_format': dict(FORMAT),
        'tts_completed': True,
        'error': None,
        'samples': [],
    }
    for index, reference in enumerate(REFERENCES, 1):
        name = f'sample-{index:02d}.wav'
        audio = directory / name
        write_wave(audio)
        payload = audio.read_bytes()
        receipt['samples'].append({'name': name, 'reference': reference,
                                   'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()})
    path = directory / 'tts-receipt.json'
    save_receipt(path, receipt)
    return path, receipt


class SyntheticASRTests(unittest.TestCase):
    def setUp(self):
        self.asr = load_helper()

    def validate(self, path, repository):
        with no_inference_imports():
            return self.asr.validate_receipt(path, repository=repository)

    def refused(self, path, repository):
        with self.assertRaises((ValueError, OSError)):
            self.validate(path, repository)

    def test_import_is_inert_and_preserves_process_configuration(self):
        environment = dict(os.environ)
        search_path = list(sys.path)
        connect = socket.socket.connect
        with mock.patch('wave.open', side_effect=AssertionError('Audio opened during import')):
            helper = load_helper()
        self.assertEqual(dict(os.environ), environment)
        self.assertEqual(sys.path, search_path)
        self.assertIs(socket.socket.connect, connect)
        for name in ('validate_receipt', 'validate_model', 'normalize_words', 'edit_distance', 'compare_words'):
            self.assertTrue(callable(getattr(helper, name)))

    def test_normalization_and_identical_punctuation_are_zero_error(self):
        self.assertEqual(self.asr.normalize_words('ЁЖ, ИГРОК! ДВА?'), ['еж', 'игрок', 'два'])
        metric = self.asr.compare_words(REFERENCES[0], 'ИГРОК два: отойди назад!!!')
        self.assertEqual(metric['reference_words'], ['игрок', 'два', 'отойди', 'назад'])
        self.assertEqual(metric['hypothesis_words'], metric['reference_words'])
        self.assertEqual(metric['edit_distance'], 0)
        self.assertEqual(metric['wer'], 0)

    def test_substitution_insertion_deletion_and_repeated_word_distance(self):
        cases = [
            ('игрок два назад', 'игрок три назад', 1),
            ('игрок два назад', 'игрок два быстро назад', 1),
            ('игрок два назад', 'игрок назад', 1),
            ('а а б', 'а б', 1),
            ('назад', 'быстро идите назад', 2),
        ]
        for reference, hypothesis, expected in cases:
            with self.subTest(reference=reference, hypothesis=hypothesis):
                ref_words = reference.split()
                hyp_words = hypothesis.split()
                self.assertEqual(self.asr.edit_distance(ref_words, hyp_words), expected)
                metric = self.asr.compare_words(reference, hypothesis)
                self.assertEqual(metric['reference_words'], ref_words)
                self.assertEqual(metric['hypothesis_words'], hyp_words)
                self.assertEqual(metric['edit_distance'], expected)
                self.assertAlmostEqual(metric['wer'], expected / len(ref_words))
        self.assertEqual(self.asr.edit_distance([], ['одно']), 1)
        self.assertEqual(self.asr.edit_distance(['одно'], []), 1)

    def test_empty_normalized_reference_is_rejected(self):
        for reference in ('', '  ', '!!!'):
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                self.asr.compare_words(reference, 'игрок')
        metric = self.asr.compare_words('игрок два', '')
        self.assertEqual(metric['edit_distance'], 2)
        self.assertEqual(metric['wer'], 1)

    def test_valid_receipt_checks_all_three_pcm_payloads_before_inference(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary).resolve()
            path, receipt = fixture(repository)
            validated = self.validate(path, repository)
            self.assertEqual(validated['receipt_path'], path)
            self.assertEqual(validated['directory'], path.parent)
            self.assertEqual(len(validated['samples']), 3)
            for expected, actual in zip(receipt['samples'], validated['samples']):
                self.assertEqual(actual['reference'], expected['reference'])
                self.assertEqual(actual['path'], path.parent / expected['name'])
                self.assertEqual(actual['pcm']['sample_rate'], 16000)
                self.assertEqual(actual['pcm']['sample_width_bytes'], 2)
                self.assertEqual(actual['pcm']['channels'], 1)
                self.assertEqual(actual['pcm']['frames'], 3200)
                self.assertAlmostEqual(actual['pcm']['duration_seconds'], 0.2)

    def test_audio_hash_size_and_changed_bytes_are_rejected(self):
        for mutation in ('hash', 'size', 'payload'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                repository = Path(temporary).resolve()
                path, receipt = fixture(repository)
                if mutation == 'hash':
                    receipt['samples'][0]['sha256'] = '0' * 64
                elif mutation == 'size':
                    receipt['samples'][0]['bytes'] += 1
                else:
                    audio = path.parent / 'sample-01.wav'
                    payload = bytearray(audio.read_bytes())
                    payload[-1] ^= 1  # Remains valid PCM with the original length.
                    audio.write_bytes(payload)
                save_receipt(path, receipt)
                self.refused(path, repository)

    def test_exact_source_headers_references_and_sample_coverage_are_required(self):
        changes = [
            ('stage', 'microphone_capture'), ('source', 'real_player'),
            ('voice_name', 'Another voice'), ('voice_culture', 'en-US'),
            ('tts_completed', False), ('error', 'TTS failed'),
            ('reference', 'Игрок два, атакуй цель.'), ('missing_sample', None),
            ('duplicate_name', None),
        ]
        for field, value in changes:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                repository = Path(temporary).resolve()
                path, receipt = fixture(repository)
                if field == 'reference':
                    receipt['samples'][0]['reference'] = value
                elif field == 'missing_sample':
                    receipt['samples'].pop()
                elif field == 'duplicate_name':
                    receipt['samples'][1]['name'] = receipt['samples'][0]['name']
                else:
                    receipt[field] = value
                save_receipt(path, receipt)
                self.refused(path, repository)

    def test_stereo_rate_width_or_receipt_format_mismatch_is_rejected(self):
        cases = [{'channels': 2}, {'sample_rate': 8000}, {'width': 1}, {'receipt_only': True}]
        for change in cases:
            with self.subTest(change=change), tempfile.TemporaryDirectory() as temporary:
                repository = Path(temporary).resolve()
                path, receipt = fixture(repository)
                if change.get('receipt_only'):
                    receipt['audio_format']['encoding'] = 'IEEE_FLOAT'
                else:
                    audio = path.parent / 'sample-01.wav'
                    write_wave(audio, **change)
                    payload = audio.read_bytes()
                    receipt['samples'][0]['bytes'] = len(payload)
                    receipt['samples'][0]['sha256'] = hashlib.sha256(payload).hexdigest()
                save_receipt(path, receipt)
                self.refused(path, repository)

    def test_path_escape_unapproved_receipt_and_missing_model_refuse_before_inference(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = Path(temporary).resolve()
            path, original = fixture(repository)
            elsewhere = repository / 'unapproved'
            shutil.copytree(path.parent, elsewhere)
            # All three WAVs and hashes exist here; rejection must not rely on missing audio.
            self.refused(elsewhere / 'tts-receipt.json', repository)
            wrong_name = path.parent.parent / 'asr-synthetic-20261013-not-a-hex-id'
            shutil.copytree(path.parent, wrong_name)
            self.refused(wrong_name / 'tts-receipt.json', repository)
            for name in ('../sample-01.wav', str((path.parent / 'sample-01.wav').resolve())):
                changed = copy.deepcopy(original)
                changed['samples'][0]['name'] = name
                save_receipt(path, changed)
                with self.subTest(name=name):
                    self.refused(path, repository)
            with no_inference_imports(), self.assertRaises((ValueError, OSError)):
                self.asr.validate_model(repository=repository)


if __name__ == '__main__':
    unittest.main()
