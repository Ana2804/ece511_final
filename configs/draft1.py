import m5
from m5.objects import *

system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MB")]

cpu1 = ARMTimingSimpleCPU()
cpu2 = ARMTimingSimpleCPU()

system.cpu = [cpu1, cpu2]
system.membus = SystemXBar()

# Create a crossbar for cache ports
crossbar = L1XBar()

# Connect CPUs to the crossbar
cpu1.icache_port = crossbar.master
cpu1.dcache_port = crossbar.master

cpu2.icache_port = crossbar.slave
cpu2.dcache_port = crossbar.slave

# Connect the crossbar to the memory controller
crossbar.cpu_side = mem_ctrl.port
crossbar.mem_side = mem_ctrl.port


system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports

system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

binary = "tests/test-progs/hello/bin/ARM/linux/hello"

# for gem5 V21 and beyond
system.workload = SEWorkload.init_compatible(binary)

process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()
root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()

print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
