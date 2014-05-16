from mock import mock_open, patch, MagicMock, Mock
from unittest import TestCase
from .. import MachineInfo 


class MachineInfoBasicsTestCase(TestCase):

    def test_init(self):
        """
        Test that we can create a machineinfo object without crashing.
        """
        processor = MachineInfo()

    def test_processors(self):
        """
        Test that we can identify the number of processors and their types.
        """
        processor = MachineInfo()
        read_data=open('./machineinfo/tests/staticfiles/proc_cpuinfo.example', 'r').read()
        with patch('__builtin__.open', create=True) as mymock:
            mymock.return_value = MagicMock(spec=file)
            handle = mymock.return_value.__enter__.return_value
            handle.__iter__.return_value = iter(read_data.split("\n"))
            processors = processor._cpudata()
        self.assertTrue("1234 PJ" in processors['cpu_model'])

    def test_network_interfaces(self):
        """
        Test that we can successfully find the network interfaces

        TODO: mock out the call to ifconfig to and inspect the result from 
        _networkdata better.
        """
        processor = MachineInfo()
        network_interfaces = MachineInfo()
        network_interfaces = processor._networkdata()
        self.assertTrue("eth0" in network_interfaces)
