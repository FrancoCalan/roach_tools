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
from Models.kestfilt import Kestfilt
from plotter import Plotter

class ConvergencePlotter(Plotter):
    """
    Class responsable for drawing power plots v/s time for filter output. 
    It includes channel power, max power, and mean power.
    """
    def __init__(self):
        Plotter.__init__(self)
        self.nplots = 1
        self.ylims = [(-100, 10)]
        self.xlabel = 'Time [$\mu$s]'
        self.ylabels = ['Power [dBFS]']
        self.legends = [self.settings.conv_info_chnl['name'], 
                        self.settings.conv_info_max['name'], 
                        self.settings.conv_info_mean['name']]

        # get xdata
        n_specs = 2**self.settings.conv_info_chnl['addr_width']
        self.xdata = self.get_spec_time_arr(n_specs)
        self.xlim = (0, self.xdata[-1])

        # get current channel frequency for title
        chnl_freq = self.xdata[self.model.fpga.read_int('channel')]
        self.titles = ['Power v/s time\nChannel at freq:' + str(chnl_freq)]

    def get_model(self):
        """
        Get kestfilt model for plotter.
        """
        return Kestfilt(self.settings)

    def get_data(self):
        """
        Gets the stability data from kestfilt.
        """
        return self.model.get_convergence_data()

if __name__ == '__main__':
    plotter = PowerPlotter()
    plotter.plot()
