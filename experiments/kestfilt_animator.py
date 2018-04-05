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
import Tkinter as Tk
from calanfpga import CalanFpga
from spectra_animator import SpectraAnimator
from convergence_plotter import ConvergencePlotter
from stability_plotter import StabilityPlotter

class KestfiltAnimator(SpectraAnimator):
    """
    Class responsable for drawing spectra plots in a Kestfilt implementation.
    """
    def __init__(self, calanfpga):
        SpectraAnimator.__init__(self, calanfpga)

    def create_window(self):
        """
        Create window and add widgets.
        """
        SpectraAnimator.create_window(self)
        
        # filter_on button
        self.filter_on_label = Tk.StringVar()
        if self.fpga.read_reg('filter_on') == 0:
            self.filter_on_label.set('Filter off')
        else:
            self.filter_on_label.set('Filter on')
        self.filter_on_button = Tk.Button(self.button_frame, textvariable=self.filter_on_label, command=self.toggle_filter)
        self.filter_on_button.pack(side=Tk.LEFT)

        # plot conv button
        self.plot_conv_button = Tk.Button(self.button_frame, text='Plot conv', command=self.plot_convergence)
        self.plot_conv_button.pack(side=Tk.LEFT)

        # plot stab button
        self.plot_stab_button = Tk.Button(self.button_frame, text='Plot stab', command=self.plot_stability)
        self.plot_stab_button.pack(side=Tk.LEFT)
       
        # filter_gain entry
        self.add_reg_entry('filter_gain')

        # filter_acc entry
        self.add_reg_entry('filter_acc')

        # channel entry
        self.add_reg_entry('channel')

    def data2dict(self):
        """
        Creates dict with kestfilt data for file saving.
        """
        data_dict = SpectraAnimator.data2dict(self)
        data_dict['filter_gain'] = self.fpga.read_reg('filter_gain')
        data_dict['filter_acc'] = self.fpga.read_reg('filter_acc')
        return data_dict

    def toggle_filter(self):
        if self.fpga.read_reg('filter_on') == 1:
            self.fpga.set_reg('filter_on', 0)
            self.filter_on_label.set('Filter Off')
            print('Filter is off')
        else:
            self.fpga.set_reg('filter_on', 1)
            self.filter_on_label.set('Filter On')
            print('Filter is on')

    def plot_convergence(self):
        ConvergencePlotter(self.fpga).plot()

    def plot_stability(self):
        StabilityPlotter(self.fpga).plot()

if __name__ == '__main__':
    fpga = CalanFpga()
    fpga.initialize()
    KestfiltAnimator(fpga).start_animation()
