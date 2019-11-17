import unittest

import itty3


class TestQueryDict(unittest.TestCase):
    def setUp(self):
        self.simple_qd = itty3.QueryDict(
            {"test": ["case"], "count": [1], "hello": ["world"]}
        )
        self.complex_qd = itty3.QueryDict(
            {
                "names": ["Daniel", "Joe", "Jane"],
                "count": [1],
                "greetings": ["Hello", "Hi", "What's up"],
            }
        )

    def test_get(self):
        self.assertEqual(self.simple_qd["test"], "case")
        self.assertEqual(self.simple_qd["count"], 1)

        self.assertEqual(self.complex_qd["names"], "Daniel")

    def test_set(self):
        # Sanity check.
        self.assertEqual(self.simple_qd["test"], "case")

        self.simple_qd["test"] = "ing"
        self.assertEqual(self.simple_qd["test"], "ing")

    def test_getlist(self):
        self.assertEqual(self.simple_qd.getlist("test"), ["case"])
        self.assertEqual(self.simple_qd.getlist("count"), [1])

        self.assertEqual(
            self.complex_qd.getlist("names"), ["Daniel", "Joe", "Jane"]
        )

    def test_dictlike(self):
        # Various dict-compatibility tests.
        self.assertTrue("test" in self.simple_qd)

        self.assertEqual(
            sorted(self.simple_qd.keys()), sorted(["count", "hello", "test"])
        )

        self.assertEqual(
            sorted([key for key in self.simple_qd]),
            sorted(["count", "hello", "test"]),
        )

        self.assertEqual(
            sorted([(key, value) for key, value in self.simple_qd.items()]),
            sorted([("count", 1), ("hello", "world"), ("test", "case")]),
        )
