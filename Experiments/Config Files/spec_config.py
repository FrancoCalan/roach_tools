# Basic settings
simulated  = True
roach_ip   = '192.168.1.12'
roach_port = 7147
program    = False
boffile    = ''
set_regs   = [{'name' : 'acc_len', 'val' : 1}]
reset_regs = ['cnt_rst']
bw         = 1000 # [MHz]

# Snapshot settings
snapshots  = [['adcsnap0'], ['adcsnap1']]
snap_samples = 256

# Spectrometer Settings
dBFS_const  = 81
spec_info   = {'addr_width' : 9,
               'data_width' : 64,
               'data_type'  : 'Q',
               'spec_list'  :
               [{'name' : 'ZDOK0', 'bram_list' : ['dout0_0']},
                {'name' : 'ZDOK1', 'bram_list' : ['dout1_0']}]}
