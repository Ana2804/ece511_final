import m5
from m5.objects import Cache

# Add the common scripts to our path
m5.util.addToPath("../../")

from common import SimpleOpts

# Some specific options for caches
# For all options see src/mem/cache/BaseCache.py


class L1Cache(Cache):
    """Simple L1 Cache with default values"""

    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

    def __init__(self, options=None):
        super().__init__()
        pass

    def connectBus(self, bus):
        """Connect this cache to a memory-side bus"""
        self.mem_side = bus.cpu_side_ports

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU-side port"""
        raise NotImplementedError


class L1ICache(L1Cache):
    """Simple L1 instruction cache with default values"""

    # Set the default size
    size = "16kB"

    SimpleOpts.add_option(
        "--l1i_size", help=f"L1 instruction cache size. Default: {size}"
    )

    def __init__(self, opts=None):
        super().__init__(opts)
        if not opts or not opts.l1d_size:
            return
        self.size = opts.l1d_size

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU dcache port"""
        self.cpu_side = cpu.dcache_port


class L2Cache(Cache):
    """Simple L2 Cache with default values"""

    # Default parameters
    size = "256kB"
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

    SimpleOpts.add_option("--l2_size", help=f"L2 cache size. Default: {size}")

    def __init__(self, opts=None):
        super().__init__()
        if not opts or not opts.l2_size:
            return
        self.size = opts.l2_size

    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports
class SystemWithTwoCPUs(m5.objects.System):
    def __init__(self):
        super().__init__()

        # Create CPUs
        self.cpu1 = m5.objects.ARMV8A_FastModel()
        self.cpu2 = m5.objects.ARMV8A_FastModel()

        # Create caches
        self.l1i_cache1 = L1ICache()
        self.l1d_cache1 = L1DCache()
        self.l2_cache = L2Cache()

        # Connect CPU1 to L1 cache
        self.cpu1.icache_port = self.l1i_cache1.cpu_side
        self.cpu1.dcache_port = self.l1d_cache1.cpu_side

        # Connect L1 cache to L2 cache
        self.l1i_cache1.mem_side = self.l2_cache.cpu_side
        self.l1d_cache1.mem_side = self.l2_cache.cpu_side

        # Connect L2 cache to CPU2
        self.l2_cache.mem_side = self.cpu2.icache_port
        self.l2_cache.mem_side = self.cpu2.dcache_port

        # Add components to the system
        self.add(self.cpu1)
        self.add(self.cpu2)
        self.add(self.l1i_cache1)
        self.add(self.l1d_cache1)
        self.add(self.l2_cache)


# Entry point for gem5
def main():
    m5.options.parse_args()
    system = SystemWithTwoCPUs()
    root = m5.objects.Root(full_system=False, system=system)
    m5.instantiate()
    m5.simulate()

if __name__ == "__m5_main__":
    main()
