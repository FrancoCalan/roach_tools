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

import os, sys, importlib
from matplotlib.figure import Figure
import matplotlib.animation as animation

class Animator():
    """
    Generic animator class.
    """
    def __init__(self):
        self.plot_map = {1:[1,1], 2:[1,2], 3:[2,2], 4:[2,2]}
        config_file = os.path.splitext(sys.argv[1])[0]
        self.settings = importlib.import_module(config_file)
        self.line_arr = []
        
    def start_animation(self):
        """
        Add the basic parameters to the plot and starts the animation.
        """
        for i, ax in enumerate(self.ax_arr):
            ax.set_xlim(self.xlim)
            ax.set_ylim(self.ylim)
            ax.set_xlabel(self.xlabel)
            ax.set_ylabel(self.ylabel)
            ax.set_title(self.titles[i])
            ax.grid(True)
            self.line_arr(ax.plot([], [], lw=2)[0])

            self.fig.set_tight_layout(True)
            anim = animation.FuncAnimation(self.fig, animate, fargs=(self,), blit=True)

    def animate(_, self):
        """
        It's call on every frame of the animation. Updates the data.
        """
        data_arr = self.get_data()

        for i, ydata in enumerate(data_arr):
            self.line_arr[i].set_data(self.xdata, ydata)
