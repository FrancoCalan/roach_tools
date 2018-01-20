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
from Dummies.dummy_kestfilt import DummyKestfilt

class Kestfilt(Spectrometer):
    """
    Helper class to read and write data from Kesteven filter.
    """
    def __init__(self, settings):
        Spectrometer.__init__(self, settings)

    def get_dummy(self):
        """
        Gets dummy kestfilt fpga.
        """
        return DummyKestfilt(self.settings)

    def get_convergence_data(self):
        """
        Returns data for convergence analysis. This includes single channel power,
        max channel power, and mean channel power.
        """
        # single channel
        [chnl_data_real, chnl_data_imag] = self.get_bram_data(self.settings.conv_info_chnl)
        chnl_data = np.array(chnl_data_real)**2 + np.array(chnl_data_imag)**2 # compute power
        chnl_data = self.linear_to_dBFS(chnl_data)
        
        # max channel
        max_data = self.get_bram_data(self.settings.conv_info_max)
        max_data = self.linear_to_dBFS(max_data)

        # mean channel
        mean_data = self.get_bram_data(self.settings.conv_info_mean)
        mean_data = self.linear_to_dBFS(mean_data)

        return [chnl_data, max_data, mean_data]

    def get_stability_data(self):
        """
        Gets the complex data from a single channel within consecutive instantaneous spectra
        for different inputs. Then computes the magnitude ratio and angle difference.
        """
        [chnl0_data_real, chnl0_data_imag] = self.get_bram_data(self.settings.inst_chnl_info0)
        [chnl1_data_real, chnl1_data_imag] = self.get_bram_data(self.settings.inst_chnl_info1)

        chnl0_data = np.array(chnl0_data_real) + 1j*np.array(chnl0_data_imag)
        chnl1_data = np.array(chnl1_data_real) + 1j*np.array(chnl0_data_imag)

        stability_data = chnl1_data / chnl0_data

        return [np.abs(stability_data), np.angle(stability_data, deg=True)]

    def get_bram_data(self, bram_info):
        """
        Receive and unpack data from FPGA using data information from bram_info.
        """
        bram_list = bram_info['bram_list']
        width = bram_info['data_width']
        depth = 2**bram_info['addr_width']
        dtype = bram_info['data_type'] 

        bram_data_arr = []
        for bram in bram_list:
            bram_data = struct.unpack('>'+str(depth)+dtype, self.fpga.read(bram, depth*width/8, 0))
            bram_data_arr.append(np.array(bram_data))

        if len(bram_data_arr)==1:
            return bram_data_arr[0]
            
        return bram_data_arr
