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

import numpy as np
from itertools import chain
import struct
from snapshot import Snapshot

class Spectrometer(Snapshot):
    """
    Helper class to read and write data from spectrometer models.
    """
    def __init__(self, settings, dummy_spectrometer):
        Snapshot.__init__(self, settings, dummy_spectrometer)
            
    def get_spectra(self):
        """
        Get spectra data from brams using the information specified in the
        config file.
        """
        width = self.settings.spec_info['data_width']
        depth = 2**self.settings.spec_info['addr_width']
        dtype = self.settings.spec_info['data_type']

        spec_data_arr = []
        for spec in self.settings.spec_info['spec_list']:
            bram_data_arr = []
            for bram in spec['bram_list']:
                bram_data = struct.unpack('>'+str(depth)+dtype, self.fpga.read(bram, 
                    depth*width/8, 0))
                bram_data_arr.append(bram_data)
            spec_data = np.fromiter(chain(*zip(*bram_data_arr)), dtype=dtype) # interleave data
            spec_data = spec_data / float(self.fpga.read_int('acc_len')) # divide by accumulation
            spec_data = self.linear_to_dBFS(spec_data)
            spec_data_arr.append(spec_data)

        return spec_data_arr

    def linear_to_dBFS(self, data):
        return 10*np.log10(data+1) - self.settings.dBFS_const
