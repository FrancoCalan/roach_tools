import itertools
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from ..experiment import Experiment, linear_to_dBFS, get_nchannels
from ..calanfigure import CalanFigure
from ..instruments.generator import Generator, create_generator
from ..axes.spectrum_axis import SpectrumAxis
from mag_ratio_axis import MagRatioAxis
from angle_diff_axis import AngleDiffAxis

class AdcSynchronatorFreq(Experiment):
    """
    This class is used to synchronize two ADC using
    frequency domain information.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.nchannels = get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(0, self.settings.bw, self.nchannels, endpoint=False)
        self.lo_combinations = get_lo_combinations(self.settings.lo_sources)
        
        # sources (RF and LOs)
        self.rf_source = create_generator(self.settings.rf_source)
        self.lo_sources = [create_generator(lo_source) for lo_source in self.settings.lo_sources]
        
        # test channels array
        sync_chnl_start = self.settings.sync_chnl_start
        sync_chnl_stop  = self.settings.sync_chnl_stop
        sync_chnl_step  = self.settings.sync_chnl_step
        self.sync_channels = range(sync_chnl_start, sync_chnl_stop, sync_chnl_step)
        self.sync_freqs = self.freqs[self.sync_channels]

        # figures and axes
        self.figure = CalanFigure(n_plots=4, create_gui=False)
        self.figure.create_axis(0, SpectrumAxis,  self.sync_freqs, 'ZDOK0 spec')
        self.figure.create_axis(1, SpectrumAxis,  self.sync_freqs, 'ZDOK1 spec')
        self.figure.create_axis(2, MagRatioAxis,  self.sync_freqs, 'Magnitude Ratio')
        self.figure.create_axis(3, AngleDiffAxis, self.sync_freqs, 'Angle Difference')
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
        self.init_sources()

        # set LO freqs as first freq combination
        lo_comb = self.get_lo_combinations()[0]
        for lo_source, freq in zip(self.lo_sources, lo_comb):
            lo_source.set_freq_mhz(freq)
        center_freq = sum(lo_comb)

        print "Synchronizing ADCs..."
        while True:
            spec_ratios = []

            for i, chnl in enumerate(self.sync_channels):
                # set generator frequency
                freq = self.freqs[chnl]
                self.rf_source.set_freq_mhz(center_freq + freq)
                plt.pause(self.settings.pause_time) 

                # get power-crosspower data
                a2, b2 = self.fpga.get_bram_data_interleave(self.settings.spec_info)
                ab_re, ab_im = self.fpga.get_bram_data_interleave(self.settings.crosspow_info)

                # compute constant
                ab = cal_ab_re[chnl] + 1j*cal_ab_im[chnl]
                spec_ratios.append(np.conj(ab) / cal_a2[chnl]) # (ab*)* / aa* = a*b / aa* = b/a

                # plot spec data
                [a2_plot, b2_plot] = \
                    self.scale_dbfs_spec_data([cal_a2, cal_b2], self.settings.spec_info)
                self.figure.axes[0].plot(a2_plot)
                self.figure.axes[1].plot(b2_plot)

                # plot magnitude ratio and angle difference
                partial_freqs = self.freqs[self.sync_channels[:i+1]]
                self.figure.axes[2].plot(partial_freqs, np.abs(spec_ratios))
                self.calfigure_usb.axes[3].plot(partial_freqs, np.angle(spec_ratios, deg=True))

            # plot last frequency
            plt.pause(self.settings.pause_time) 

            delay = self.compute_adc_delay_freq(partial_freqs, spec_ratios) 
            # check adc sync status, apply delay if needed
            if delay == 0:
                print "ADCs successfully synthronized!"
                return
            elif delay > 0: # if delay is positive adc1 is ahead, hence delay adc1
                self.fpga.set_reg('adc1_delay', delay)
            else: # (delay < 0) if delay is negative adc0 is ahead, hence delay adc0
                self.fpga.set_reg('adc0_delay', -1*delay)

    def init_sources(self):
        """
        Turn on LO and RF sources and set them to their default power value.
        """
        self.rf_source.set_power_dbm()
        self.rf_source.turn_output_on()
        for lo_source in self.lo_sources:
            lo_source.set_power_dbm()
            lo_source.turn_output_on()

    def compute_adc_delay_freq(self, freqs, sb_ratios):
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

def get_lo_combinations(lo_sources):
    """
    Creates a list of tuples with all the possible LO combinations from
    the lo_sources parameter of the config file. Used to perform a
    nested loop that set all LO combinations in generators.
    :param lo_sources: list of dictionaries with the sources for the LOs.
    :return: list of tuples of LO combinations.
    """
    lo_freqs_arr = [lo_source['lo_freqs'] for lo_source in lo_sources]
    return list(itertools.product(*lo_freqs_arr))
