import unittest


class HelpersTestCase(unittest.TestCase):
    def test_with_time(self):
        MOCK_VALUE = 5

        def test_func(val):
            return val

        self.assertEqual(
            MOCK_VALUE,
            test_func(MOCK_VALUE),
        )


if __name__ == "__main__":
    unittest.main()
