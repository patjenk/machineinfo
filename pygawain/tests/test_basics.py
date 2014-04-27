from mock import mock_open, patch, MagicMock, Mock
from unittest import TestCase
from .. import Gawain


class GawainBasicsTestCase(TestCase):

    def test_init(self):
        """
        Test that we can create a pygawain object without crashing.
        """
        processor = Gawain()

    def test_processors(self):
        """
        Test that we can identify the number of processors and their types.
        """
        processor = Gawain()

        read_data=open('./pygawain/tests/staticfiles/proc_cpuinfo.example', 'r').read()
        with patch('__builtin__.open', create=True) as mymock:
            mymock.return_value = MagicMock(spec=file)
            handle = mymock.return_value.__enter__.return_value
            handle.__iter__.return_value = iter(read_data.split("\n"))


            processors = processor._cpudata()
        self.assertTrue("1234 PJ" in processors['cpu_model'])
