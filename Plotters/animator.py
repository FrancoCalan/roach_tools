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

import os, sys
from plotter import Plotter
import matplotlib.animation as animation
import Tkinter as Tk

class Animator(Plotter):
    """
    Generic animator class.
    """
    def __init__(self):
        Plotter.__init__(self)

    def start_animation(self):
        """
        Add the basic parameters to the plot and starts the animation.
        """
        self.add_plot_parameters()
        anim = animation.FuncAnimation(self.fig, animate, fargs=(self,), blit=True)
        Tk.mainloop()

def animate(_, self):
    """
    It's call on every frame of the animation. Updates the data.
    """
    self.draw_plot_lines()

    return self.line_arr
