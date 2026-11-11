"""Host-only behavioral acceptance for the real pytest unittest lifecycle bug."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

PYTHON = Path(os.environ.get('FIELDTEST_PYTHON', sys.executable))

CASE_SOURCE = r'''
import json
import os
import pdb
import unittest
from pathlib import Path

LOG = Path(os.environ['CASE_LOG'])
def note(value):
    with LOG.open('a') as stream:
        stream.write(value + '\n')

class Recorder(pdb.Pdb):
    def interaction(self, frame, traceback):
        note('debug')
        self.set_continue()

MODE = os.environ['CASE_MODE']
class TestLifecycle(unittest.TestCase):
    def setUp(self):
        note('setup')
        self.addCleanup(note, 'cleanup-first')
        self.addCleanup(note, 'cleanup-last')
        if MODE == 'setup_error':
            raise ValueError('setup broke')
        if MODE == 'setup_skip':
            self.skipTest('setup skip')

    def tearDown(self):
        note('teardown')
        if MODE == 'teardown_error':
            raise ValueError('teardown broke')

    def test_case(self):
        note('test')
        if MODE in ('failure', 'pdb_failure'):
            assert False, 'intentional failure'
        if MODE == 'error':
            raise ValueError('test broke')
        if MODE == 'skip':
            self.skipTest('skip')

class TestExpected(unittest.TestCase):
    @unittest.expectedFailure
    def test_expected(self):
        self.addCleanup(note, 'expected-cleanup')
        assert False
'''


def verify(workspace):
    results = []
    with tempfile.TemporaryDirectory(prefix='dstest-d-accept-') as temp:
        temp = Path(temp)
        (temp / 'test_lifecycle.py').write_text(CASE_SOURCE, encoding='utf-8')
        env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',
                   PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
        for mode in ('pass', 'failure', 'error', 'setup_error', 'teardown_error', 'skip', 'setup_skip', 'pdb_failure', 'trace_pass'):
            log = temp / (mode + '.txt')
            env.update(CASE_LOG=str(log), CASE_MODE=mode)
            cmd = [str(PYTHON), '-B', str(workspace / 'run_pytest.py'),
                   str(temp / 'test_lifecycle.py') + '::TestLifecycle', '-q', '-c', 'NUL',
                   '--confcutdir', str(temp), '--basetemp', str(temp / ('tmp-' + mode))]
            if mode == 'pdb_failure':
                cmd += ['--pdb', '--pdbcls=test_lifecycle:Recorder']
            if mode == 'trace_pass':
                cmd += ['--trace', '--pdbcls=test_lifecycle:Recorder']
            try:
                proc = subprocess.run(cmd, cwd=workspace, env=env, input='', capture_output=True, text=True, timeout=20)
                events = log.read_text().splitlines() if log.exists() else []
                expected = ['setup']
                if mode not in ('setup_error', 'setup_skip'):
                    expected += ['test', 'teardown']
                expected += ['cleanup-last', 'cleanup-first']
                clean_events = [e for e in events if e != 'debug']
                expected_code = 1 if mode in ('failure', 'error', 'setup_error', 'teardown_error', 'pdb_failure') else 0
                ok = clean_events == expected and proc.returncode == expected_code
                if mode == 'pdb_failure':
                    ok = (events == ['setup', 'test', 'debug', 'teardown',
                                     'cleanup-last', 'cleanup-first']
                          and proc.returncode == expected_code)
                if mode in ('pdb_failure', 'trace_pass'):
                    ok = ok and 'debug' in events
                    if mode == 'pdb_failure' and 'teardown' in events and 'debug' in events:
                        ok = ok and events.index('debug') < events.index('teardown')
                results.append({'case': mode, 'pass': ok, 'events': events, 'expected_without_debug': expected,
                                'exit_code': proc.returncode, 'output': proc.stdout[-2500:], 'stderr': proc.stderr[-1000:]})
            except subprocess.TimeoutExpired:
                results.append({'case': mode, 'pass': False, 'error': 'timeout'})
        log = temp / 'expected.txt'
        env.update(CASE_LOG=str(log), CASE_MODE='pass')
        proc = subprocess.run([str(PYTHON), '-B', str(workspace / 'run_pytest.py'),
                               str(temp / 'test_lifecycle.py') + '::TestExpected', '-q', '-c', 'NUL',
                               '--confcutdir', str(temp)], cwd=workspace, env=env, capture_output=True, text=True, timeout=20)
        events = log.read_text().splitlines() if log.exists() else []
        results.append({'case': 'expected_failure', 'pass': proc.returncode == 0 and events == ['expected-cleanup'] and '1 xfailed' in proc.stdout,
                        'events': events, 'output': proc.stdout[-1000:]})
    from diagnose_cleanup import diagnose
    diagnostic = diagnose(workspace)
    results.append({'case': 'failure_and_cleanup_error',
                    'pass': diagnostic['exit_code'] == 1 and diagnostic['cleanup_error_visible'] and diagnostic['original_failure_visible'],
                    'diagnostic': diagnostic})
    return {'task': 'D', 'workspace': str(workspace), 'passed': sum(r['pass'] for r in results),
            'total': len(results), 'all_passed': all(r['pass'] for r in results), 'checks': results}


if __name__ == '__main__':
    result = verify(Path(sys.argv[1]).resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result['all_passed'] else 1)
