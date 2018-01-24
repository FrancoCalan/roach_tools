# Basic Settings
simulated  = True
roach_ip   = '192.168.1.12'
roach_port = 7147
program    = False
boffile    = ''
set_regs   = [{'name' : 'cal_acc_len' : 'val' : 2**12},
              {'name' : 'acc_gain'    : 'val' : 2**32-1}]
reset_regs = ['cnt_rst']
bw         = 800

# Snapshot settings
snapshots  = [['adcsnap0'], ['adcsnap1']]
snap_samples = 256

# Spectrometer Settings
spec_info_pow  = {'addr_width'  : 10
                  'data_width'  : 64
                  'data_type'   : 'Q'
                  'bram_list2d' : 
                  [['x1_aa', 'x2_aa', 'x3_aa', 'x4_aa', 'x5_aa', 'x6_aa', 'x7_aa', 'x8_aa'],
                   ['x1_bb', 'x2_bb', 'x3_bb', 'x4_bb', 'x5_bb', 'x6_bb', 'x7_bb', 'x8_bb']]}

spec_info_prod = {'addr_width'  : 10
                 'data_width'  : 64
                 'data_type'   : 'q'
                 'bram_list2d' : 
                 [['x1_abr', 'x2_abr', 'x3_abr', 'x4_abr', 'x5_abr', 'x6_abr', 'x7_abr', 'x8_abr'],
                  ['x1_abi', 'x2_abi', 'x3_abi', 'x4_abi', 'x5_abi', 'x6_abi', 'x7_abi', 'x8_abi']]}

# Sync Settings
source_ip   = '192.168.1.34'
source_port = 5025
