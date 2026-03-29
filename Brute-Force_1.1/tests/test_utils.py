import unittest
from src.core.utils import es_valido, parse_headers

class TestUtils(unittest.TestCase):
    def test_es_valido(self):
        self.assertTrue(es_valido('usuario'))
        self.assertFalse(es_valido('usua#rio!'))
    def test_parse_headers(self):
        txt = "User-Agent: test\nAccept: */*"
        headers = parse_headers(txt)
        self.assertEqual(headers['User-Agent'], 'test')
