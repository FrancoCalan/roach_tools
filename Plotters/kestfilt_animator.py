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
sys.path.append('../Models')
sys.path.append(os.getcwd())
import numpy as np
import matplotlib.pyplot as plt
import Tkinter as Tk
from kestfilt import Kestfilt
from spectra_animator import SpectraAnimator

class KestfiltAnimator(SpectraAnimator):
    """
    Class responsable for drawing spectra plots.
    """
    def __init__(self):
        SpectraAnimator.__init__(self)

    def get_model(self, settings):
        """
        Get kestfilt model for animator.
        """
        return Kestfilt(settings)

    
    def get_data(self):
        """
        Gets the snapshot data form the spectrometer model.
        """
        return self.model.get_spectra()

    def create_window(self):
        """
        Create window and add widgets.
        """
        SpectraAnimator.create_window(self)
        
        # filter_on button
        self.filter_on_label = Tk.StringVar()
        if self.model.fpga.read_int('filter_on') == 0:
            self.filter_on_label.set('Filter off')
        else:
            self.filter_on_label.set('Filter on')
        self.filter_on_button = Tk.Button(self.button_frame, textvariable=self.filter_on_label, command=self.toggle_filter)
        self.filter_on_button.pack(side=Tk.LEFT)
       
        # filter_gain entry
        self.add_reg_entry('filter_gain')

        # filter_acc entry
        self.add_reg_entry('filter_acc')

        # channel entry
        self.add_reg_entry('channel')

    def toggle_filter(self):
        if self.model.fpga.read_int('filter_on') == 1:
            self.model.set_reg('filter_on', 0)
            self.filter_on_label.set('Filter Off')
            print('Filter is off')
        else:
            self.model.set_reg('filter_on', 1)
            self.filter_on_label.set('Filter On')
            print('Filter is on')

if __name__ == '__main__':
    animator = KestfiltAnimator()
    animator.start_animation()
