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
from itertools import chain
import struct
from model import Model
sys.path.append('../Dummies')
from dummy_spectrometer import DummySpectrometer

class Spectrometer(Model):
    """
    Helper class to read and write data from spectrometer models.
    """
    def __init__(self, settings):
        Model.__init__(self, settings)

    def get_dummy_fpga(self, settings):
        """
        Create a dummy spectrometer to fetch fake data. For testing proposes.
        """
        return DummySpectrometer(settings)

    def get_snapshot(self):
        """
        Get snapshot data from all snapshot blocks specified in the config 
        file.
        """
        snap_data_arr = []
        for snapshot in chain.from_iterable(self.settings.snapshots): # flatten list
            snap_data = np.fromstring(self.fpga.snapshot_get(snapshot, man_trig=True, 
                man_valid=True)['data'], dtype='>i1')[0:self.settings.snap_samples]
            snap_data_arr.append(snap_data)

        return snap_data_arr
            
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
            spec_data = 10*np.log10(spec_data+1) - self.settings.dBFS_const # transform to dBFS
            spec_data_arr.append(spec_data)

        return spec_data_arr
