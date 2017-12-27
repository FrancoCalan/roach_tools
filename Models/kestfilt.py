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

import sys
import numpy as np
import struct
from spectrometer import Spectrometer
sys.path.append('../Dummies')
from dummy_kestfilt import DummyKestfilt

class Kestfilt(Spectrometer):
    """
    Helper class to read and write data from Kesteven filter.
    """
    def __init__(self, settings):
        Spectrometer.__init__(self, settings)

    def get_dummy_fpga(self, settings):
        """
        Create a dummy kestfilt to fetch fake data. For testing proposes.
        """
        return DummyKestfilt(settings)
        
    def get_time_data(self):
        """
        Returns data from time analysis. This includes single channel power,
        max channel power, and mean channel power.
        """
        # single channel
        [chnl_data_real, chnl_data_imag] = self.get_bram_data(self.settings.time_info_chnl)
        chnl_data = np.array(chnl_data_real)**2 + np.array(chnl_data_imag)**2 # compute power
        chnl_data = self.linear_to_dBFS(chnl_data)
        
        # max channel
        max_data = self.get_bram_data(self.settings.time_info_max)
        max_data = self.linear_to_dBFS(max_data)

        # mean channel
        mean_data = self.get_bram_data(self.settings.time_info_mean)
        mean_data = self.linear_to_dBFS(mean_data)

        return [chnl_data, max_data, mean_data]

    def get_bram_data(self, bram_info):
        """
        Receive and unpack data from FPGA using data information from bram_info.
        """
        bram_list = bram_info['name_list']
        width = bram_info['data_width']
        depth = 2**bram_info['addr_width']
        dtype = bram_info['data_type'] 

        bram_data_arr = []
        for bram in bram_list:
            bram_data = struct.unpack('>'+str(depth)+dtype, fpga.read(bram, depth*width/8, 0))
            bram_data_arr.append(bram_data)

        return bram_data_arr
