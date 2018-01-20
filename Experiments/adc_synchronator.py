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

import numpy as np
from experiment import Experiment
from Models.snapshot import Snapshot
from snapshot_animator import SnapshotAnimator
from Generator.generator import Generator
from Models.Dummies.dummy_generator import gen_time_arr

class AdcSynchronator(Experiment):
    """
    This class is used to synchronize two ADC
    """

    def __init__(self):
        Experiment.__init__(self)
        self.snapshot_animator = SnapshotAnimator()
        self.source = Generator(self.settings.source_ip, self.settings.source_port)

    def get_model(self, settings):
        """
        Get snapshot model.
        """
        return Snapshot(settings)

    def synchronize_adcs(self):
        """
        Iteratively tries to synchornize two adcs from ROACH2, using 
        snapshot information, and computing phase difference using
        single frequency DFT.
        """
        # start plot
        #self.snapshot_animator.start_animation()

        # turn source on and set freq and amp
        self.source.set_freq_mhz(self.settings.sync_freq) 
        self.source.set_power_dbm(self.settings.sync_power)
        self.source.turn_on()

        for _ in range(2):
            [snap_adc0, snap_adc1] = self.get_snapshots()
            snap0_phasor = self.estimate_phasor(self.settings.sync_freq, snap_adc0)
            snap1_phasor = self.estimate_phasor(self.settings.sync_freq, snap_adc1)
            phasor_div = self.compute_phasor_div(snap0_phasor, snap1_phasor)
            sync_delay = self.compute_delay_diff(phasor_div)
            print "Sync delay: " + str(sync_delay)
            self.delay_adcs(sync_delay)

        self.source.turn_off()

    def get_snapshots(self):
        """
        Activate snapshot trigger so a single snapshot per adc is saved
        in bram. This way both snapshots are synchronized. Returns the 
        snapshot data array.
        """
        self.model.set_reg(self.settings.snap_trig, 0)
        self.model.set_reg(self.settings.snap_trig, 1)
        return self.model.get_snapshots()

    def estimate_phasor(self, freq, data):
        """
        Estimates a phasor associated with frequency freq from data.
        It's done by computing the single channel DFT at frequency freq.
        """
        Ts = 1.0/(2*self.settings.bw)
        time_arr = gen_time_arr(Ts, self.settings.snap_samples)
        exp_sig = np.exp(-1j*2*np.pi*freq * time_arr)
        return  np.dot(data, exp_sig)

    def compute_phasor_div(self, phasor0, phasor1):
        """
        Computes the phasor division: phasor1 / phasor0.
        """
        phasor_div = phasor1 / phasor0
        print "Magnitude ratio: " + str(np.abs(phasor_div))
        print "Phase difference: " + str(np.angle(phasor_div, deg=True))
        return phasor_div

    def compute_delay_diff(self, phasor_div):
        """
        Given the phasor division, computes the corresponding delay 
        difference in the model. Positive delay means that adc1 is 
        ahead of adc0, and negative delay means that adc0 is ahead of
        adc1.
        """
        Fs = 2*self.settings.bw
        samples_per_period = Fs / self.settings.sync_freq # = Tsync / Ts
        phase_diff = np.angle(phasor_div)
        return int(samples_per_period * phase_diff / 2*np.pi)

    def delay_adcs(self, delay):
        """
        Delay one of the adcs in order to put synchronize them. Assumes
        that a postive delay means a delay in adc1, and a negative delay 
        is a delay in adc0.
        """
        # case adc1 is ahead, hence delay adc1
        if delay > 0:
            self.model.set_reg(self.settings.adc_delays[1], delay)
        # case adc0 is ahead, hence delay adc0
        else:
            self.model.set_reg(self.settings.adc_delays[0], delay)

if __name__ == '__main__':
    synchronator = AdcSynchronator()
    synchronator.model.initialize_roach()
    synchronator.synchronize_adcs()
