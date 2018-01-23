# Basic settings
simulated  = True
roach_ip   = '0.0.0.0'
roach_port = 7147
program    = False
boffile    = ''
set_regs   = [{'name' : 'acc_len',     'val' : 1},
              {'name' : 'filter_gain', 'val' : 2**32-1},
              {'name' : 'filter_acc',  'val' : 1},
              {'name' : 'channel',     'val' : 0}]
reset_regs = ['cnt_rst', 'filter_on']
bw         = 1000 # [MHz]

# Snapshot settings
snapshots  = [['adcsnap0'], ['adcsnap1']]
snap_samples = 256

# Spectrometer Settings
plot_titles = ['Primary Signal', 'Reference Signal', 'Filter Output']
dBFS_const  = 81
spec_info   = {'addr_width'   : 9,
               'data_width'   : 64,
               'data_type'    : 'Q',
               'bram_list2d'  :
               [['dout0_0',],
                ['dout1_0',],
                ['dout2_0',]]}

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
                  'bram_name'  : 'dout_chnl_max'}

conv_info_mean = {'name'       : 'mean',
                  'addr_width' : 10,
                  'data_width' : 64,
                  'data_type'  : 'Q',
                  'bram_name'  : 'dout_chnl_mean'}
###
inst_chnl_info0 = {'addr_width' : 10,
                   'data_width' : 32,
                   'data_type'  : 'i',
                   'bram_list'  : ['dout_chnl_real0', 'dout_chnl_imag0']}

inst_chnl_info1 = {'addr_width' : 10,
                   'data_width' : 32,
                   'data_type'  : 'i',
                   'bram_list' : ['dout_chnl_real1', 'dout_chnl_imag1']}
