import unittest

cleanups = []


class TestExample(unittest.TestCase):
    def test_1_pass(self):
        self.addCleanup(cleanups.append, 'passed')

    def test_2_fail(self):
        self.addCleanup(cleanups.append, 'failed')
        assert False, 'intentional test failure'

    def test_3_check_cleanup(self):
        assert cleanups == ['passed', 'failed']
