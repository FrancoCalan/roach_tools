import time
import numpy as np
import matplotlib.pyplot as plt
from experiment import Experiment
from plotter import Plotter
from spectrum_axis import SpectrumAxis
from mag_ratio_axis import MagRatioAxis
from angle_diff_axis import AngleDiffAxis
from generator import Generator

class DssCalibrator(Experiment):
    """
    This class is used to calibrate a Sideband Separating receiver.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.source = Generator(self.settings.source_ip, self.settings.source_port)
        self.nchannels = self.get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(0, self.settings.bw, self.nchannels, endpoint=False)
        self.usb_consts = np.zeros(self.nchannels, dtype=np.complex128)
        self.lsb_consts = np.zeros(self.nchannels, dtype=np.complex128)
        
    def run_dss_test(self):
        """
        Perform a full DSS test, with constants and SRR computation. 
        """
        if not self.settings.ideal:
            self.run_consts_computation()
        run_srr_computation(self)

    def compute_sb_ratios(self, center_freq=0, tone_in_usb=True):
        """
        Sweep a tone through the receiver bandwidth and computes the
        sideband ratio for a number of FFT channel. The total number
        depends in the config file parameter cal_channel_step. The 
        channels not measured are interpolated.
        :param center_freq: analog center frequency of the downconverted 
            signal. Used to properly set the RF input.
        :param tone_in_usb: True: tone is swept over the USB, and the
            and the ratio computed is LSB/USB.
            False: tone is swept over the LSB, and the ratio computed
            is USB/LSB.
        """
        channels = range(self.nchannels)[1::self.settings.cal_chnl_step]
        partial_freqs = [] # for plotting
        sb_ratios = []

        self.calplotter = DssCalibrationPlotter(self.fpga)
        self.calplotter.create_window(create_gui=False)
        
        # set generator power
        self.source.set_power_dbm(self.settings.sync_power)
        self.source.turn_output_on()

        for chnl in channels:
            freq = self.freqs[chnl]
            # set generator frequency
            if tone_in_usb:
                self.source.set_freq_mhz(center_freq + freq)
            else: # tone in lsb
                self.source.set_freq_mhz(center_freq - freq)    
            # plot while the generator is changing to frequency to give the system time to update
            plt.pause(1) 

            # get power-crosspower data
            cal_a2, cal_b2 = self.fpga.get_bram_list_interleaved_data(self.settings.cal_pow_info)
            cal_ab_re, cal_ab_im = self.fpga.get_bram_list_interleaved_data(self.settings.cal_crosspow_info)
            
            # compute constant
            ab = cal_ab_re[chnl] + 1j*cal_ab_im[chnl]
            if tone_in_usb:
                sb_ratios.append(np.conj(ab) / cal_a2[chnl]) # (ab*)* / aa* = a*b / aa* = b/a = LSB/USB
            else: # tone in lsb
                sb_ratios.append(ab / cal_b2[chnl]) # ab* / bb* = a/b = USB/LSB

            # plot data specta
            for spec_data, axis in zip([cal_a2, cal_b2], self.calplotter.axes[:2]):
                spec_data = spec_data / float(self.fpga.read_reg('cal_acc_len')) # divide by accumulation
                spec_data = self.linear_to_dBFS(spec_data)
                axis.plot(spec_data)
            
            partial_freqs.append(freq)
            # plot magnitude ratio
            self.calplotter.axes[2].plot(partial_freqs, np.abs(sb_ratios))
            # plot angle difference
            self.calplotter.axes[3].plot(partial_freqs, np.angle(sb_ratios, deg=True))

        # plot last frequency
        plt.pause(1) 

        # compute interpolations
        print "Computing interpolations..."
        sb_ratios = np.interp(range(self.nchannels), channels, sb_ratios)
        print "done"
            
        return sb_ratios

    def run_srr_computation(self):
        """
        Compute SRR from the calibrated receiver using ideal or computed
        calibration constants.
        """
        if self.settings.ideal:
            self.load_ideal_constants()

        self.srrplotter = DssSrrPlotter(self.fpga)
        self.srrplotter.create_window(create_gui=False)

        while True:
            plt.pause(1) # plot while the generator is changing to frequency to give the system time to update
            spec_data_arr = self.fpga.get_bram_list_interleaved_data(self.settings.spec_info)
            # plot data
            for spec_data, axis in zip(spec_data_arr, self.srrplotter.axes):
                spec_data = spec_data / float(self.fpga.read_reg('syn_acc_len')) # divide by accumulation
                spec_data = self.linear_to_dBFS(spec_data)
                axis.plot(spec_data)

    def load_ideal_constants(self):
        """
        Load ideal constants into de DSS receiver.
        """
        nbrams = len(self.settings.const_brams_info['bram_list2d'][0])
        depth = 2**self.settings.const_brams_info['addr_width']
        
        bram_info0 = self.settings.const_brams_info.copy()
        bram_info0['bram_list'] = self.settings.const_brams_info['bram_list2d'][0]
        bram_info1 = self.settings.const_brams_info.copy()
        bram_info1['bram_list'] = self.settings.const_brams_info['bram_list2d'][1]

        self.fpga.write_bram_list_data(bram_info0, np.zeros((nbrams, depth)))
        self.fpga.write_bram_list_data(bram_info1, np.zeros((nbrams, depth)))
        #self.fpga.write_bram_list_data(bram_info0, (2**27 + 2**27 * 2**32) * np.ones((nbrams, depth)))
        #self.fpga.write_bram_list_data(bram_info1, (2**27 + 2**27 * 2**32) * np.ones((nbrams, depth)))

class DssCalibrationPlotter(Plotter):
    """
    Inner class for calibration plots.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.nplots = 4
        mpl_axes = self.create_axes()
        self.nchannels = self.get_nchannels(self.settings.cal_pow_info)
        
        # add custom axes
        self.axes.append(SpectrumAxis(mpl_axes[0], self.nchannels,
                self.settings.bw, 'ZDOK0 spec'))
        self.axes.append(SpectrumAxis(mpl_axes[1], self.nchannels,
                self.settings.bw, 'ZDOK1 spec'))
        self.axes.append(MagRatioAxis(mpl_axes[2], self.nchannels,
                self.settings.bw, 'Magnitude ratio 0/1'))
        self.axes.append(AngleDiffAxis(mpl_axes[3], self.nchannels,
                self.settings.bw, 'Angle difference 0-1'))
       
class DssSrrPlotter(Plotter):
    """
    Inner class for post-calibration plots.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.nplots = 2
        mpl_axes = self.create_axes()
    
        self.nchannels = self.get_nchannels(self.settings.spec_info)
        for i, ax in enumerate(mpl_axes):
            self.axes.append(SpectrumAxis(ax, self.nchannels,
                self.settings.bw, self.settings.plot_titles[i]))
 
