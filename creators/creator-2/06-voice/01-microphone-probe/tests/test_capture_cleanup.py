"""Failure injection for diagnostics only: no hardware capture."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('microphone_probe', Path(__file__).parents[1] / 'notes/capture-command.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

class ForcedExit(BaseException):
    pass

class DiagnosticCleanupTests(unittest.TestCase):
    def exercise_unsafe(self, failure):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / 'result.json'
            with mock.patch.object(probe.os, '_exit', side_effect=ForcedExit) as exit_call:
                with failure:
                    with self.assertRaises(ForcedExit):
                        probe.write_diagnostics({'error': 'cleanup failed'}, output, root, True)
                exit_call.assert_called_once_with(1)

    def test_unsafe_write_failure_still_terminates_process(self):
        self.exercise_unsafe(mock.patch.object(Path, 'write_text', side_effect=OSError('disk failure')))

    def test_unsafe_stdout_failure_still_terminates_process(self):
        self.exercise_unsafe(mock.patch('builtins.print', side_effect=BrokenPipeError('pipe failure')))

    def test_unsafe_successful_diagnostics_still_terminates_process(self):
        self.exercise_unsafe(mock.patch('builtins.print'))

    def test_safe_logging_error_propagates_without_emergency_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with mock.patch.object(probe.os, '_exit') as exit_call:
                with mock.patch.object(Path, 'write_text', side_effect=OSError('disk failure')):
                    with self.assertRaises(OSError):
                        probe.write_diagnostics({}, root / 'result.json', root, False)
                exit_call.assert_not_called()

if __name__ == '__main__':
    unittest.main()
