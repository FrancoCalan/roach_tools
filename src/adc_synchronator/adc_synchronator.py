import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels, init_sources, turn_off_sources
from ..calanfigure import CalanFigure
from ..instruments.generator import Generator, create_generator
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis

class AdcSynchronator(Experiment):
    """
    This class is used to synchronize two or more ADC using
    frequency domain information.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(0, self.bw, self.nchannels, endpoint=False)
        self.sync_regs = self.settings.sync_regs
        self.sync_delays = [self.fpga.read_reg(sync_reg) for sync_reg in self.sync_regs]
        
        # test channels array
        chnl_start = self.settings.sync_chnl_start
        chnl_stop  = self.settings.sync_chnl_stop
        chnl_step  = self.settings.sync_chnl_step
        self.test_channels = range(chnl_start, chnl_stop, chnl_step)
        self.test_freqs = self.freqs[self.test_channels]

        # sources (RF and LOs)
        self.rf_source  = create_generator(self.settings.test_source)
        self.lo_sources = [create_generator(lo_source) for lo_source in self.settings.lo_sources]
        self.sources = self.lo_sources + [self.rf_source]
        self.lo_combination = get_first_lo_combination(self.settings.lo_sources)

        # figures and axes
        self.n_inputs = len(self.settings.spec_titles)
        self.figure = CalanFigure(n_plots=self.n_inputs+2, create_gui=False)
        for i, spec_title in enumerate(self.settings.spec_titles):
            self.figure.create_axis(i, SpectrumAxis,  self.freqs, spec_title)
        self.legends = self.settings.corr_legends
        self.figure.create_axis(self.n_inputs, MagRatioAxis, self.test_freqs, self.legends, 'Magnitude Ratio')
        self.figure.create_axis(self.n_inputs+1, AngleDiffAxis, self.test_freqs, self.legends, 'Angle Difference')

    def synchronize_adcs(self):
        """
        Compute the delay difference between ADCs (expected to be 
        an integer of the smaple time), and apply that delays to the
        ADCs running ahead (all except the slowest one) in order to sychronize
        all ADCs. This is frequency based synchronization methods, that is an 
        alternative to the stand-alone time-based adc_synchornator method, with 
        the benefit that is less cumbersome when using backends that require
        down-conversion, and that is more precise.
        """
        init_sources(self.sources)

        # set LO freqs as first freq combination
        for lo_source, freq in zip(self.lo_sources, self.lo_combination):
            lo_source.set_freq_mhz(freq)
        center_freq = sum(self.lo_combination)

        print "Synchronizing ADCs..."
        while True:
            ratios = [[] for i in range(len(self.legends))]

            for i, chnl in enumerate(self.test_channels):
                # set generator frequency
                freq = self.freqs[chnl]
                self.rf_source.set_freq_mhz(center_freq + freq)
                plt.pause(self.settings.pause_time)

                # get power-crosspower data
                pow_data = self.fpga.get_bram_data(self.settings.spec_info)
                crosspow_data = self.fpga.get_bram_data(self.settings.crosspow_info)

                # combine real and imaginary part of crosspow data
                crosspow_data = np.array(crosspow_data[0::2]) + 1j*np.array(crosspow_data[1::2])

                # compute the complex ratios (magnitude ratio and phase difference)
                # use first input as reference
                aa = pow_data[0][chnl]
                for j, ab in enumerate(crosspow_data):
                    ratios[j].append(np.conj(ab[chnl]) / aa) # (ab*)* / aa* = a*b / aa* = b/a

                # plot spectrum
                spec_data_dbfs = self.scale_dbfs_spec_data(pow_data, self.settings.spec_info)
                for j, spec in enumerate(spec_data_dbfs):
                    self.figure.axes[j].plot(spec)
            
                # plot the magnitude ratio and phase difference
                self.figure.axes[-2].plotxy(self.test_freqs[:i+1], np.abs(ratios))
                self.figure.axes[-1].plotxy(self.test_freqs[:i+1], np.angle(ratios, deg=True))

            # plot last frequency
            plt.pause(self.settings.pause_time) 

            # get delays between adcs
            delays = self.compute_adc_delays_freq(self.test_freqs[:i+1], ratios) 
            
            # if the sync regs are 1 more than the computed delays,
            # assume that the first reg is for the reference
            if len(self.sync_regs)-1 == len(delays):
                delays.insert(0, 0) # 0 delay for the reference

            # check adc sync status, apply delay if needed
            if all(delay == 0 for delay in delays):
                print "ADCs successfully synthronized!"
                break
            else:
                # transform actual delays to necessary delays needed to sync
                sync_delays = -1*np.array(delays)
                # offset delays to only get non-negative integers (negative delay do not exist)
                sync_delays = sync_delays - np.min(sync_delays)
                # update sync delay values
                self.sync_delays = self.sync_delays + sync_delays
                # apply delays
                for sync_delay, sync_reg in zip(self.sync_delays, self.sync_regs):
                    self.fpga.set_reg(sync_reg, sync_delay)

        turn_off_sources(self.sources)

    def compute_adc_delays_freq(self, freqs, ratios):
        """
        Compute the adc delay between two or more unsynchronized adcs using 
        information in the frequency domain. It's done by computing the slope in 
        the frequency domain of the phase difference between the input of an ADC
        and a reference signal, and then it translates this value into an 
        integer delay in number of samples.
        :freqs: frequency array in which the phase difference slope is computed.
        :ratios: the complex ratio of the adc inputs and the reference. The 
            reference is usually one of the ADC inputs.
        :return: list of the adc delays in number of samples.
        """
        delays = []
        for adc_ratios in ratios:
            phase_diffs = np.unwrap(np.angle(adc_ratios))
            linregress_results = scipy.stats.linregress(freqs, phase_diffs)
            angle_slope = linregress_results.slope
            delay = int(round(angle_slope * 2*self.settings.bw / (2*np.pi))) # delay = dphi/df * Fs / 2pi
            delays.append(delay)
        print "Computed delays: " + str(delays)
        return delays

def get_first_lo_combination(lo_sources):
    """
    Get the first lo combination from the lo_sources config file.
    :param lo_sources: list of dictionaries with the sources for the LOs.
    :return: list of the lo frequencies for the first combination.
    """
    return [lo_source['lo_freqs'][0] for lo_source in lo_sources]
