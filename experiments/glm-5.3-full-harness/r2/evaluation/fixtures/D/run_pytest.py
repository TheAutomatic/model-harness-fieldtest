"""Run this checkout with the preinstalled offline dependencies."""
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'src'))
sys.path.insert(1, os.environ['DSTEST_PYTEST_DEPS'])
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'

import pytest

if __name__ == '__main__':
    sys.exit(pytest.main(sys.argv[1:]))
