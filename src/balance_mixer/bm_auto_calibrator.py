import time, json, datetime, vxi11
import numpy as np
import matplotlib.pyplot as plt
from ..calanfigure import CalanFigure
from ..experiment import Experiment, get_nchannels
from ..digital_sideband_separation.dss_calibrator import float2fixed
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis

class BmAutoCalibrator(Experiment):
    """
    Class to calibrate balance mixer using broadband
    noise input.
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
        self.calfigure = CalanFigure(n_plots=4, create_gui=False)
        self.synfigure = CalanFigure(n_plots=1, create_gui=False)

        # axes on figures
        self.calfigure.create_axis(0, SpectrumAxis, self.freqs, 'ZDOK0 spec')
        self.calfigure.create_axis(1, SpectrumAxis, self.freqs, 'ZDOK1 spec')
        self.calfigure.create_axis(2, MagRatioAxis, self.freqs, ['ZDOK0/ZDOK1'], 'Magnitude Ratio')
        self.calfigure.create_axis(3, AngleDiffAxis, self.freqs, ['ZDOK0-ZDOK1'], 'Angle Difference')
        #
        self.synfigure.create_axis(0, SpectrumAxis, self.freqs, 'Synth spec')

        # power source control
        #self.noise_source = vxi11.Instrument('TCPIP::192.168.1.38::INSTR')

    def run_bm_auto_test(self):
        """
        Run automated test for balance mixer. 
        """
        initial_time = time.time()
        # first get calibration constants
        print "\tCompute calibration constants..."; step_time = time.time()
        time.sleep(5)
        ab_ratios, cal_a2, cal_b2, cal_ab = self.compute_calibration()
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        ###############################################################
        if self.settings.do_digital:
            print "### Computing parameters for cold source ###"
            [zero_cold_a, zero_cold_b] = self.get_single_ended_data()

            consts = 1*np.ones(self.nchannels, dtype=np.complex)
            rf_cold_ideal = self.get_synth_data("Loading ideal constants RF (1) and getting data...", consts)

            consts = -1*np.ones(self.nchannels, dtype=np.complex)
            lo_cold_ideal = self.get_synth_data("Loading ideal constants LO (-1) and getting data...", consts)

            consts = -1*ab_ratios
            rf_cold_cal = self.get_synth_data("Loading calibrated constants RF and getting data...", consts)

            consts = 1*ab_ratios
            lo_cold_cal = self.get_synth_data("Loading calibrated constants LO and getting data...", consts)

        ###############################################################
            raw_input("Now set the noise source to hot and press start...")
            #print "Setting the source to hot..."
            #self.noise_source.write('OUTPUT CH1,ON')
            #time.sleep(1)
            [zero_hot_a, zero_hot_b] = self.get_single_ended_data()

            consts = 1*np.ones(self.nchannels, dtype=np.complex)
            rf_hot_ideal = self.get_synth_data("Loading ideal constants RF (1) and getting data...", consts)

            consts = -1*np.ones(self.nchannels, dtype=np.complex)
            lo_hot_ideal = self.get_synth_data("Loading ideal constants LO (-1) and getting data...", consts)

            consts = -1*ab_ratios
            rf_hot_cal = self.get_synth_data("Loading calibrated constants RF and getting data...", consts)

            consts = 1*ab_ratios
            lo_hot_cal = self.get_synth_data("Loading calibrated constants LO and getting data...", consts)

        ##############################################################
            raw_input("Now turn off the LO noise and press start...")
            [zero_hot_a_nolo, zero_hot_b_nolo] = self.get_single_ended_data()

            consts = 1*np.ones(self.nchannels, dtype=np.complex)
            rf_hot_ideal_nolo = self.get_synth_data("Loading ideal constants RF (1) and getting data...", consts)

            consts = -1*np.ones(self.nchannels, dtype=np.complex)
            lo_hot_ideal_nolo = self.get_synth_data("Loading ideal constants LO (-1) and getting data...", consts)

            consts = -1*ab_ratios
            rf_hot_cal_nolo = self.get_synth_data("Loading calibrated constants RF and getting data...", consts)

            consts = 1*ab_ratios
            lo_hot_cal_nolo = self.get_synth_data("Loading calibrated constants LO and getting data...", consts)

        ##############################################################
            raw_input("Now set the noise source to cold and press start...")
            #print "Setting the source to cold..."
            #self.noise_source.write('OUTPUT CH1,OFF')
            #time.sleep(1)
            [zero_cold_a_nolo, zero_cold_b_nolo] = self.get_single_ended_data()

            consts = 1*np.ones(self.nchannels, dtype=np.complex)
            rf_cold_ideal_nolo = self.get_synth_data("Loading ideal constants RF (1) and getting data...", consts)

            consts = -1*np.ones(self.nchannels, dtype=np.complex)
            lo_cold_ideal_nolo = self.get_synth_data("Loading ideal constants LO (-1) and getting data...", consts)

            consts = -1*ab_ratios
            rf_cold_cal_nolo = self.get_synth_data("Loading calibrated constants RF and getting data...", consts)

            consts = 1*ab_ratios
            lo_cold_cal_nolo = self.get_synth_data("Loading calibrated constants LO and getting data...", consts)

        ##############################################################
        if self.settings.do_analog:
            raw_input("Now put the 0 degree combiner and press start...")
            raw_input("And remember to turn on the noise source...")
            rf_cold_analog = self.get_analog_data()
            raw_input("Now set the noise source to hot and press start...")
            rf_hot_analog = self.get_analog_data()
            raw_input("Now put the 180 degree combiner and press start...")
            lo_hot_analog = self.get_analog_data()
            raw_input("Now set the noise source to cold and press start...")
            lo_cold_analog = self.get_analog_data()

        ##############################################################

        print "Saving data..."
        datetime_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        np.savez('bm_data ' + datetime_now,
            freqs=self.freqs,
            cal_acc_len=self.fpga.read_reg(self.settings.spec_info['acc_len_reg']),
            syn_acc_len=self.fpga.read_reg(self.settings.synth_info['acc_len_reg']),
            # cal data
            cal_a2=cal_a2, cal_b2=cal_b2, cal_ab=cal_ab, ab_ratios=ab_ratios,
            # lo noise data
            zero_cold_a=zero_cold_a,     zero_hot_a=zero_hot_a,
            zero_cold_b=zero_cold_b,     zero_hot_b=zero_hot_b,
            rf_cold_ideal=rf_cold_ideal, rf_cold_cal=rf_cold_cal,
            lo_cold_ideal=lo_cold_ideal, lo_cold_cal=lo_cold_cal,
            rf_hot_ideal=rf_hot_ideal,   rf_hot_cal=rf_hot_cal,
            lo_hot_ideal=lo_hot_ideal,   lo_hot_cal=lo_hot_cal,
            # no lo noise data
            zero_cold_a_nolo  =zero_cold_a_nolo, 
            zero_cold_b_nolo  =zero_cold_b_nolo, 
            zero_hot_a_nolo   =zero_hot_a_nolo, 
            zero_hot_b_nolo   =zero_hot_b_nolo, 
            rf_cold_ideal_nolo=rf_cold_ideal_nolo, 
            rf_cold_cal_nolo  =rf_cold_cal_nolo,
            rf_hot_ideal_nolo =rf_hot_ideal_nolo, 
            rf_hot_cal_nolo   =rf_hot_cal_nolo,
            lo_cold_ideal_nolo=lo_cold_ideal_nolo, 
            lo_cold_cal_nolo  =lo_cold_cal_nolo,
            lo_hot_ideal_nolo =lo_hot_ideal_nolo, 
            lo_hot_cal_nolo   =lo_hot_cal_nolo,
            # analog data
            rf_cold_analog=rf_cold_analog, rf_hot_analog=rf_hot_analog,
            lo_cold_analog=lo_cold_analog, lo_hot_analog=lo_hot_analog)

        print "Total time: " + str(time.time() - initial_time) + "[s]"

    def compute_calibration(self):
        """
        Compute calibration constants with broadband noise signal.
        :return: calibration constants.
        """
        # get power-crosspower data
        cal_a2, cal_b2 = self.fpga.get_bram_data(self.settings.spec_info)
        cal_ab_re, cal_ab_im = self.fpga.get_bram_data(self.settings.crosspow_info)    

        # compute ratio
        cal_ab = cal_ab_re + 1j*cal_ab_im
        ab_ratios = cal_ab / cal_b2 # ab* / bb* = a/b

        # plot spec data
        [cal_a2_plot, cal_b2_plot] = \
            self.scale_dbfs_spec_data([cal_a2, cal_b2], self.settings.spec_info)
        self.calfigure.axes[0].plot(cal_a2_plot)
        self.calfigure.axes[1].plot(cal_b2_plot)

        # plot the magnitude ratio and phase difference
        self.calfigure.axes[2].plot([np.abs(ab_ratios)])
        self.calfigure.axes[3].plot([np.angle(ab_ratios, deg=True)])
        plt.pause(0.1)

        return ab_ratios, cal_a2, cal_b2, cal_ab

    def get_single_ended_data(self):
        sleep_time = 5
        print "Getting single ended data..."; step_time = time.time()
        time.sleep(sleep_time)
        [a, b] = self.fpga.get_bram_data(self.settings.spec_info)
        print "\tdone (" + str(time.time() - step_time) + "[s])"
        return [a, b]

    def get_synth_data(self, msg, consts):
        sleep_time = 5
        print msg; step_time = time.time()
        self.load_constants(consts)
        time.sleep(sleep_time)
        pwr_data = self.fpga.get_bram_data(self.settings.synth_info)
        self.plot_synth(pwr_data)
        print "\tdone (" + str(time.time() - step_time) + "[s])"
        return pwr_data

    def get_analog_data(self):
        sleep_time = 5
        print "Getting analog data..."; step_time = time.time()
        time.sleep(sleep_time)
        pwr_data = self.fpga.get_bram_data(self.settings.spec_info)[0]
        self.plot_synth(pwr_data)
        print "\tdone (" + str(time.time() - step_time) + "[s])"
        return pwr_data

    def load_constants(self, consts):
        consts_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts))
        consts_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts))
        self.fpga.write_bram_data(self.settings.const_brams_info, [consts_real, consts_imag])

    def plot_synth(self, data):
        data_plot = self.scale_dbfs_spec_data(data, self.settings.synth_info)
        self.synfigure.axes[0].plot(data_plot)
        plt.pause(0.1)
