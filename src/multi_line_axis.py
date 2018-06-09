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

from calanaxis import CalanAxis

class MultiLineAxis(CalanAxis):
    """
    Class representing an axis from a plot with multiple lines plot.
    """
    def __init__(self, ax, xdata, legends):
        CalanAxis.__init__(self, ax, xdata)
        self.lines = []
        self.legends = legends
        for legend in self.legends:
            self.lines.append(self.ax.plot([], [], lw=2, label=legend)[0])

    def plot(self, ydata_arr):
        """
        Plot y data in axis.
        """
        for line, ydata in zip(self.lines, ydata_arr):
            line.set_data(self.xdata, ydata)
