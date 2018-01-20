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

import struct
import numpy as np
from itertools import chain
from dummy_roach import DummyRoach

class DummySnapshot(DummyRoach):
    """
    Emulates a snapshot implemented in ROACH. Used to deliver test data.
    """
    def __init__(self, settings):
        DummyRoach.__init__(self, settings)
        
        # add registers from config file
        for reg in settings.set_regs:
            self.regs.append({'name':reg['name'], 'val':0})
        for reg in settings.reset_regs:
            self.regs.append({'name':reg, 'val':0})

        # get snapshots
        self.snapshots = list(chain.from_iterable(self.settings.snapshots)) # flatten list
        
    def snapshot_get(self, snapshot, man_trig=True, man_valid=True):
        """
        Returns snapshot signal given by generator.
        """
        if snapshot in self.snapshots:
            snap_data = self.get_generator_signal(self.settings.snap_samples)
            return {'data' : snap_data}
        else:
            raise Exception("Snapshot not defined in config file.")
