"""Post-hoc diagnostic defined during OMP D comparison; same scenario for Claude."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

SOURCE = '''import unittest

def cleanup_error():
    raise RuntimeError("cleanup sentinel error")

class TestCleanupError(unittest.TestCase):
    def test_failure_and_cleanup_error(self):
        self.addCleanup(cleanup_error)
        assert False, "original sentinel failure"
'''


def diagnose(workspace):
    workspace = Path(workspace).resolve()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
               PYTHONIOENCODING='utf-8', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
    with tempfile.TemporaryDirectory(prefix='dstest-cleanup-diagnostic-') as temp:
        temp = Path(temp)
        target = temp / 'test_cleanup_error.py'
        target.write_text(SOURCE, encoding='utf-8')
        proc = subprocess.run([os.environ.get('FIELDTEST_PYTHON', sys.executable), '-B',
                               str(workspace / 'run_pytest.py'), str(target), '-q', '-c', 'NUL',
                               '--confcutdir', str(temp)], cwd=workspace, env=env, capture_output=True, text=True, timeout=30)
    return {'exit_code': proc.returncode, 'cleanup_error_visible': 'cleanup sentinel error' in proc.stdout,
            'original_failure_visible': 'original sentinel failure' in proc.stdout,
            'stdout': proc.stdout, 'stderr': proc.stderr,
            'preplanned_original_D': False, 'defined_before_claude_submission': True}


if __name__ == '__main__':
    print(json.dumps(diagnose(sys.argv[1]), ensure_ascii=False, indent=2))
