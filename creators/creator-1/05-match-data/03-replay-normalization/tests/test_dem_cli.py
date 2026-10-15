import json
import subprocess
import sys
import unittest
from pathlib import Path

class CliTests(unittest.TestCase):
    def test_cli_missing_input_is_error_not_traceback(self):
        script=Path(__file__).resolve().parents[1]/'src/import_dem.py'
        r=subprocess.run([sys.executable,str(script),'--input','missing','--match-id','1','--account-id','1',
                          '--lock','missing','--config','missing','--output','missing'],capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
        self.assertEqual(json.loads(r.stdout)['completed'],False)
        self.assertNotIn('Traceback',r.stderr)

if __name__=='__main__':unittest.main()
