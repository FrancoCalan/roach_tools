# Basic settings
simulated  = True
roach_ip   = '0.0.0.0'
roach_port = 7147
upload     = False
program    = False
boffile    = ''
set_regs   = [{'name' : 'snap_trig', 'val' : 1}]
reset_regs = []
bw         = 1000

# Snapshot settings
snapshots    = [{'zdok' : 0, 'names' : ['adcsnap0']}, 
                {'zdok' : 1, 'names' : ['adcsnap1']}]
snap_samples = 256
cal_adcs     = False
