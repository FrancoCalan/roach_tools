# Basic settings
simulated  = True
roach_ip   = '0.0.0.0'
roach_port = 7147
upload     = False
program    = False
boffile    = ''
set_regs   = [{'name' : 'acc_len', 'val' : 2**0}]
reset_regs = ['cnt_rst']
bw         = 800.0 # [MHz]

# Snapshot settings
snapshots    = ['adcsnap0', 'adcsnap1']
snap_samples = 256

# Spectrometer Settings
plot_titles = ['ZDOK0', 'ZDOK1']
spec_info   = {'addr_width'   : 9,
               'word_width'   : 64,
               'data_type'    : '>u8',
               'interleave'   : True,
               'acc_len_reg'  : 'acc_len',
               'bram_names'  :
               [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'],
                ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3', 'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7']]}
