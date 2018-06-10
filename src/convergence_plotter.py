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
from plotter import Plotter
from multi_line_axis import MultiLineAxis

class ConvergencePlotter(Plotter):
    """
    Class responsable for drawing power plots v/s time for filter output. 
    It includes channel power, max power, and mean power.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.nplots = 1
        self.legends = ['chnl', 'max', 'mean']
        mpl_axis = self.create_axes()[0]

        # get xdata
        n_specs = 2**self.settings.conv_info_chnl['addr_width']
        self.xdata = self.get_spec_time_arr(n_specs)

        # get current channel frequency for title
        chnl_freq = self.get_freq_from_channel(self.fpga.read_reg('channel'))
        title = 'Power v/s time\nChannel at freq: ' + str(chnl_freq)

        mpl_axis.set_title(title)
        mpl_axis.set_xlim(0, self.xdata[-1])
        mpl_axis.set_ylim((-100, 10))
        mpl_axis.set_xlabel('Time [$\mu$s]')
        mpl_axis.set_ylabel('Power [dBFS]')
        self.axes.append(MultiLineAxis(mpl_axis, self.xdata, self.legends))


    def get_data(self):
        """
        Gets the convergence analysis data. This includes single channel power,
        max channel power, and mean channel power.
        """
        # single channel
        [chnl_data_real, chnl_data_imag] = self.fpga.get_bram_list_data(self.settings.conv_info_chnl)
        chnl_data = chnl_data_real**2 + chnl_data_imag**2 # compute power
        chnl_data = self.linear_to_dBFS(chnl_data)
        
        # max channel
        max_data = self.fpga.get_bram_data(self.settings.conv_info_max)
        max_data = self.linear_to_dBFS(max_data)

        # mean channel
        mean_data = self.fpga.get_bram_data(self.settings.conv_info_mean)
        mean_data = self.linear_to_dBFS(mean_data)

        return [[chnl_data, max_data, mean_data]]

    def data2dict(self):
        """
        Creates dict with convergence data for file saving.
        """
        data_dict = {}

        data_arr = self.get_data()
        for i, data in enumerate(data_arr[0]):
            data_dict[self.legends[i] + ' ' + self.axes[0].ax.get_ylabel()] = data.tolist()
        
        data_dict[self.axes[0].ax.get_xlabel()] = self.xdata.tolist()
        data_dict['filter_gain'] = self.fpga.read_reg('filter_gain')
        data_dict['filter_acc'] = self.fpga.read_reg('filter_acc')
        return data_dict
