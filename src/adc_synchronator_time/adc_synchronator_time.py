import sys, time
import numpy as np
import matplotlib.pyplot as plt
from ..experiment import Experiment
from ..calanfigure import CalanFigure
from ..axes.snapshot_axis import SnapshotAxis
from ..instruments.generator import create_generator
from ..dummies.dummy_generator import gen_time_arr

class AdcSynchronatorTime(Experiment):
    """
    This class is used to synchronize two ADC using
    time domain information.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.snapshots = self.settings.snapshots
        self.figure = CalanFigure(n_plots=2, create_gui=False)
        
        self.figure.create_axis(0, SnapshotAxis, self.settings.snap_samples, self.snapshots[0])
        self.figure.create_axis(1, SnapshotAxis, self.settings.snap_samples, self.snapshots[1])

        self.Ts = 1.0/(2*self.settings.bw)
        self.source = create_generator(self.settings.sync_source)

        self.sync_freq = self.settings.sync_source['def_freq']
        self.synced_counter = 0
        self.required_synced_count = 5 # number of simultaneous iterations with ADCs in sync
                                       # required to consider the ADC synchronized

    def synchronize_adcs(self):
        """
        Iteratively tries to synchornize two adcs from ROACH2, using 
        snapshot information, and computing phase difference using
        single frequency DFT.
        """
        # turn source on and set default freq and power
        self.source.set_freq_mhz() 
        self.source.set_power_dbm()
        self.source.turn_output_on()

        while True:
            [snap_adc0, snap_adc1] = self.fpga.get_snapshots_sync()
            self.figure.axes[0].plot(snap_adc0[:self.settings.snap_samples])
            self.figure.axes[1].plot(snap_adc1[:self.settings.snap_samples])
            plt.pause(1)
            
            snap0_phasor = self.estimate_phasor(self.sync_freq, snap_adc0)
            snap1_phasor = self.estimate_phasor(self.sync_freq, snap_adc1)
            phasor_div = self.compute_phasor_div(snap0_phasor, snap1_phasor)
            sync_delay = self.compute_delay_diff(phasor_div)
            print "Sync delay: " + str(sync_delay)
            if sync_delay == 0:
                self.synced_counter += 1
                if self.synced_counter >= self.required_synced_count:
                    break
            else:
                self.synced_counter = 0
                self.delay_adcs(sync_delay)
        
        print "ADCs successfully synchronized"
        self.source.turn_output_off()

    def estimate_phasor(self, freq, data):
        """
        Estimates a phasor associated with frequency freq from data.
        It's done by computing the single channel DFT at frequency freq.
        """
        time_arr = gen_time_arr(self.Ts, len(data))
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
        samples_per_period = Fs / self.sync_freq # = Tsync / Ts
        phase_diff = np.angle(phasor_div)
        return int(samples_per_period * phase_diff / (2*np.pi))

    def delay_adcs(self, delay):
        """
        Delay one of the adcs in order to synchronize them. Assumes
        that a postive delay means a delay in adc0, and a negative delay 
        means a delay in adc1.
        """
        # if delay is positive adc1 is ahead, hence delay adc1
        if delay > 0:
            self.fpga.set_reg('adc1_delay', delay)
        # if delay is negative adc0 is ahead, hence delay adc0
        else:
            self.fpga.set_reg('adc0_delay', -1*delay)
        time.sleep(1)
