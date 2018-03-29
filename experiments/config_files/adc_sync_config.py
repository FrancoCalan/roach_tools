# Basic settings
simulated  = True
roach_ip   = '0.0.0.0'
roach_port = 7147
program    = False
boffile    = ''
set_regs   = [{'name' : 'adc0_delay', 'val' : 0},
              {'name' : 'adc1_delay', 'val' : 0}]
reset_regs = ['snap_trig']
bw         = 1000 # [MHz]

# Snapshot settings
snapshots  = [['adcsnap0'], ['adcsnap1']]
snap_samples = 400

# Adc synchronator settings
source_ip    = '0.0.0.0'
source_port  = 0
sync_freq    = 10 # [MHz]
sync_power   = 0  # [dBm]
bram_snapshots = {'addr_width' : 10,
                  'bram_width' : 128,
                  'data_type'  : 'b',
                  'bram_list'  : ['bram_adcsnap0', 'bram_adcsnap1']}
