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
sys.path.append(os.getcwd())
from itertools import chain
import numpy as np
import Tkinter as Tk
from animator import Animator

class SpectraAnimator(Animator):
    """
    Class responsable for drawing spectra plots.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.titles = self.settings.plot_titles
        self.nplots = len(self.titles) 
        self.xlim = (0, self.settings.bw)
        self.ylims = self.nplots * [(-100, 10)]
        self.xlabel = 'Frequency [MHz]'
        self.ylabels = self.nplots * ['Power [dBFS]']
        self.entries = []
        
        nchannels = self.get_nchannels()
        self.xdata = np.linspace(0, self.settings.bw, nchannels, endpoint=False)
        
    def get_data(self):
        """
        Gets the spectra data form the spectrometer model.
        """
        spec_data_arr = self.fpga.get_bram_list_interleaved_data(self.settings.spec_info)
        spec_plot_arr = []
        for spec_data in spec_data_arr:
            spec_data = spec_data / float(self.fpga.read_reg('acc_len')) # divide by accumulation
            spec_data = self.linear_to_dBFS(spec_data)
            spec_plot_arr.append(spec_data)

        return spec_plot_arr

    def create_window(self):
        """
        Create window and add widgets.
        """
        Animator.create_window(self)

        # reset button
        self.reset_button = Tk.Button(self.button_frame, text='Reset', command=lambda: self.fpga.reset_reg('cnt_rst'))
        self.reset_button.pack(side=Tk.LEFT)

        # acc_len entry
        self.add_reg_entry('acc_len')

    def data2dict(self):
        """
        Creates dict with spectrometer data for file saving.
        """
        data_dict = {}
        
        data_arr = self.get_data()
        for i, data in enumerate(data_arr):
            data_dict[self.titles[i] + ' ' + self.ylabels[i]] = data.tolist()

        data_dict['acc_len'] = self.fpga.read_reg('acc_len')
        data_dict[self.xlabel] = self.xdata.tolist()

        return data_dict

    def add_reg_entry(self, reg):
        """
        Add a text entry for modifying regiters in FPGA."
        """
        frame = Tk.Frame(master=self.root)
        frame.pack(side = Tk.TOP, anchor="w")
        label = Tk.Label(frame, text=reg+":")
        label.pack(side=Tk.LEFT)
        entry = Tk.Entry(frame)
        entry.insert(Tk.END, self.fpga.read_reg(reg))
        entry.pack(side=Tk.LEFT)
        entry.bind('<Return>', lambda x: self.set_reg_from_entry(reg, entry))
        self.entries.append(entry)

    def set_reg_from_entry(self, reg, entry):
        """
        Modify a FPGA register from the value of an entry.
        """
        string_val = entry.get()
        try:
            val = int(numexpr.evaluate(string_val))
        except:
            raise Exception('Unable to parse value in textbox')
        self.fpga.set_reg(reg, val)