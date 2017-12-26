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

class DummyRoach():
    """
    Emulates a ROACH connection. Is used for debugging purposes for the rest
    of the code.
    """
    def __init__(self):
        self.clk = 1
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
        return self.clk

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

    def gen_gaussian_array(self, mu, sigma, low, high, size, dtype='>i1'):
        """
        Returns an array with Gaussian (normal distributed) values. Values can
        be clipped (saturated), and the data type can be defined, in order to 
        emulate ADC values.

        Parameters
        ----------
        mu : float
            Mean of Gaussian distribution.
        sigma : float
            Standard deviation of Gaussian distribution.
        low : float
            Lower limit for data values (inclusive).
        high : float
            Upper limit for data values (inclusive).
        size : int or array
            Size of the array.
        dtype : dtype
            Data type of the array.

        Returns
        -------
        array
            Array with the Gaussian values.
        """
        try:
            signal = sigma * np.random.randn(size) + mu  # single axis
        except:
            signal = sigma * np.random.randn(*size) + mu # multi axis
        signal = np.clip(signal, low, high)
        return signal.astype(dtype)
