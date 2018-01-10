# Basic settings
simulated  = True
ip         = '0.0.0.0'
port       = 7147
boffile    = 'dummy.bof'
set_regs   = [{'name' : 'acc_len', 'val' : 1}]
reset_regs = ['cnt_rst']
cal_adc    = [False, False]
snapshots  = [['adcsnap0'], ['adcsnap1']]

# Snapshot settings
snap_samples = 256
