# Basic settings
simulated  = True
roach_ip   = '0.0.0.0'
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
plot_titles = ['ZDOK0', 'ZDOK1']
dBFS_const  = 81
spec_info   = {'addr_width'   : 9,
               'data_width'   : 64,
               'data_type'    : 'Q',
               'bram_list2d'  :
               [['dout0_0',],
                ['dout1_0',]]}
