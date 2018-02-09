# Basic settings
simulated  = True
roach_ip   = '192.168.1.12'
roach_port = 7147
program    = False
boffile    = 'spec2adc_4096ch_800mhz.bof.gz'
set_regs   = [{'name' : 'acc_len', 'val' : 2**0}]
reset_regs = ['cnt_rst']
bw          = 800 # [MHz]

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
               [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'],
                ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3', 'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7']]}
