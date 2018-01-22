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
        """
        bram_list = bram_info['bram_list']
        width = bram_info['bram_width']
        depth = 2**bram_info['addr_width']
        dtype = bram_info['data_type'] 
        ndata = (width / type2bits[dtype]) * depth

        bram_data_arr = []
        for bram in bram_list:
            bram_data = struct.unpack('>'+str(ndata)+dtype, self.fpga.read(bram, depth*width/8, 0))
            bram_data_arr.append(np.array(bram_data))

        if len(bram_data_arr)==1:
            return bram_data_arr[0]
            
        return bram_data_arr

type2bits = {'b' :  8, 'B' :  8,
             'h' : 16, 'H' : 16,
             'i' : 32, 'I' : 32,
             'q' : 64, 'Q' : 64} 
