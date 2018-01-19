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

import struct
import numpy as np
from dummy_spectrometer import DummySpectrometer

class DummyKestfilt(DummySpectrometer):
    """
    Emulates a Kesteven filter implemented in ROACH. Used to deliver test data.
    """
    def __init__(self, settings):
        DummySpectrometer.__init__(self, settings)

    def read(self, bram, nbytes, offset=0):
        # get conv_info
        conv_info_arr = []
        conv_info_arr.append(self.settings.conv_info_chnl)
        conv_info_arr.append(self.settings.conv_info_max)
        conv_info_arr.append(self.settings.conv_info_mean)

        # get inst_chnl_info
        inst_chnl_info_arr = []
        inst_chnl_info_arr.append(self.settings.inst_chnl_info0)
        inst_chnl_info_arr.append(self.settings.inst_chnl_info1)
        
        for conv_info in conv_info_arr:
            if bram in conv_info['bram_list']:
                n_data = self.get_n_data(nbytes, conv_info['data_width'])
                
                # conv data a + exp(b*x)
                a = 10
                b = -(100.0/n_data)*np.random.random()
                conv_data = np.exp(a*np.exp((b*np.arange(n_data)))) + np.random.random(n_data)

                return struct.pack('>'+str(n_data)+conv_info['data_type'], *conv_data)

        for inst_chnl_info in inst_chnl_info_arr:
            if bram in inst_chnl_info['bram_list']:
                n_data = self.get_n_data(nbytes, inst_chnl_info['data_width'])
                inst_chnl_data = 10 * (np.random.random(n_data)+1)
                return struct.pack('>'+str(n_data)+inst_chnl_info['data_type'], *inst_chnl_data)
                
        return DummySpectrometer.read(self, bram, nbytes, offset)
        
