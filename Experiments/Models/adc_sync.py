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

from model import Model
from Dummies.dummy_adc_sync import DummyAdcSync

class AdcSync(Model):
    """
    Helper class to read and write data from adc_sync models.
    """
    def __init__(self, settings):
        Snapshot.__init__(self, settings)

    def get_dummy(self):
        """
        Gets dummy adc_sync fpga.
        """
        return DummyAdcSync(self.settings)

    def get_snapshots(self):
        """
        Get snapshot data from bram. Used for ADC synchronator.
        """
        return self.get_bram_data(self.settings.bram_snapshots)