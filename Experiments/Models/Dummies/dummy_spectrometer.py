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
from itertools import chain
from dummy_snapshot import DummySnapshot

class DummySpectrometer(DummySnapshot):
    """
    Emulates a spectrometer implemented in ROACH. Used to deliver test data.
    """
    def __init__(self, settings):
        DummySnapshot.__init__(self,settings)
        
        # get spectrometers brams
        self.spec_brams = list(chain.from_iterable(self.settings.spec_info['bram_list2d'])) # flatten list
            
    def read(self, bram, nbytes, offset=0):
        """
        Return spectra of generator signal accumulated acc_len times.
        """
        if bram in self.spec_brams:
            acc_len = self.read_int('acc_len')
            spec_len = get_n_data(nbytes, self.settings.spec_info['data_width'])
            spec = np.zeros(spec_len)
            for _ in range(acc_len):
                signal = self.get_generator_signal(2*spec_len)
                spec += np.abs(np.fft.rfft(signal)[:spec_len])
            spec = spec / acc_len
            return struct.pack('>'+str(spec_len)+self.settings.spec_info['data_type'], *spec)

        else: 
            raise Exception("BRAM not defined in config file.")

def get_n_data(nbytes, data_width):
    """
    Computes the number of data values given the total number of
    bytes in the data array, and data width in bits.
    """
    return 8 * nbytes / data_width
