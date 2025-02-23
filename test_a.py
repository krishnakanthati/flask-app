import unittest
from a import add

class TestAdd(unittest.TestCase):
    def test_add(self):
        res = add(1, 2)
        self.assertEqual(res, 3)

if __name__ == '__main__':
    unittest.main()