import time
import numpy as np
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
        self.consts0 = np.zeros(self.nchannels, dtype=np.complex128)
        self.consts1 = np.zeros(self.nchannels, dtype=np.complex128)
        
    def run_dss_test(self):
        """
        Perform a full DSS test, with constants and SRR computation. 
        """
        if not self.settings.ideal:
            self.run_consts_computation()
        run_srr_computation(self)

    def run_consts_computation(self):
        """
        Sweep a tone through the receiver bandwidth and computes the
        calibration constants for all FFT channels for LSB and USB. 
        Depending on the config file settings some constants can be
        interpolated to speed up the process.
        """
        a_div_b = np.zeros(self.nchannels, dtype=np.complex128)
        self.calplotter = DssCalibrationPlotter(self.fpga)
        self.calplotter.create_window(create_gui=False)
        
        # set generator power
        self.source.set_power_dbm(self.settings.sync_power)
        self.source.turn_output_on()
        for channel in range(1, self.nchannels, self.settings.cal_chnl_step):
            # set generator frequency
            self.source.set_freq_mhz(self.freqs[channel])
            time.sleep(2)

            # get power-crosspower data
            cal_a2, cal_b2 = self.fpga.get_bram_list_interleaved_data(self.settings.cal_pow_info)
            cal_ab_re, cal_ab_im = self.fpga.get_bram_list_interleaved_data(self.settings.cal_crosspow_info)
            
            # compute constant
            ab = cal_ab_re[channel] + 1j*cal_ab_im[channel]
            a_div_b[channel] = ab / cal_b2[channel]

            # plot data specta
            for spec_data, axis in zip([cal_a2, cal_b2], self.calplotter.axes[:2]):
                spec_data = spec_data / float(self.fpga.read_reg('cal_acc_len')) # divide by accumulation
                spec_data = self.linear_to_dBFS(spec_data)
                axis.plot(spec_data)
            
            freqs = [self.freqs[index] for index in range(1, channel+1, self.settings.cal_chnl_step)]

            # plot magnitude ratio
            self.calplotter.axes[2].plot(np.absolute(a_div_b)[1:channel+1:self.settings.cal_chnl_step], freqs)

            # plot angle difference
            self.calplotter.axes[3].plot(np.angle(a_div_b, deg=True)[1:channel+1:self.settings.cal_chnl_step], freqs) 

            self.calplotter.canvas.draw()

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
            spec_data_arr = self.fpga.get_bram_list_interleaved_data(self.settings.spec_info)
            # plot data
            for spec_data, axis in zip(spec_data_arr, self.srrplotter.axes):
                spec_data = spec_data / float(self.fpga.read_reg('syn_acc_len')) # divide by accumulation
                spec_data = self.linear_to_dBFS(spec_data)
                axis.plot(spec_data)
            self.srrplotter.canvas.draw()

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

        #self.fpga.write_bram_list_data(bram_info0, np.zeros((nbrams, depth)))
        #self.fpga.write_bram_list_data(bram_info1, np.zeros((nbrams, depth)))
        self.fpga.write_bram_list_data(bram_info0, (2**27 + 2**27 * 2**32) * np.ones((nbrams, depth)))
        self.fpga.write_bram_list_data(bram_info1, (2**27 + 2**27 * 2**32) * np.ones((nbrams, depth)))
    
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
 
