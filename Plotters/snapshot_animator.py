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

import sys
sys.path.append('../Models')
from spectrometer import Spectrometer
from animator import Animator

class SnapshotAnimator(Animator):
    """
    Class responsable for drawing snapshot plots.
    """
    def __init__(self):
        Animator.__init__()
        self.spectrometer = Spectrometer(self.settings)
        self.xlim = (0, self.settings.snap_xlim)
        self.ylim = (-130, 130)
        self.xlabel = 'Sample'
        self.ylabel = 'Amplitude [a.u.]'
        self.titles = self.settings.snapshots
        self.xdata = range(self.settings.n_samples)

        n_plots = len(self.settings.snapshots)
        self.fig, self.ax_arr = plt.subplots(*self.plot_map[n_plots])

    def get_data(self):
        """
        Gets the snapshot data form the spectrometer model.
        """
        return self.spectrometer.get_snapshot()

if '__name__' == '__main__':
    animator = SnapshotAnimator()
    animator.start_animation()
