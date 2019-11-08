import os, time, datetime, itertools, json, tarfile, shutil
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from ..experiment import Experiment, get_nchannels, init_sources, turn_off_sources
from ..calanfigure import CalanFigure
from ..instruments.generator import Generator, create_generator
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis
from cancellation_axis import CancellationAxis
from ..digital_sideband_separation.dss_calibrator import get_lo_combinations, float2fixed

class BmNoiseLnrComputation(Experiment):
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

        # LO sources
        self.lo_sources  = [create_generator(lo_source) for lo_source in self.settings.lo_sources]
        self.lo_combinations = get_lo_combinations(self.settings.lo_sources)

        # figures
        self.calfigure = CalanFigure(n_plots=4, create_gui=False)
        self.synfigure = CalanFigure(n_plots=1, create_gui=False)

        # axes on figures
        self.calfigure.create_axis(0, SpectrumAxis, self.freqs, 'ZDOK0 spec')
        self.calfigure.create_axis(1, SpectrumAxis, self.freqs, 'ZDOK1 spec')
        self.calfigure.create_axis(2, MagRatioAxis, self.freqs, ['ZDOK0/ZDOK1'], 'Magnitude Ratio')
        self.calfigure.create_axis(3, AngleDiffAxis, self.freqs, ['ZDOK0-ZDOK1'], 'Angle Difference')
        #
        self.synfigure.create_axis(0, CancellationAxis, self.freqs)

        # data save attributes
        self.save_data = not self.settings.saved_params['use_saved'] or self.settings.compute_cancellation
        self.dataname = self.settings.boffile[:self.settings.boffile.index('.')]
        self.dataname = 'bm_noise_test ' + self.dataname
        self.datadir = self.dataname + ' ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.testinfo = {'bw'               : self.bw,
                         'nchannels'        : self.nchannels,
                         'saved_params'     : self.settings.saved_params,
                         'cal_acc_len'      : self.fpga.read_reg(self.settings.spec_info['acc_len_reg']),
                         'syn_acc_len'      : self.fpga.read_reg(self.settings.synth_info['acc_len_reg']),
                         'lo_combinations'  : self.lo_combinations}

        os.mkdir(self.datadir)
        with open(self.datadir + '/testinfo.json', 'w') as jsonfile:
            json.dump(self.testinfo, jsonfile, indent=4)

        np.save(self.datadir+'/freqs', self.freqs)

    def run_bm_noise_test(self):
        """
        Perform a balance mixer test calibration using
        noise as input.
        """
        #init_sources(self.lo_sources)
        self.lo_sources[0].set_power_dbm()
        self.lo_sources[0].turn_output_on()

        initial_time = time.time()
        # get compute ab params
        print "\tComputing ab parameters with noise input..."; step_time = time.time()
        a2, b2, ab = self.compute_ab_params()
        print "\tdone (" + str(time.time() - step_time) + "[s])" 

        np.save(self.datadir+'/input_a2', a2)
        np.save(self.datadir+'/input_b2', b2)
        np.save(self.datadir+'/input_ab', ab)

        consts = -1.0 * ab / b2
        
        # compute Noise Power
        if self.settings.do_digital:
            # Ideal constants
            print("Ideal constant LNR computation")
            step_time = time.time()
            consts = np.ones(self.nchannels, dtype=np.complex)
            self.compute_cancellation(consts, 'ideal')
            print "done (" + str(time.time() - step_time) + "[s])"

            # calibrated constants
            print("Calibrated constant LNR computation")
            step_time = time.time()
            consts = -1.0 * ab / b2
            self.compute_cancellation(consts, 'cal')
            print "done (" + str(time.time() - step_time) + "[s])"
        
        if self.settings.do_analog:
            # Analog computation
            print("Analog LNR computation")
            step_time = time.time()
            self.compute_analog_cancellation()
            print "done (" + str(time.time() - step_time) + "[s])" 
        
        plt.pause(self.settings.pause_time)

        time.sleep(1)
        # turn off sources
        #turn_off_sources(self.lo_sources)

        # compress saved data
        print "\tCompressing data..."; step_time = time.time()
        tar = tarfile.open(self.datadir + ".tar.gz", "w:gz")
        for datafile in os.listdir(self.datadir):
            tar.add(self.datadir + '/' + datafile, datafile)
        tar.close()
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        # delete data folder
        shutil.rmtree(self.datadir)

        print "Total time: " + str(time.time() - initial_time) + "[s]"
        print("Close plots to finish.")

    def compute_ab_params(self):
        """
        Compute the ab parameters using noise as an input.
        The ab paramters are the power of the first input (a2), the power
        of the second input (b2), and the correlation between the inputs,
        i.e. the first multiplied by the conjugated of the second (ab).
        :return: ab parameters.
        """
        # get power-crosspower data
        time.sleep(5)
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
        plt.pause(self.settings.pause_time)

        return cal_a2, cal_b2, cal_ab

    def compute_cancellation(self, consts, label):
        """
        Compute LNR for a set of constants.
        """
        sleep_time = 5
        
        # positive constants
        self.load_constants(consts)
        time.sleep(sleep_time)
        self.synfigure.fig.canvas.set_window_title('LNR Computation ' + label + ' RF')
        pow_rf = self.fpga.get_bram_data(self.settings.synth_info)

        # plot pow
        pow_rf_plot = self.scale_dbfs_spec_data(pow_rf, self.settings.synth_info)
        self.synfigure.axes[0].plot(pow_rf_plot)
        plt.pause(self.settings.pause_time)

        # negative constants
        self.load_constants(-1*consts)
        time.sleep(sleep_time)
        self.synfigure.fig.canvas.set_window_title('LNR Computation ' + label + ' LO')
        pow_lo = self.fpga.get_bram_data(self.settings.synth_info)
        plt.pause(self.settings.pause_time)

        # plot pow
        pow_lo_plot = self.scale_dbfs_spec_data(pow_lo, self.settings.synth_info)
        self.synfigure.axes[0].plot(pow_lo_plot)

        # cancellation computation
        lnr = np.array(pow_lo, dtype=np.float64) / np.array(pow_rf, dtype=np.float64)

        # save syn data
        np.save(syn_datadir+"/" + label + "_pow_rf", pow_rf) 
        np.save(syn_datadir+"/" + label + "_pow_lo", pow_lo) 
        np.save(syn_datadir+"/" + label + "_lnr", lnr) 

    def compute_cancellation_analog(self):
        """
        Compute analog LNR.
        """
        sleep_time = 5
        
        # load zero constants, to avoid digital combination
        consts = np.zeros(self.nchannels, dtype=np.complex)
        self.load_constants(consts)

        # 0 degrees combiner
        self.test_source.turn_output_off()
        raw_input("Put 0 degree combiner and press enter...")
        self.test_source.turn_output_on()
        time.sleep(sleep_time)
        self.synfigure.fig.canvas.set_window_title('LNR Computation ' + label + ' RF')
        pow_rf = self.fpga.get_bram_data(self.settings.synth_info)

        # plot pow
        pow_rf_plot = self.scale_dbfs_spec_data(pow_rf, self.settings.synth_info)
        self.synfigure.axes[0].plot(pow_rf_plot)

        # 180 degrees combiner
        self.test_source.turn_output_off()
        raw_input("Put 180 degree combiner and press enter...")
        self.test_source.turn_output_on()
        time.sleep(sleep_time)
        self.synfigure.fig.canvas.set_window_title('LNR Computation ' + label + ' LO')
        pow_lo = self.fpga.get_bram_data(self.settings.synth_info)

        # plot pow
        pow_lo_plot = self.scale_dbfs_spec_data(pow_lo, self.settings.synth_info)
        self.synfigure.axes[0].plot(pow_lo_plot)

        # cancellation computation
        lnr = np.array(pow_lo, dtype=np.float64) / np.array(pow_rf, dtype=np.float64)

        # save syn data
        np.save(syn_datadir+"/analog_pow_rf", pow_rf)
        np.save(syn_datadir+"/analog_pow_lo", pow_lo)
        np.save(syn_datadir+"/analog_lnr", lnr) 
