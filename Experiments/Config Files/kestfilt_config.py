# Basic settings
simulated  = True
roach_ip   = '192.168.1.12'
roach_port = 7147
program    = True
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
               [['dout0_0', 'dout0_1', 'dout0_2', 'dout0_3', 'dout0_4', 'dout0_5', 'dout0_6', 'dout0_7'],
                ['dout1_0', 'dout1_1', 'dout1_2', 'dout1_3', 'dout1_4', 'dout1_5', 'dout1_6', 'dout1_7'],
                ['dout2_0', 'dout2_1', 'dout2_2', 'dout2_3', 'dout2_4', 'dout2_5', 'dout2_6', 'dout2_7']]}

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
