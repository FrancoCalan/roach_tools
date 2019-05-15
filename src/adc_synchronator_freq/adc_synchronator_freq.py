import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels, init_sources, turn_off_sources
from ..calanfigure import CalanFigure
from ..instruments.generator import Generator, create_generator
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis

class AdcSynchronatorFreq(Experiment):
    """
    This class is used to synchronize two ADC using
    frequency domain information.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.specsync_info)
        self.freqs = np.linspace(0, self.bw, self.nchannels, endpoint=False)
        
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
        self.figure = CalanFigure(n_plots=4, create_gui=False)
        self.figure.create_axis(0, SpectrumAxis,  self.freqs, 'ZDOK0 spec')
        self.figure.create_axis(1, SpectrumAxis,  self.freqs, 'ZDOK1 spec')
        self.figure.create_axis(2, MagRatioAxis,  self.test_freqs, ['z1/z0'], 'Magnitude Ratio')
        self.figure.create_axis(3, AngleDiffAxis, self.test_freqs, ['z1-z0'], 'Angle Difference')
        self.figure.set_window_title('ADC Sync')
        
    def synchronize_adcs(self):
        """
        Compute the delay difference between ADC (expected to be 
        an integer of the smaple time), and apply that delay to the
        ADC running ahead in order to sychronize both ADCs. This is 
        frequency based synchronization methods, that is an alternative
        to the stand-alone time-based adc_synchornator method, with the
        benefit that is less cumbersome when using backends that require
        down-conversion, and that is more precise.
        """
        init_sources(self.sources)

        # set LO freqs as first freq combination
        for lo_source, freq in zip(self.lo_sources, self.lo_combination):
            lo_source.set_freq_mhz(freq)
        center_freq = sum(self.lo_combination)

        print "Synchronizing ADCs..."
        while True:
            spec_ratios = []

            for i, chnl in enumerate(self.test_channels):
                # set generator frequency
                freq = self.freqs[chnl]
                self.rf_source.set_freq_mhz(center_freq + freq)
                plt.pause(self.settings.pause_time)

                # get power-crosspower data
                a2, b2 = self.fpga.get_bram_data_interleave(self.settings.specsync_info)
                ab_re, ab_im = self.fpga.get_bram_data_interleave(self.settings.crosspowsync_info)

                # compute constant
                ab = ab_re[chnl] + 1j*ab_im[chnl]
                spec_ratios.append(np.conj(ab) / a2[chnl]) # (ab*)* / aa* = a*b / aa* = b/a

                # plot spec data
                [a2_plot, b2_plot] = \
                    self.scale_dbfs_spec_data([a2, b2], self.settings.specsync_info)
                self.figure.axes[0].plot(a2_plot)
                self.figure.axes[1].plot(b2_plot)

                # plot magnitude ratio and angle difference
                self.figure.axes[2].plotxy(self.test_freqs[:i+1], [np.abs(spec_ratios)])
                self.figure.axes[3].plotxy(self.test_freqs[:i+1], [np.angle(spec_ratios, deg=True)])

            # plot last frequency
            plt.pause(self.settings.pause_time) 

            delay = self.compute_adc_delay_freq(self.test_freqs[:i+1], spec_ratios) 
            # check adc sync status, apply delay if needed
            if delay == 0:
                print "ADCs successfully synthronized!"
                break
            elif delay > 0: # if delay is positive adc1 is ahead, hence delay adc1
                self.fpga.set_reg('adc1_delay', delay)
            else: # (delay < 0) if delay is negative adc0 is ahead, hence delay adc0
                self.fpga.set_reg('adc0_delay', -1*delay)

        turn_off_sources(self.sources)

    def compute_adc_delay_freq(self, freqs, spec_ratios):
        """
        Compute the adc delay between two unsynchronized adcs using information
        in the frequency domain. It's done by computing the slope of the phase
        difference with respect the frequency, and then it translates this value
        into an integer delay in number of samples.
        :freqs: frequency array in which the sideband ratios where computed.
        :spec_ratios: spectrometer ratios array of the adcs. The spectrometer
            ratio is the complex division of an spectral channel from adc0 with adc1.
        :return: adc delay in number of samples.
        """
        phase_diffs = np.unwrap(np.angle(spec_ratios))
        linregress_results = scipy.stats.linregress(freqs, phase_diffs)
        angle_slope = linregress_results.slope
        delay = int(round(angle_slope * 2*self.settings.bw / (2*np.pi))) # delay = dphi/df * Fs / 2pi
        print "Computed delay: " + str(delay)
        return delay

def get_first_lo_combination(lo_sources):
    """
    Get the first lo combination from the lo_sources config file.
    :param lo_sources: list of dictionaries with the sources for the LOs.
    :return: list of the lo frequencies for the first combination.
    """
    return [lo_source['lo_freqs'][0] for lo_source in lo_sources]
