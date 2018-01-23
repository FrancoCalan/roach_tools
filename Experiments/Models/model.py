###############################################################################
#                                                                             #
#   Millimeter-wave Laboratory, Department of Astronomy, University of Chile  #
#   http://www.das.uchile.cl/lab_mwl                                          #
#   Copyright (C) 2017 Franco Curotto                                         #
#                                                                             #
#   This program is free software; you can redistribute it and/or modify      #
#   it under the terms of the GNU General Public License as published by      #
#   the Free Software Foundation; either version 3 of the License, or         #
#   (at your option) any later version.                                       #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU General Public License for more details.                              #
#                                                                             #
#   You should have received a copy of the GNU General Public License along   #
#   with this program; if not, write to the Free Software Foundation, Inc.,   #
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.               #
#                                                                             #
###############################################################################

import time, struct
import numpy as np
import corr
#import adc5g

class Model():
    """
    Helper class used to initialize, program the FPGA, and read and write data
    from the ROACH.
    """
    def __init__(self, settings):
        self.settings = settings
        if self.settings.simulated:
            self.fpga = self.get_dummy()
        else:
            self.fpga = corr.katcp_wrapper.FpgaClient(self.settings.roach_ip, self.settings.roach_port)
            time.sleep(1)

    def initialize_roach(self):
        self.connect_to_roach()
        if self.settings.program:
            self.upload_and_program()
        self.estimate_clock()
        self.set_reset_regs()

    def connect_to_roach(self):
        """
        Verify communication with ROACH.
        """
        print 'Connecting to ROACH server %s on port %i... ' %(self.settings.roach_ip, self.settings.roach_port),
        if self.fpga.is_connected():
            print 'ok'
        else:
            raise Exception('Unable to connect to ROACH.')

    def upload_and_program(self):
        """
        Upload to RAM and program the .bof model to de FPGA.
        """
        print 'Uploading and programming FPGA with %s... ' %self.settings.boffile,
        self.fpga.upload_bof(self.settings.boffile, 60000)
        self.fpga.progdev(self.settings.boffile)
        time.sleep(0.1)
        print 'done'

    def estimate_clock(self):
        """
        Estimate FPGA clock
        """
        print 'Estimating FPGA clock: ' + str(self.fpga.est_brd_clk()) + '[MHz]'

    #def calibrate_adc(self):
    #    print 'Calibrating ADC0... ', 
    #    if self.settings.cal_adc[0]:
    #        adc5g.calibrate_mmcm_phase(fpga, 0, settings.snap_names[0])
    #        time.sleep(0.1)
    #        print 'done'
    #    else:
    #        print 'skipped'

    #    print 'Calibrating ADC1... ', 
    #    if self.settings.cal_adc[0]:
    #        adc5g.calibrate_mmcm_phase(fpga, 1, settings.snap_names[1])
    #        time.sleep(0.1)
    #        print 'done'
    #    else:
    #        print 'skipped'

    def set_reset_regs(self):
        """
        Set registers to a given value and reset registers (->1->0). The registers
        used come from the corresponding list in the configuration file.
        """
        print 'Setting registers:'
        for reg in self.settings.set_regs:
            self.set_reg(reg['name'], reg['val'])
            
        print 'Resetting registers:'
        for reg in self.settings.reset_regs:
            self.reset_reg(reg)

        print 'Done setting and reseting registers'

    def set_reg(self, reg, val):
        """
        Set register.
        """
        print '\tSetting %s to %i... ' %(reg, val),
        self.fpga.write_int(reg, val)
        time.sleep(0.1)
        print 'done'

    def reset_reg(self, reg):
        """
        Reset register.
        """
        print '\tResetting %s... ' %reg,
        self.fpga.write_int(reg, 1)
        time.sleep(0.1)
        self.fpga.write_int(reg, 0)
        time.sleep(0.1)
        print 'done'

    def get_bram_data(self, bram_info):
        """
        Receive and unpack data from FPGA using data information from bram_info.
        The bram_info dictionary format is:
        {'addr_width' : width of bram address in bits.
         'data_width' : width of bram data (word) in bits.
         'data_type'  : data type in struct format ('b', 'B', 'h', etc.)
         'bram_name'  : bram name in the model
        }
        """
        width = bram_info['data_width']
        depth = 2**bram_info['addr_width']
        dtype = bram_info['data_type'] 
        bram  = bram_info['bram_name']
        ndata = (width / type2bits[dtype]) * depth

        bram_data = struct.unpack('>'+str(ndata)+dtype, self.fpga.read(bram, depth*width/8, 0))
        return np.array(bram_data)

    def get_bram_list_data(self, bram_info):
        """
        Similar to get_bram_data but it gets the data from a list of bram. In this case
        'bram_name' is 'bram_list', a list of bram names. Returns the data in a list
        of the same size.
        """
        bram_data_arr = []
        for bram in bram_info['bram_list']:
            # make a new bram info only with current bram
            current_bram_info = bram_info
            current_bram_info['bram_name'] = bram
            bram_data = self.get_bram_data(current_bram_info)
            bram_data_arr.append(bram_data)

        return bram_data_arr

    def get_bram_list2d_data(self, bram_info):
        """
        Similar to get_bram_list_data but it gets the data from a list of list of brams.
        In this case 'bram_list' is 'bram_list2d', a 2d list of bram names. Returns the 
        data in a list of the same dimansions.
        """
        bram_data_arr2d = []
        for bram_list in bram_info['bram_list2d']:
            # make a new bram info only with current bram_list
            current_bram_info = bram_info
            current_bram_info['bram_list'] = bram_list
            bram_data_arr = self.get_bram_list_data(current_bram_info)
            bram_data_arr2d.append(bram_data_arr)

        return bram_data_arr2d

type2bits = {'b' :  8, 'B' :  8,
             'h' : 16, 'H' : 16,
             'i' : 32, 'I' : 32,
             'q' : 64, 'Q' : 64} 
