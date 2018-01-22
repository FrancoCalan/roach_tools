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
from dummy_snapshot import DummySnapshot

class DummyAdcSync(DummySnapshot):
    """
    Emulates an adc_sync implemented in ROACH. Used to deliver test data.
    """
    def __init__(self, settings):
        DummySnapshot.__init__(self, settings)
        self.snapshot_data = np.zeros(self.settings.snap_samples)
        self.natural_desync = 50

    def write_int(self, reg_name, val):
        """
        If snap_trig is triggered (0->1), update snapshot data with new signal
        from generator.
        """
        if reg_name == 'snap_trig':
            if self.read_int('snap_trig') == 0 and val == 1:
                self.snapshot_data = self.get_generator_signal(self.settings.snap_samples)
        DummySnapshot.write_int(self, reg_name, val)
        
    def snapshot_get(self, snapshot, man_trig=True, man_valid=True):
        """
        Returns snapshot signal stored in 'ram', adding the delyas from both the natural
        desync of the adcs, and the ones induced by the model.
        """
        if snapshot in self.snapshots:
            if snapshot == self.snapshots[0]:
                snap_data = np.roll(self.snapshot_data, self.read_int('adc0_delay'))
            else: # snapshot[1]
                snap_data = np.roll(self.snapshot_data, self.read_int('adc1_delay') + self.natural_desync)
            return {'data' : snap_data}
        else:
            raise Exception("Snapshot not defined in config file.")
