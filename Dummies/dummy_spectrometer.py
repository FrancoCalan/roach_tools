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

from itertools import chain
from dummy_roach import DummyRoach

class DummySpectrometer(DummyRoach):
    """
    Emulates an spectrometer implemented in ROACH. Used to deliver teset data.
    """
    def __init__(self, settings):
        DummyRoach.__init__()
        self.settings = settings
        
        # add registers from config file
        for reg in settings.set_regs:
            self.regs.append({'name':reg['name'], 'val':0})
        for reg in settings.reset_regs:
            self.regs.append({'name':reg, 'val':0})

        # get snapshots
        self.snapshots = chain.from_iterable(self.settings.snapshots): # flatten list
        
        # get spectrometers brams
        self.spec_brams = []
        for spec in self.settings.spec_info.spec_list:
            for bram in spec.bram_list:
                spec_brams.append(bram)


    def snapshot_get(self, snapshot, man_trig=True, man_valid=True):
        """
        Returns random snapshot signal.
        """
        if snapshot in self.snapshots:
            snap_data = self.gen_gaussian_array(mu=0, sigma=50, low=-128, 
                high=127, size=self.settings.snap_samples, dtype='>i1')
            return snap_data
        else:
            raise Exception("Snapshot not defined in config file.")
            
    def read(self, bram, size, offset=0):
        if bram in self.spec_brams:
            acc_len = [reg['val'] for reg in self.regs if reg['name']=='acc_len'][0]
            signal_arr = self.gen_gaussian_array(mu=0, sigma=0.25, low=-1, high=1,
                size=(acc_len, size), dtype='>f')

            spec_arr = np.fft.rfft(signal_arr, axis=1) / size
            spec = np.mean(spec_arr, axis=0)
            return spec

        else: 
            raise Exception("BRAM not defined in config file.")

    
