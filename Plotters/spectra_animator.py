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

import sys, os, numexpr
from itertools import chain
sys.path.append('../Models')
sys.path.append(os.getcwd())
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
from spectrometer import Spectrometer
from animator import Animator

class SpectraAnimator(Animator):
    """
    Class responsable for drawing spectra plots.
    """
    def __init__(self):
        Animator.__init__(self)
        self.spectrometer = Spectrometer(self.settings)
        self.xlim = (0, self.settings.bw)
        self.ylim = (-100, 10)
        self.xlabel = 'Frequency [MHz]'
        self.ylabel = 'Power [dBFS]'
        self. titles = [spec['name'] for spec in self.settings.spec_info['spec_list']]
        
        n_brams = len(self.settings.spec_info['spec_list'][0]['bram_list'])
        channels = n_brams * 2**self.settings.spec_info['addr_width']
        self.xdata = np.linspace(0, self.settings.bw, channels, endpoint=False)

        n_plots = len(self.titles)
        self.fig, self.ax_arr = plt.subplots(*self.plot_map[n_plots])

    def get_data(self):
        """
        Gets the snapshot data form the spectrometer model.
        """
        return self.spectrometer.get_spectra()

    def add_widgets(self):
        """
        Modify the figure layout and add the widgets for the spectrometers.
        """
        # layout adjust
        self.fig.subplots_adjust(bottom=0.2)
        
        # reset button
        reset_button_ax = self.fig.add_axes([0.1, 0.08, 0.1, 0.04])
        self.reset_button = Button(reset_button_ax, 'Reset', color='lightgoldenrodyellow', hovercolor='0.975')
        def reset_button_on_clicked(mouse_event):
            self.spectrometer.reset_reg('cnt_rst')
        self.reset_button.on_clicked(reset_button_on_clicked)

        # acc_len textbox
        acc_len_textbox_ax = self.fig.add_axes([0.1, 0.02, 0.25, 0.04])
        self.acc_len_textbox = TextBox(acc_len_textbox_ax, 'acc_len', initial=str(self.spectrometer.fpga.read_int('acc_len')))
        def acc_len_textbox_on_submit(text):
            self.spectrometer.set_reg({'name':'acc_len', 'val':self.get_textbox_val(text)})
        self.acc_len_textbox.on_submit(acc_len_textbox_on_submit)

    def get_textbox_val(self, text):
        try:
            return int(numexpr.evaluate(text))
        except:
            raise Exception('Unable to parse value in textbox')

        
if __name__ == '__main__':
    animator = SpectraAnimator()
    animator.start_animation()
