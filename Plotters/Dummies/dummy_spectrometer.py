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
        self.spec_brams = []
        for spec in self.settings.spec_info['spec_list']:
            for bram in spec['bram_list']:
                self.spec_brams.append(bram)

            
    def read(self, bram, nbytes, offset=0):
        """
        Return random spectra added by acc_len.
        """
        if bram in self.spec_brams:
            acc_len = [reg['val'] for reg in self.regs if reg['name']=='acc_len'][0]
            spec_len = self.get_n_data(nbytes, self.settings.spec_info['data_width'])
            signal_arr = self.gen_gaussian_array(mu=0, sigma=0.25, low=-1, high=1,
                size=(acc_len, 2*spec_len), dtype='>f')

            spec_arr = np.abs(np.fft.rfft(signal_arr, axis=1)[:, :spec_len])
            spec = np.sum(spec_arr, axis=0)
            return struct.pack('>'+str(spec_len)+self.settings.spec_info['data_type'], *spec)

        else: 
            raise Exception("BRAM not defined in config file.")

    def get_n_data(self, nbytes, data_width):
        return 8 * nbytes / data_width
