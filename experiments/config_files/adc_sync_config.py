# Basic settings
simulated  = True
roach_ip   = '0.0.0.0'
roach_port = 7147
upload     = False
program    = False
boffile    = ''
set_regs   = [{'name' : 'snap_trig' , 'val' : 0},
              {'name' : 'adc0_delay', 'val' : 0},
              {'name' : 'adc1_delay', 'val' : 0}]
reset_regs = []
bw         = 1000.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1']
snap_samples = 400
sync_snaps   = True

# Adc synchronator settings
source_ip    = '0.0.0.0'
source_port  = 0
sync_freq    = 10 # [MHz]
sync_power   = 0  # [dBm]
