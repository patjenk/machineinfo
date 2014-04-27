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
