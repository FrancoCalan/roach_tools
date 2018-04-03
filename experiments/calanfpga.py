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

import os, sys, importlib, time, struct
import numpy as np
from itertools import chain
import corr
from dummies.dummy_fpga import DummyFpga

class CalanFpga():
    """
    Wrapper around corr's FpgaClient in order to add common functions used in 
    Calan Lab (Millimeter Wave Laboratory, Univerity of Chile). Examples of the
    funtions added are: roach initialization, regiter setting/reseting, easy data
    grab from multiple snapshots, bram arrays, interleaved bram arrays, etc.
    """
    def __init__(self):
        config_file = os.path.splitext(sys.argv[1])[0]
        self.settings = importlib.import_module(config_file)
        if self.settings.simulated:
            self.fpga = DummyFpga(self.settings)
        else:
            self.fpga = corr.katcp_wrapper.FpgaClient(self.settings.roach_ip, self.settings.roach_port)
            time.sleep(1)

    def initialize(self):
        """
        Performs a standard ROACH initialization: Check connection,
        upload and program bof if requested, estimate clock, and
        set and resset the inital state of register listed in the 
        configuration file.
        """
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
        Upload to RAM and program the .bof/.bof.gz model to the FPGA.
        """
        print 'Uploading and programming FPGA with %s... ' %self.settings.boffile,
        time.sleep(0.5)
        self.fpga.upload_bof(self.settings.boffile, 60000, force_upload=True)
        time.sleep(0.5)
        self.fpga.progdev(self.settings.boffile)
        time.sleep(0.5)
        print 'done'

    def estimate_clock(self):
        """
        Estimate FPGA clock
        """
        print 'Estimating FPGA clock: ' + str(self.fpga.est_brd_clk()) + '[MHz]'

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

    def read_reg(self, reg):
        """
        Read register.
        """
        reg_val = self.fpga.read_int(reg)
        return reg_val

    def get_snapshots(self):
        """
        Get snapshot data from all snapshot blocks specified in the config 
        file.
        """
        snap_data_arr = []
        for snapshot in self.settings.snapshots:
            snap_data = np.fromstring(self.fpga.snapshot_get(snapshot, man_trig=True, 
                man_valid=True)['data'], dtype='>i1')
            snap_data_arr.append(snap_data)
        
        return snap_data_arr

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
        data in a list of the same dimensions.
        """
        bram_data_arr2d = []
        for bram_list in bram_info['bram_list2d']:
            # make a new bram info only with current bram_list
            current_bram_info = bram_info
            current_bram_info['bram_list'] = bram_list
            bram_data_arr = self.get_bram_list_data(current_bram_info)
            bram_data_arr2d.append(bram_data_arr)

        return bram_data_arr2d

    def get_bram_interleaved_data(self, bram_info):
        """
        Get data using get_bram_list_data and then interleave the data. Useful for easily 
        getting data from a spectrometer.
        """
        bram_data_arr = self.get_bram_list_data(bram_info)
        interleaved_data = np.fromiter(chain(*zip(*bram_data_arr)), dtype=bram_info['data_type'])
        return interleaved_data

    def get_bram_list_interleaved_data(self, bram_info):
        """
        Get data from a list of a list of interleaved data brams and return the data in a 1d list.
        Useful to easily get data from multiple spectrometer implemented in the same FPGA, and with
        the same data type.
        """
        interleaved_data_arr = []
        for bram_list in bram_info['bram_list2d']:
            # make a new bram info only with current bram_list
            current_bram_info = bram_info
            current_bram_info['bram_list'] = bram_list
            interleaved_data = self.get_bram_interleaved_data(current_bram_info)
            interleaved_data_arr.append(interleaved_data)

        return interleaved_data_arr
            
type2bits = {'b' :  8, 'B' :  8,
             'h' : 16, 'H' : 16,
             'i' : 32, 'I' : 32,
             'q' : 64, 'Q' : 64} 
