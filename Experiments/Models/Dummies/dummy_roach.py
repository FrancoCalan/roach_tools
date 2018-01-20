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
from dummy_generator import DummyGenerator

class DummyRoach():
    """
    Emulates a ROACH connection. Is used for debugging purposes for the rest
    of the code.
    """
    def __init__(self, settings):
        self.settings = settings
        self.generator = DummyGenerator(1.0/(2*self.settings.bw*1e6))
        self.regs = []

    def is_connected(self):
        """
        Emulates ROACH connection test. Always True.
        """
        return True

    def upload_program_bof(self, boffile):
        """
        Emulates programming of the FPGA. Does nothing.
        """
        pass

    def est_brd_clk(self):
        """
        Emulates FPGA clock estimation.
        """
        return 2*self.settings.bw

    def write_int(self, reg_name, val):
        """
        Writes an int value into the Dummy ROACH.
        """
        try:
            write_reg = [reg for reg in self.regs if reg['name'] == reg_name][0]
        except:
            raise Exception('No register found with name ' + reg_name)
        write_reg['val'] = val

    def read_int(self, reg_name):
        """
        Reads the int value from the Dummy ROACH.
        """
        try:
            return [reg['val'] for reg in self.regs if reg['name'] == reg_name][0]
        except:
            raise Exception('No register found with name ' + reg_name)
    
    def get_generator_signal(self, nsamples):
        """
        Get the generator signal, clipped to simulate ADC saturation, and casted to the
        corresponding type to simulate ADC bitwidth.
        """
        signal = np.clip(self.generator.get_signal(nsamples), -128, 127)
        return signal.astype('>i1')
