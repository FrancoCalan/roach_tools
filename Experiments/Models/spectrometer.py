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
from Dummies.dummy_spectrometer import DummySpectrometer

class Spectrometer(Snapshot):
    """
    Helper class to read and write data from spectrometer models.
    """
    def __init__(self, settings):
        Snapshot.__init__(self, settings)

    def get_dummy(self):
        """
        Gets dummy spectrometer fpga.
        """
        return DummySpectrometer(self.settings)
            
    def get_spectra(self):
        """
        Get spectra data from brams using the information specified in the
        config file.
        """
        bram_data_arr2d = self.get_bram_list2d_data(self.settings.spec_info)

        spec_data_arr = []
        for spec_data in bram_data_arr2d:
            spec_data = np.fromiter(chain(*zip(*spec_data)), dtype=self.settings.spec_info['data_type']) # interleave data
            spec_data = spec_data / float(self.fpga.read_int('acc_len')) # divide by accumulation
            spec_data = self.linear_to_dBFS(spec_data)
            spec_data_arr.append(spec_data)

        return spec_data_arr
            
    def linear_to_dBFS(self, data):
        return 10*np.log10(data+1) - self.settings.dBFS_const
