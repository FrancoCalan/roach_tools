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
from itertools import chain
sys.path.append(os.getcwd())
from Models.snapshot import Snapshot
from Dummies.dummy_snapshot import DummySnapshot
from animator import Animator

class SnapshotAnimator(Animator):
    """
    Class responsable for drawing snapshot plots.
    """
    def __init__(self):
        Animator.__init__(self)
        self.titles = list(chain.from_iterable(self.settings.snapshots)) # flatten list
        self.nplots = len(self.titles)
        self.xlim = (0, self.settings.snap_samples)
        self.ylims = self.nplots * [(-140, 140)]
        self.xlabel = 'Sample'
        self.ylabels = self.nplots * ['Amplitude [a.u.]']
        self.xdata = range(self.settings.snap_samples)

    def get_model(self, settings):
        """
        Get spectrometer model for animator.
        """
        return Snapshot(settings, DummySnapshot(settings))

    def get_data(self):
        """
        Gets the snapshot data form the spectrometer model.
        """
        return self.model.get_snapshot()

if __name__ == '__main__':
    animator = SnapshotAnimator()
    animator.start_animation()
