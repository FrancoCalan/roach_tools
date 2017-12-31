# Basic settings
simulated  = True
ip         = '0.0.0.0'
port       = 7147
boffile    = 'dummy.bof'
set_regs   = [{'name' : 'acc_len',     'val' : 1},
              {'name' : 'filter_gain', 'val' : 2**32-1},
              {'name' : 'filter_acc',  'val' : 1},
              {'name' : 'channel',     'val' : 0}]
reset_regs = ['cnt_rst', 'filter_on']
cal_adc    = [False, False]
snapshots  = [['adcsnap0'], ['adcsnap1']]

# Snapshot settings
snap_samples = 256

# Spectrometer Settings
bw          = 1000 # [MHz]
dBFS_const  = 81
spec_info   = {'addr_width' : 9,
               'data_width' : 64,
               'data_type'  : 'Q',
               'spec_list'  :
               [{'name' : 'Primary Signal',   'bram_list' : ['dout0_0']},
                {'name' : 'Reference Signal', 'bram_list' : ['dout1_0']},
                {'name' : 'Filter Output',    'bram_list' : ['dout2_0']}]}

# Kestfilt Settings
conv_info_chnl = {'name'       : 'chnl',
                  'addr_width' : 10,
                  'data_width' : 32,
                  'data_type'  : 'i',
                  'bram_list'  : ['dout_chnl_real', 'dout_chnl_imag']}

conv_info_max  = {'name'       : 'max',
                  'addr_width' : 10,
                  'data_width' : 64,
                  'data_type'  : 'Q',
                  'bram_list'  : ['dout_chnl_max']}

conv_info_mean = {'name'       : 'mean',
                  'addr_width' : 10,
                  'data_width' : 64,
                  'data_type'  : 'Q',
                  'bram_list'  : ['dout_chnl_mean']}
