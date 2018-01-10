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
from itertools import chain
from model import Model

class Snapshot(Model):
    """
    Helper class to read and write data from snapshot models.
    """
    def __init__(self, settings, dummy_snapshot):
        Model.__init__(self, settings, dummy_snapshot)

    def get_snapshot(self):
        """
        Get snapshot data from all snapshot blocks specified in the config 
        file.
        """
        snap_data_arr = []
        for snapshot in chain.from_iterable(self.settings.snapshots): # flatten list
            snap_data = np.fromstring(self.fpga.snapshot_get(snapshot, man_trig=True, 
                man_valid=True)['data'], dtype='>i1')[0:self.settings.snap_samples]
            snap_data_arr.append(snap_data)

        return snap_data_arr
