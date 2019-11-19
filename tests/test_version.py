import unittest

import itty3


class TestVersion(unittest.TestCase):
    def test_short(self):
        short_version = "{}.{}.{}".format(
            itty3.__version__[0], itty3.__version__[1], itty3.__version__[2],
        )
        self.assertEqual(itty3.get_version(), short_version)

    def test_full(self):
        short_version = "{}.{}.{}".format(
            itty3.__version__[0], itty3.__version__[1], itty3.__version__[2],
        )
        long_version = "-".join([str(v) for v in itty3.__version__[3:]])
        self.assertEqual(
            itty3.get_version(full=True),
            "{}-{}".format(short_version, long_version),
        )
