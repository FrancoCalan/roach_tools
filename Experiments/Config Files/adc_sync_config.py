# Basic settings
simulated  = True
roach_ip   = '0.0.0.0'
roach_port = 7147
program    = False
boffile    = ''
set_regs   = []
reset_regs = []

# Snapshot settings
snapshots  = [['adcsnap0'], ['adcsnap1']]
snap_samples = 256

# Adc synchronator settings
source_ip    = '0.0.0.0'
source_port  = 0
sync_freq    = 10 # MHz
sync_power   = 0  # dBm
snap_samples = 16 * 2**10 # simultaneous inputs * bram depth
snap_trig    = 'snap_trig'
adc_delays   = ['adc0_delay', 'adc1_delay']

