# Basic settings
simulated  = True
ip         = '0.0.0.0'
port       = 7147
program    = False
boffile    = ''
set_regs   = [{'name' : 'acc_len', 'val' : 1}]
reset_regs = ['cnt_rst']
cal_adc    = [False, False]

# Snapshot settings
snap_samples = 256

# Spectrometer Settings
bw          = 1000 # [MHz]
dBFS_const  = 81
spec_info   = {'addr_width' : 9,
               'data_width' : 64,
               'data_type'  : 'Q',
               'spec_list'  :
               [{'name' : 'I', 'bram_list' : ['dout0_0']},
                {'name' : 'Q', 'bram_list' : ['dout1_0']}]}
