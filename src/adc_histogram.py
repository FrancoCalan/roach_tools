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

import numpy as np
from animator import Animator
from snapshot_animator import SnapshotAnimator
from single_line_axis import SingleLineAxis
from bar_axis import BarAxis

class AdcHistogram(SnapshotAnimator):
    """
    Class responsible of making histogram from ADC snapshot data.
    Useful to find 'missing codes' and debug the ADC.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.nplots = 2 * len(self.settings.snapshots)
        mpl_axes = self.create_axes()
        
        self.xdata_hist = range(-2**7, 2**7) # Hardcoded 8-bit ADC

        SnapshotAnimator.set_axes_parameters(self, mpl_axes[:self.nplots/2]) # set axes for snapshots

        # set axes for histograms
        for i, ax in enumerate(mpl_axes[self.nplots/2:]):
            ax.set_title(self.settings.snapshots[i] + "hist")
            ax.set_xlim((-2**7, 2**7-1)) # Hardcoded 8-bit ADC
            ax.set_ylim((0, 0.035))
            ax.set_xlabel('Code')
            ax.set_ylabel('Normalized Fequency')
            self.axes.append(BarAxis(ax, self.xdata_hist))

        self.nhists = self.nplots / 2
        self.abs_hists = self.nhists * [np.zeros(2**8)] # Hardcoded 8-bit ADC

    def get_data(self):
        """
        Get snapshot data and generate histogram data to plot.
        """
        snapshots = SnapshotAnimator.get_data(self)
        norm_hists = []
        for i, snapshot in enumerate(snapshots):
            new_hist, _ = np.histogram(snapshot, bins=range(-2**7, 2**7+1)) # Hardcoded 8-bit ADC
            self.abs_hists[i] += new_hist
            norm_hists.append(self.abs_hists[i] / np.sum(self.abs_hists[i]))

        return snapshots + norm_hists
