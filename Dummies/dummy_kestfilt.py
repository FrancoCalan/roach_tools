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
        
        # get time-test info
        self.time_info_arr = []
        self.time_info_arr.append(self.settings.time_info_chnl)
        self.time_info_arr.append(self.settings.time_info_max)
        self.time_info_arr.append(self.settings.time_info_mean)

    def read(self, bram, nbytes, offset=0):                    
        for time_info in self.time_info_arr:
            if bram in time_info['bram_list']:
                n_data = self.get_n_data(nbytes, time_info['data_width'])
                
                # time data a + exp(b*x)
                a = np.random.random()
                b = -(1.0/n_data)*np.random.random()
                time_data = a + np.exp(b*range(n_data))

                return struct.pack('>'+str(n_data)+time_info['data_type'], *time_data)

        else:
            return DummySpectrometer.read(self, bram, nbytes, offset)
        
