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

from animator import Animator
from single_line_axis import SingleLineAxis

class SnapshotAnimator(Animator):
    """
    Class responsable for drawing snapshot plots.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.nplots = len(self.settings.snapshots)
        mpl_axes = self.create_axes()
        
        self.set_axes_parameters(mpl_axes)

    def set_axes_parameters(self, mpl_axes):
        xdata = range(self.settings.snap_samples)
        for i, ax in enumerate(mpl_axes):
            ax.set_title(self.settings.snapshots[i])
            ax.set_xlim(0, self.settings.snap_samples)
            ax.set_ylim((-140, 140)) # Hardcoded 8-bit ADC
            ax.set_xlabel('Sample')
            ax.set_ylabel('Amplitude [a.u.]')
            self.axes.append(SingleLineAxis(ax, xdata))
        
    def get_data(self):
        """
        Gets the snapshot data form fpga.
        """
        snapshots = self.fpga.get_snapshots()
        sliced_snapshots = [snapshot[:self.settings.snap_samples] for snapshot in snapshots]
        return sliced_snapshots
