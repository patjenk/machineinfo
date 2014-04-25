from unittest import TestCase
from .. import Gawain


class GawainBasicsTestCase(TestCase):

    def test_init(self):
        """
        Test that we can create a pygawain object without crashing.
        """
        processor = Gawain()
