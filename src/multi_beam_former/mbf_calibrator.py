import time
import numpy as np
import matplotlib.pyplot as plt
from itertools import chain
from ..experiment import Experiment, get_nchannels
from ..calanfigure import CalanFigure
from mbf_spectrometer import write_phasor_reg_list
from cal_phasor_axis import CalPhasorAxis

class MBFCalibrator(Experiment):
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
        self.figure = CalanFigure(n_plots=1, create_gui=False)
        self.figure.create_axis(0, CalPhasorAxis, ['uncalibrated', 'calibrated'])

        # initialy set all phasors to 1 to measure the imbalances
        self.array_info = self.settings.array_info
        self.nports = len(list(chain.from_iterable(self.array_info['el_pos']))) # flatten list
        write_phasor_reg_list(self.fpga, self.nports*[1], range(self.nports), self.settings.cal_phase_info)

    def calibrate_mbf(self):
        """
        Perform power/phase calibration for the MBF.
        """
        # get data from fpga
        print "Getting calibration data..."
        pow_data_uncal = self.fpga.get_bram_data(self.settings.spec_info)
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

        # plot calibration data
        self.figure.plot_axes([cal_ratios, []])
        plt.pause(1)

        # load correction constants
        write_phasor_reg_list(self.fpga, cal_ratios, range(self.nports), self.settings.cal_phase_info)

        # test calibration
        time.sleep(0.1)
        print "Verifying calibration..."
        pow_data_cal = self.fpga.get_bram_data(self.settings.spec_info)
        plt.pause(1)
        xab_data = self.fpga.get_bram_data(self.settings.cal_crosspow_info) 
        xab_comp_data = reim2comp(xab_data)
        cal_ratios_new = compute_ratios(pow_data_cal, xab_comp_data, self.freq_chnl)
        for i, cal_ratio_new in enumerate(cal_ratios_new):
            print "Imbalance port " + str(i).zfill(2) + \
            ": mag: " + "%0.4f" % np.abs(cal_ratio_new) + \
            ", ang: " + "%0.4f" % np.angle(cal_ratio_new, deg=True) + "[deg]"
        print ""
        
        # plot calibration data
        self.figure.plot_axes([cal_ratios, cal_ratios_new])
        plt.pause(1)

        print("Close plots to finish.")
        plt.show()
            
def reim2comp(data):
    """
    Given an array with real data, where two consecutive elements
    constitute a complex number (real and imaginary part in that order), 
    combine the data to generate an array of complex numbers. The initial
    array must have a even number of elements. If the input is a list of
    array with real data, the output is the corresponding list of arrays
    with the complex data.
    :param data: array or list of arrays of real data.
    :return: array or list of arrays of complex data.
    """
    if isinstance(data, np.ndarray):
        return data[::2] + 1j*data[1::2]

    elif isinstance(data, list):
        return [reim2comp(data_el) for data_el in data]

def compute_ratios(pow_data, xab_data, chnl):
    """
    Given a list of spectral data and cross-spectral data,
    compute the complex ratio (=magnitude ratio and phase difference)
    of the data for a single channel chnl. It is assumed that the
    cross-spectrum was computed as: reference x conj(signal).
    :param pow_data: list of power spectral data.
    :param xab_data: lisr of crosspower spectral data.
    :param chnl: frequency channel of the data in which compute the
        complex ratio.
    :return: array of the complex ratios of the data. The size of
        this list is equal to the number of spectrum arrays in the
        pow_data and xab_data lists.
    """
    cal_ratios = []
    for xpow, xab in zip(pow_data, xab_data):
        cal_ratios.append(xab[chnl] / xpow[chnl])

    return np.array(cal_ratios)

# NOTE: maybe I'm use this in another situation?
#def reorder_multiline_data(data_legend_arr):
#    """
#    Given data for MultiLineAxis distributed as array with
#    each element for each legend, distributes the data in an array
#    so that each element has the data for each plot. For example
#    (p: plot, l: legend):
#    input:  [[p1l1, p2l1, p3l1], [p1l2, p2l2, p3l2]]
#    output: [[p1l1, p1l2], [p2l1, p2l2], [p3l1, p3l2]]
#    """
#    data_plot_arr = [[] for i in range(len(data_legend_arr[0]))]
#    for data_legend in data_legend_arr:
#        for nplot, data_line in enumerate(data_legend):
#            data_plot_arr[nplot].append(data_line)
#
#    return data_plot_arr
