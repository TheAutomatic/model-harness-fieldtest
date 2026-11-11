import json, os, pathlib, subprocess, sys, tempfile

def diagnose(workspace):
    workspace=pathlib.Path(workspace).resolve()
    with tempfile.TemporaryDirectory(prefix='double-failure-') as temp:
        temp=pathlib.Path(temp)
        marker=temp/'cleanup.marker'
        source=temp/'test_double.py'
        source.write_text('''import unittest, os
from pathlib import Path
class TestDouble(unittest.TestCase):
    def test_fail(self):
        self.addCleanup(lambda: Path(os.environ['CLEANUP_MARKER']).write_text('yes'))
        assert False, 'original failure'
    def tearDown(self):
        raise RuntimeError('teardown failure')
''',encoding='utf-8')
        env=dict(os.environ,CLEANUP_MARKER=str(marker),PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
        proc=subprocess.run([sys.executable,str(workspace/'run_pytest.py'),str(source),'-q','-s','-c','NUL','--confcutdir',str(temp)],env=env,capture_output=True,text=True,timeout=30)
        return {'post_hoc':True,'not_part_of_11_point_score':True,'scenario':'test and tearDown both fail','cleanup_ran':marker.exists(),'exit_code':proc.returncode}

if __name__=='__main__':
    print(json.dumps(diagnose(sys.argv[1]),indent=2))
