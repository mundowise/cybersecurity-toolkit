import unittest
from src.modules.password_ai import rank_passwords, simple_markov

class TestPasswordAI(unittest.TestCase):
    def test_rank_passwords(self):
        pwlist = ['123', 'abc', 'password', 'admin', '1234']
        ranked = rank_passwords(pwlist)
        self.assertIn('123', ranked)
    def test_simple_markov(self):
        pwlist = ['test', 'testing', 'tester']
        ranked = simple_markov(pwlist)
        self.assertIn('test', ranked)
