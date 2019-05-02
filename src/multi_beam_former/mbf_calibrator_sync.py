import time
import numpy as np
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels
from ..calanfigure import CalanFigure
from mbf_spectrometer import write_phasor_reg_list
from ..adc5g_calibrator.spectrum_axis import SpectrumAxis
from mbf_calibrator import reim2comp, compute_ratios, reorder_multiline_data

class MBFCalibratorSync(Experiment):
    """
    This class calibrates the multi beam former for
    analog front-end imbalances. It assumes the front-end
    is feed by a equal power and phase in all its port.
    This class takes the first port as reference and sets
    phasor constants in in the rest of the port in order to
    match the reference in power and phase. In only calibrates
    for a single frequency channel in all ports.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(0, self.bw, self.nchannels, endpoint=False)
        self.freq_chnl = self.settings.freq_chnl

        # figure and axes
        self.nports = len(self.settings.spec_titles)
        self.figure = CalanFigure(n_plots=self.nports, create_gui=False)
        self.figure.fig.set_size_inches(18.5, 10.5)
        for i, spec_title in enumerate(self.settings.spec_titles):
            self.figure.create_axis(i, SpectrumAxis, self.freqs, spec_title)

        # initialy set all phasors to 1 to measure the imbalances
        write_phasor_reg_list(self.fpga, self.nports*[1], range(self.nports), self.settings.cal_phase_info)

    def calibrate_mbf(self):
        """
        Perform power/phase calibration for the MBF.
        """
        # get data from fpga
        print "Getting calibration data..."
        pow_data_uncal = self.fpga.get_bram_data_sync(self.settings.spec_info)
        pow_data_uncal_dbfs = self.scale_dbfs_spec_data(pow_data_uncal, self.settings.spec_info)
        self.figure.plot_axes(reorder_multiline_data([pow_data_uncal_dbfs]))
        plt.pause(1)
        xab_data = self.fpga.get_bram_data(self.settings.cal_crosspow_info) 
        print 'done'
        
        # produce complex data and compute calibration constants
        print "Computing calibrations constants..."
        xab_comp_data = reim2comp(xab_data)
        cal_ratios = compute_ratios(pow_data_uncal, xab_comp_data, self.freq_chnl)
        for i, cal_ratio in enumerate(cal_ratios):
            print "Constant port " + str(i).zfill(2) + \
                ": mag: " + "%0.4f" % np.abs(cal_ratio) + \
                ", ang: " + "%0.4f" % np.angle(cal_ratio, deg=True) + "[deg]"
        print ""

        # load correction constants
        write_phasor_reg_list(self.fpga, cal_ratios, range(self.nports), self.settings.cal_phase_info)

        # test calibration
        time.sleep(0.1)
        print "Verifying calibration..."
        pow_data_cal = self.fpga.get_bram_data_sync(self.settings.spec_info)
        pow_data_cal_dbfs = self.scale_dbfs_spec_data(pow_data_cal, self.settings.spec_info)
        self.figure.plot_axes(reorder_multiline_data([pow_data_uncal_dbfs, pow_data_cal_dbfs]))
        plt.pause(1)
        xab_data = self.fpga.get_bram_data(self.settings.cal_crosspow_info) 
        xab_comp_data = reim2comp(xab_data)
        cal_ratios_new = compute_ratios(pow_data_cal, xab_comp_data, self.freq_chnl)
        for i, cal_ratio_new in enumerate(cal_ratios_new):
            print "Imbalance port " + str(i).zfill(2) + \
            ": mag: " + "%0.4f" % np.abs(cal_ratio_new) + \
            ", ang: " + "%0.4f" % np.angle(cal_ratio_new, deg=True) + "[deg]"
        print ""

        print "Original squared error:\n" + str(np.square(np.abs(cal_ratios - np.ones(self.nports))))
        print "Calibrated squared error:\n" + str(np.square(np.abs(cal_ratios_new - np.ones(self.nports))))
        print("Close plots to finish.")
        plt.show()
