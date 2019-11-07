import os, time, datetime, itertools, json, tarfile, shutil
import numpy as np
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels, init_sources, turn_off_sources
from ..calanfigure import CalanFigure
from ..instruments.generator import Generator, create_generator
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis
from ..digital_sideband_separation.dss_calibrator import get_lo_combinations, float2fixed

class BmToneLnrComputation(Experiment):
    """
    This class is used to compute the LNR of a Balance Mixer, for calibrated,
    ideal constants, and analog setups.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.synth_info)
        self.freqs = np.linspace(0, self.bw, self.nchannels, endpoint=False)
        
        # test channels array
        self.syn_channels  = range(self.settings.syn_chnl_start, self.settings.syn_chnl_stop, self.settings.syn_chnl_step)
        self.syn_freqs = self.freqs[self.syn_channels]

        # const dtype info
        self.consts_nbits = np.dtype(self.settings.const_brams_info['data_type']).alignment * 8
        self.consts_bin_pt = self.settings.const_bin_pt

        # sources (RF and LOs)
        self.test_source   = create_generator(self.settings.rf_source)
        self.sources = [self.test_source]
        self.lo_combinations = get_lo_combinations(self.settings.lo_sources)
        
        # figures
        self.synfigure = CalanFigure(n_plots=3, create_gui=False)
        
        # axes on figures
        self.synfigure.create_axis(0, SpectrumAxis, self.freqs, 'ZDOK0 spec')
        self.synfigure.create_axis(1, SpectrumAxis, self.freqs, 'ZDOK1 spec')
        self.synfigure.create_axis(2, SpectrumAxis, self.freqs, 'Synth spec')
        self.synfigure.create_axis(3, SpectrumAxis, self.freqs, 'Cancellation')

        # data save attributes
        self.dataname = self.settings.boffile[:self.settings.boffile.index('.')]
        self.dataname = 'bmtest ' + self.dataname
        self.datadir = self.dataname + ' ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.testinfo = {'bw'               : self.bw,
                         'nchannels'        : self.nchannels,
                         'syn_acc_len'      : self.fpga.read_reg(self.settings.synth_info['acc_len_reg']),
                         'syn_chnl_step'    : self.settings.syn_chnl_step,
                         'lo_combinations'  : self.lo_combinations}

        os.mkdir(self.datadir)
        with open(self.datadir + '/testinfo.json', 'w') as jsonfile:
            json.dump(self.testinfo, jsonfile, indent=4)
        
    def run_lnr_computation(self):
        """
        Perform LNR computation for the different setups of the balance mixer. 
        """
        init_sources(self.sources)
        initial_time = time.time()

        if self.settings.do_digital:
            # Ideal constants
            print("Ideal constant LNR computation")
            step_time = time.time()
            consts = np.ones(self.nchannels, dtype=np.complex)
            lnr_ideal_usb, lnr_ideal_lsb = self.compute_cancellation(consts, 'ideal')
            print "done (" + str(time.time() - step_time) + "[s])"

            # calibrated constants
            print("Calibrated constant LNR computation")
            step_time = time.time()
            consts = self.get_constants()
            lnr_cal_usb, lnr_cal_lsb = self.compute_cancellation(consts, 'cal')
            print "done (" + str(time.time() - step_time) + "[s])"
        
        if self.settings.do_analog:
            # Analog computation
            print("Analog LNR computation")
            step_time = time.time()
            lnr_analog_usb, lnr_analog_lsb = self.compute_analog_cancellation()
            print "done (" + str(time.time() - step_time) + "[s])"

        turn_off_sources(self.sources)
        self.print_cancellation_plot()

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

    def compute_cancellation(self, consts, label):
        """
        Compute the amount of cancellation for the balanced mixer by loading 
        calibration constants, and then the negative of the constants, and
        computing the difference of power for a test tone. The total number of 
        channels used for the noise power computations can be controlled by the
        config file parameter syn_chnl_step.
        """
        sleep_time = 1
        lo_freq = self.settings.lo_source['lo_freq']
        rf_freqs_usb = lo_freq + self.freqs
        rf_freqs_lsb = lo_freq - self.freqs

        syn_datadir = self.datadir + '/' + label
        os.mkdir(syn_datadir)

        # positive constants
        self.load_constants(consts)
        time.sleep(sleep_time)
        self.synfigure.fig.canvas.set_window_title('LNR Computation ' + label + ' USB Pos')
        syn_usb_pos = self.get_calibration_tone_power(rf_freqs_usb, label + '_pos_usb', syn_datadir)
        self.synfigure.fig.canvas.set_window_title('LNR Computation ' + label + ' LSB Pos')
        syn_lsb_pos = self.get_calibration_tone_power(rf_freqs_lsb, label + '_pos_lsb', syn_datadir)
        
        # negative constants
        self.load_constants(-1*consts)
        time.sleep(sleep_time)
        self.synfigure.fig.canvas.set_window_title('LNR Computation ' + label + ' USB Neg')
        syn_usb_neg = self.get_calibration_tone_power(rf_freqs_usb, label + '_neg_usb', syn_datadir)
        self.synfigure.fig.canvas.set_window_title('LNR Computation ' + label + ' LSB Neg')
        syn_lsb_neg = self.get_calibration_tone_power(rf_freqs_lsb, label + '_neg_lsb', syn_datadir)

        # cancellation computation
        lnr_usb = np.array(syn_usb_neg, dtype=np.float64) / np.array(syn_usb_pos, dtype=np.float64)
        lnr_lsb = np.array(syn_lsb_neg, dtype=np.float64) / np.array(syn_lsb_pos, dtype=np.float64)

        # save syn data
        np.savez(syn_datadir+"/cancellation",
            syn_usb_pos=syn_usb_pos, syn_lsb_pos=syn_lsb_pos,
            syn_usb_neg=syn_usb_neg, syn_lsb_neg=syn_lsb_neg,
            lnr_usb=lnr_usb, lnr_lsb=lnr_lsb)

        return lnr_usb, lnr_lsb

    def compute_analog_cancellation(self):
        """
        Compute the amount of cancellation for the balanced mixer by loading 
        calibration constants, and then the negative of the constants, and
        computing the difference of power for a test tone. The total number of 
        channels used for the noise power computations can be controlled by the
        config file parameter syn_chnl_step.
        """
        sleep_time = 1
        lo_freq = self.settings.lo_source['lo_freq']
        rf_freqs_usb = lo_freq + self.freqs
        rf_freqs_lsb = lo_freq - self.freqs

        syn_datadir = self.datadir + '/analog'
        os.mkdir(syn_datadir)

        # load zero constants, to avoid digital combination
        consts = np.zeros(self.nchannels, dtype=np.complex)
        self.load_constants(consts)

        # 0 degrees combiner
        self.test_source.turn_output_off()
        raw_input("Put 0 degree combiner and press enter...")
        self.test_source.turn_output_on()
        self.synfigure.fig.canvas.set_window_title('LNR Computation analog USB Pos')
        syn_usb_pos = self.get_calibration_tone_power(rf_freqs_usb, 'analog_pos_usb', syn_datadir)
        self.synfigure.fig.canvas.set_window_title('LNR Computation analog LSB Pos')
        syn_lsb_pos = self.get_calibration_tone_power(rf_freqs_lsb, 'analog_pos_lsb', syn_datadir)
        
        # 180 degrees combiner
        self.test_source.turn_output_off()
        raw_input("Put 180 degree combiner and press enter...")
        self.test_source.turn_output_on()
        self.synfigure.fig.canvas.set_window_title('LNR Computation analog USB Neg')
        syn_usb_neg = self.get_calibration_tone_power(rf_freqs_usb, 'analog_neg_usb', syn_datadir)
        self.synfigure.fig.canvas.set_window_title('LNR Computation LSB Neg')
        syn_lsb_neg = self.get_calibration_tone_power(rf_freqs_lsb, 'analog_neg_lsb', syn_datadir)

        # cancellation computation
        lnr_usb = np.array(syn_usb_neg, dtype=np.float64) / np.array(syn_usb_pos, dtype=np.float64)
        lnr_lsb = np.array(syn_lsb_neg, dtype=np.float64) / np.array(syn_lsb_pos, dtype=np.float64)

        # save syn data
        np.savez(syn_datadir+"/cancellation",
            syn_usb_pos=syn_usb_pos, syn_lsb_pos=syn_lsb_pos,
            syn_usb_neg=syn_usb_neg, syn_lsb_neg=syn_lsb_neg,
            lnr_usb=lnr_usb, lnr_lsb=lnr_lsb)

        return lnr_usb, lnr_lsb

    def get_calibration_tone_power(self, freqs, label, datadir):
        """
        Sweep a tone through a given frequency list and get the
        power of the tone at the output (synth) of the balance mixer. 
        Assumes that constants were previously loaded.
        :param freqs: list of possible frequencies to sweep, the actual
            frequencies indeces used are given by syn_channels.
        :return: power of tones at output
        """
        rawdata_datadir = self.datadir + '/rawdata'
        if not os.path.exists(rawdata_datadir):
            os.mkdir(rawdata_datadir)

        sleep_time = 1
        syn_arr = []
        for i, chnl in enumerate(self.syn_channels):
            # set generator frequency
            self.test_source.set_freq_mhz(freqs[chnl])
            # plot while the generator is changing to frequency to give the system time to update
            plt.pause(self.settings.pause_time) 
            #plt.pause(sleep_time) 
            
            # get USB power data
            a2_tone, b2_tone = self.fpga.get_bram_data(self.settings.spec_info)
            syn_tone = self.fpga.get_bram_data(self.settings.synth_info)

            # plot spec data
            [a2_tone_plot, b2_tone_plot] = \
                self.scale_dbfs_spec_data([a2_tone, b2_tone], self.settings.spec_info)
            syn_tone_plot = self.scale_dbfs_spec_data(syn_tone, self.settings.synth_info)
            self.synfigure.axes[0].plot(a2_tone_plot)
            self.synfigure.axes[1].plot(b2_tone_plot)
            self.synfigure.axes[2].plot(syn_tone_plot)

            # save syn rawdata
            np.savez(rawdata_datadir+'/'+label+'_chnl_'+str(chnl), 
                a2_tone=a2_tone, b2_tone=b2_tone, syn_tone=syn_tone)

            syn_arr.append(syn_tone[chnl])

        return syn_arr

    def get_constants(self):
        """
        Get calibration constants from .tar.gz file.
        :return: calibration constats.
        """
        tar_datafile = tarfile.open(self.settings.saved_params['datadir'])
        ab_datafile = tar_datafile.extractfile('ab_params.npz')
        ab_data = np.load(ab_datafile)
        a2 = ab_data['a2']; b2 = ab_data['b2']; ab = ab_data['ab']
        return -1 * ab / b2 # ab* / bb* = a/b

    def load_constants(self, consts):
        consts_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts))
        consts_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts))
        self.fpga.write_bram_data(self.settings.const_brams_info, [consts_real, consts_imag])

    def print_cancellation_plot(self):
        """
        Print cancellation plot using the data saved from the test.
        """
        fig = plt.figure()
        
        lo_freq = self.settings.lo_source['lo_freq']
        usb_freqs = lo_freq + self.syn_freqs
        lsb_freqs = lo_freq - self.syn_freqs


        try:
            cancel_data_ideal = np.load(self.datadir + '/ideal/cancellation.npz')
            ideal_lnr_usb = 10*np.log10(cancel_data_ideal['lnr_usb'])
            ideal_lnr_lsb = 10*np.log10(cancel_data_ideal['lnr_lsb'])
            plt.plot(usb_freqs, ideal_lnr_usb, '-b', label='ideal')
            plt.plot(lsb_freqs, ideal_lnr_lsb, '-b')
        except IOError:
            pass

        try:
            cancel_data_cal = np.load(self.datadir + '/cal/cancellation.npz')
            cal_lnr_usb = 10*np.log10(cancel_data_cal['lnr_usb'])
            cal_lnr_lsb = 10*np.log10(cancel_data_cal['lnr_lsb'])
            plt.plot(usb_freqs, cal_lnr_usb, '-g', label='cal')
            plt.plot(lsb_freqs, cal_lnr_lsb, '-g')
        except IOError:
            pass

        try:
            cancel_data_analog = np.load(self.datadir + '/analog/cancellation.npz')
            analog_lnr_usb = 10*np.log10(cancel_data_analog['lnr_usb'])
            analog_lnr_lsb = 10*np.log10(cancel_data_analog['lnr_lsb'])
            plt.plot(usb_freqs, analog_lnr_usb, '-r', label='analog')
            plt.plot(lsb_freqs, analog_lnr_lsb, '-r')
        except IOError:
            pass

        plt.grid()
        plt.xlabel('Frequency [GHz]')
        plt.ylabel('LNR [dB]')
        plt.legend()
        
        plt.savefig(self.datadir + '/lnr.pdf', bbox_inches='tight')
