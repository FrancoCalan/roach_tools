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

import sys, os
sys.path.append(os.getcwd())
import numpy as np
from plotter import Plotter

class StabilityPlotter(Plotter):
    """
    Class responsable for drawing magnitude ratio and angle difference
    in order to visualize the stability between two signals.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.ylims = [(-1, 10), (-200, 200)]
        self.xlabel = 'Time [$\mu$s]'
        self.ylabels = ['Magnitude ratio', 'Angle difference [deg]']

        # get xdata
        n_specs = 2**self.settings.inst_chnl_info['addr_width']
        self.xdata = self.get_spec_time_arr(n_specs)
        self.xlim = (0, self.xdata[-1])

        # get current channel frequency for title
        chnl_freq = self.settings.bw * self.fpga.read_reg('channel') / self.get_nchannels()
        self.titles = ['Channel at freq: ' + str(chnl_freq), 
                       'Channel at freq: ' + str(chnl_freq)]
        self.nplots = len(self.titles)

    def get_data(self):
        """
        Gets the complex data from a single channel within consecutive instantaneous spectra
        for different inputs. Then computes the magnitude ratio and angle difference.
        """
        [[chnl0_data_real, chnl0_data_imag], [chnl1_data_real, chnl1_data_imag]] =\
            self.fpga.get_bram_list2d_data(self.settings.inst_chnl_info)

        chnl0_data = np.array(chnl0_data_real) + 1j*np.array(chnl0_data_imag)
        chnl1_data = np.array(chnl1_data_real) + 1j*np.array(chnl0_data_imag)

        stability_data = chnl1_data / chnl0_data

        return [np.abs(stability_data), np.angle(stability_data, deg=True)]

    def data2dict(self):
        """
        Creates dict with stability data for file saving.
        """
        data_dict = {}

        data_arr = self.get_data()
        for i, data in enumerate(data_arr):
            data_dict[self.titles[i] + ' ' + self.ylabels[i]] = data.tolist()

        data_dict[self.xlabel] = self.xdata.tolist()

        return data_dict
