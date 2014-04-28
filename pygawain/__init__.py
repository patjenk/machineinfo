import re
import subprocess
import os


class Gawain:
    pass

    def _cpudata(self):
        """
        Return some CPU information for Linux minions

        Derived from https://github.com/saltstack/salt/blob/9f03a55b1024cd362fc61aa9acc6dcaab164a0f8/salt/grains/core.py#L79
        """
        # Provides:
        #   num_cpus
        #   cpu_model
        #   cpu_flags
        cpus = {}
        cpuinfo = '/proc/cpuinfo'
        # Parse over the cpuinfo file
        if os.path.isfile(cpuinfo):
            with open(cpuinfo, 'r') as _fp:
                for line in _fp:
                    comps = line.split(':')
                    if not len(comps) > 1:
                        continue
                    key = comps[0].strip()
                    val = comps[1].strip()
                    if key == 'processor':
                        cpus['num_cpus'] = int(val) + 1
                    elif key == 'model name':
                        cpus['cpu_model'] = val
                    elif key == 'flags':
                        cpus['cpu_flags'] = val.split()
                    elif key == 'Features':
                        cpus['cpu_flags'] = val.split()
                    # ARM support - /proc/cpuinfo
                    #
                    # Processor       : ARMv6-compatible processor rev 7 (v6l)
                    # BogoMIPS        : 697.95
                    # Features        : swp half thumb fastmult vfp edsp java tls
                    # CPU implementer : 0x41
                    # CPU architecture: 7
                    # CPU variant     : 0x0
                    # CPU part        : 0xb76
                    # CPU revision    : 7
                    #
                    # Hardware        : BCM2708
                    # Revision        : 0002
                    # Serial          : 00000000XXXXXXXX
                    elif key == 'Processor':
                        cpus['cpu_model'] = val.split('-')[0]
                        cpus['num_cpus'] = 1
        if 'num_cpus' not in cpus:
            cpus['num_cpus'] = 0
        if 'cpu_model' not in cpus:
            cpus['cpu_model'] = 'Unknown'
        if 'cpu_flags' not in cpus:
            cpus['cpu_flags'] = []
        return cpus

    def _networkdata(self):
        """
        Uses ifconfig to return a dictionary of interfaces with various information
        about each (up/down state, ip address, netmask, and hwaddr)

        Derived from https://github.com/saltstack/salt/blob/cf65a7d4ce380d34f78536296ac29705ad729f4d/salt/utils/network.py#L269
        """
        ifconfig_path = "/sbin/ifconfig" # this should probably be determined programatically
        ifconfig_output = subprocess.Popen(
            '{0} -a'.format(ifconfig_path),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT).communicate()[0]


        ifconfig_interfaces = dict()

        piface = re.compile(r'^([^\s:]+)')
        pmac = re.compile('.*?(?:HWaddr|ether|address:|lladdr) ([0-9a-fA-F:]+)')
        pip = re.compile(r'.*?(?:inet addr:|inet )(.*?)\s')
        pip6 = re.compile('.*?(?:inet6 addr: (.*?)/|inet6 )([0-9a-fA-F:]+)')
        pmask = re.compile(r'.*?(?:Mask:|netmask )(?:((?:0x)?[0-9a-fA-F]{8})|([\d\.]+))')
        pmask6 = re.compile(r'.*?(?:inet6 addr: [0-9a-fA-F:]+/(\d+)|prefixlen (\d+)).*')
        pupdown = re.compile('UP')
        pbcast = re.compile(r'.*?(?:Bcast:|broadcast )([\d\.]+)')

        groups = re.compile('\r?\n(?=\\S)').split(ifconfig_output)
        for group in groups:
            data = dict()
            iface = ''
            updown = False
            for line in group.splitlines():
                miface = piface.match(line)
                mmac = pmac.match(line)
                mip = pip.match(line)
                mip6 = pip6.match(line)
                mupdown = pupdown.search(line)
                if miface:
                    iface = miface.group(1)
                if mmac:
                    data['hwaddr'] = mmac.group(1)
                if mip:
                    if 'inet' not in data:
                        data['inet'] = list()
                    addr_obj = dict()
                    addr_obj['address'] = mip.group(1)
                    mmask = pmask.match(line)
                    if mmask:
                        if mmask.group(1):
                            mmask = _number_of_set_bits_to_ipv4_netmask(
                                int(mmask.group(1), 16))
                        else:
                            mmask = mmask.group(2)
                        addr_obj['netmask'] = mmask
                    mbcast = pbcast.match(line)
                    if mbcast:
                        addr_obj['broadcast'] = mbcast.group(1)
                    data['inet'].append(addr_obj)
                if mupdown:
                    updown = True
                if mip6:
                    if 'inet6' not in data:
                        data['inet6'] = list()
                    addr_obj = dict()
                    addr_obj['address'] = mip6.group(1) or mip6.group(2)
                    mmask6 = pmask6.match(line)
                    if mmask6:
                        addr_obj['prefixlen'] = mmask6.group(1) or mmask6.group(2)
                    data['inet6'].append(addr_obj)
            data['up'] = updown
            ifconfig_interfaces[iface] = data
            del data
        return ifconfig_interfaces

