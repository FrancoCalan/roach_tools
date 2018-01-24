#!/usr/bin/env python

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

import time
import numpy as np
from spectra_animator import SpectraAnimator, get_nchannels
from Generator.generator import Generator

class AdcSynchronatorFreq(Experiment):
    """
    This class is used to syncronize two ADC using spectra data.
    """
    def __init__(self):
        Experiment.__init__(self):
        self.spectra_animator = SpectraAnimator()
        self.source = Generator(self.settings.source_ip, self.settings.source_port)

    def get_model(self):
        return AdcSyncFreq(self.settings)

    def synchronize_adcs(self):
        nchannels = get_nchannels(spec_info_pow)
        freqs = np.linspace(0, self.settings.bw, nchannels, endpoint=False)

        for chnl, freq in zip(range(1, nchannels) freqs[1:]):
            # change frequency
            self.source.change_freq_mhz(freq)
            time.sleep(0.1)

            # get data
            [spec_]
            
