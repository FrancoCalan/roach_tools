import time, json, datetime
import numpy as np
import matplotlib.pyplot as plt
from ..calanfigure import CalanFigure
from ..experiment import Experiment, get_nchannels
from ..digital_sideband_separation.dss_calibrator import float2fixed
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis

class BmOptCalibrator(Experiment):
    """
    Class to calibrate balance mixer using broadband
    noise input and optimization method.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.synth_info)
        self.freqs = np.linspace(0, self.bw, self.nchannels, endpoint=False)

        # const dtype info
        self.consts_nbits = np.dtype(self.settings.const_brams_info['data_type']).alignment * 8
        self.consts_bin_pt = self.settings.const_bin_pt

        # figures
        self.calfigure  = CalanFigure(n_plots=4, create_gui=False)

        # axes on figures
        self.calfigure.create_axis(0, SpectrumAxis, self.freqs, 'ZDOK0 spec')
        self.calfigure.create_axis(1, SpectrumAxis, self.freqs, 'ZDOK1 spec')
        self.calfigure.create_axis(2, MagRatioAxis, self.freqs, ['ZDOK0/ZDOK1'], 'Magnitude Ratio')
        self.calfigure.create_axis(3, AngleDiffAxis, self.freqs, ['ZDOK0-ZDOK1'], 'Angle Difference')

    def run_bm_opt_test(self):
        """
        Run test for balance mixer with optimization method.
        """
        sleep_time = 1
        initial_time = time.time()
        # first get calibration constants
        print "\tCompute calibration data cold..."; step_time = time.time()
        time.sleep(sleep_time)
        [a_cold, b_cold, ab_cold] = self.compute_calibration()
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        raw_input("Now set the noise source to hot and press start...")
        print "\tCompute calibration data hot..."; step_time = time.time()
        time.sleep(sleep_time)
        [a_hot, b_hot, ab_hot] = self.compute_calibration()
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        print "Saving data..."
        datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        np.savez('bm_data ' + datetime_now, a_cold=a_cold, b_cold=b_cold, ab_cold=ab_cold,
            a_hot=a_hot, b_hot=b_hot, ab_hot=ab_hot)
        print "done"

    def compute_calibration(self):
        """
        Compute calibration constants with broadband noise signal.
        :return: calibration constants.
        """
        # get power-crosspower data
        cal_a2, cal_b2 = self.fpga.get_bram_data(self.settings.spec_info)
        cal_ab_re, cal_ab_im = self.fpga.get_bram_data(self.settings.crosspow_info)    

        # compute ratio
        ab = cal_ab_re + 1j*cal_ab_im
        ab_ratios = ab / cal_b2 # ab* / bb* = a/b

        # plot spec data
        [cal_a2_plot, cal_b2_plot] = \
            self.scale_dbfs_spec_data([cal_a2, cal_b2], self.settings.spec_info)
        self.calfigure.axes[0].plot(cal_a2_plot)
        self.calfigure.axes[1].plot(cal_b2_plot)

        # plot the magnitude ratio and phase difference
        self.calfigure.axes[2].plot([np.abs(ab_ratios)])
        self.calfigure.axes[3].plot([np.angle(ab_ratios, deg=True)])
        plt.pause(0.1)

        return cal_a2, cal_b2, ab
