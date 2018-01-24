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
sys.path.append(os.getcwd())
import numpy as np
import matplotlib.pyplot as plt
import Tkinter as Tk
from Models.spectrometer import Spectrometer
from animator import Animator

class SpectraAnimator(Animator):
    """
    Class responsable for drawing spectra plots.
    """
    def __init__(self):
        Animator.__init__(self)
        self.titles = self.settings.plot_titles
        self.nplots = len(self.titles) 
        self.xlim = (0, self.settings.bw)
        self.ylims = self.nplots * [(-100, 10)]
        self.xlabel = 'Frequency [MHz]'
        self.ylabels = self.nplots * ['Power [dBFS]']
        self.entries = []
        
        nchannels = get_nchannels(self.settings.spec_info)
        self.xdata = np.linspace(0, self.settings.bw, nchannels, endpoint=False)
        
    def get_model(self, settings):
        """
        Get spectrometer model for animator.
        """
        return Spectrometer(settings)
        
    def get_data(self):
        """
        Gets the snapshot data form the spectrometer model.
        """
        return self.model.get_spectra()

    def create_window(self):
        """
        Create window and add widgets.
        """
        Animator.create_window(self)

        # reset button
        self.reset_button = Tk.Button(self.button_frame, text='Reset', command=lambda: self.model.reset_reg('cnt_rst'))
        self.reset_button.pack(side=Tk.LEFT)

        # acc_len entry
        self.add_reg_entry('acc_len')

    def add_reg_entry(self, reg):
        """
        Add a text entry for modifying regiters in models."
        """
        frame = Tk.Frame(master=self.root)
        frame.pack(side = Tk.TOP, anchor="w")
        label = Tk.Label(frame, text=reg+":")
        label.pack(side=Tk.LEFT)
        entry = Tk.Entry(frame)
        entry.insert(Tk.END, self.model.fpga.read_int(reg))
        entry.pack(side=Tk.LEFT)
        entry.bind('<Return>', lambda x: self.set_reg_from_entry(reg, entry))
        self.entries.append(entry)

    def set_reg_from_entry(self, reg, entry):
        """
        Modify a model register from the value of an entry.
        """
        string_val = entry.get()
        try:
            val = int(numexpr.evaluate(string_val))
        except:
            raise Exception('Unable to parse value in textbox')
        self.model.set_reg(reg, val)

def get_nchannels(selc_info):
    """
    Compute the number of channels of an spetrum given the spec_info
    """
    n_brams = len(spec_info['bram_list2d'][0])
    return n_brams * 2**self.settings.spec_info['addr_width']
        
if __name__ == '__main__':
    animator = SpectraAnimator()
    animator.model.initialize_roach()
    animator.start_animation()
