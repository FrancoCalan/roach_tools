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

class BmNoiseCalibrator(Experiment):
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
                         'lo_combinations'  : self.lo_combinations}

        if self.save_data:
            os.mkdir(self.datadir)
            with open(self.datadir + '/testinfo.json', 'w') as jsonfile:
                json.dump(self.testinfo, jsonfile, indent=4)

    def run_bm_noise_test(self):
        """
        Perform a balance mixer test calibration using
        noise as input.
        """
        #init_sources(self.lo_sources)
        self.lo_sources[0].set_power_dbm()
        self.lo_sources[0].turn_output_on()

        initial_time = time.time()
        for lo_comb in self.lo_combinations:
            lo_label = '_'.join(['LO'+str(i+1)+'_'+str(lo/1e3)+'GHZ' for i,lo in enumerate(lo_comb)]) 
            lo_datadir = self.datadir + "/" + lo_label
            if self.save_data:
                os.mkdir(lo_datadir)

            print lo_label
            for i, lo in enumerate(lo_comb):
                self.lo_sources[i].set_freq_mhz(lo)
                
                # get compute ab params
                print "\tComputing ab parameters with noise input..."; step_time = time.time()
                a2, b2, ab = self.compute_ab_params(lo_datadir)
                print "\tdone (" + str(time.time() - step_time) + "[s])" 

                # save ab ratios
                if self.save_data:
                    # saving a2, b2 and ab as usb and lsb to make it
                    # compatible with tone calibration
                    np.savez(lo_datadir+'/ab_params', 
                        a2_usb=a2, b2_usb=b2, ab_usb=ab,
                        a2_lsb=a2, b2_lsb=b2, ab_lsb=ab)

                consts = -1.0 * ab / b2
                
                # compute Noise Power
                if self.settings.compute_cancellation:
                    print "\tComputing Noise Power..."; step_time = time.time()
                    self.synfigure.fig.canvas.set_window_title('Noise Power Computation ' + lo_label)
                    self.compute_cancellation(lo_datadir, consts)
                    print "\tdone (" + str(time.time() - step_time) + "[s])"
                
                plt.pause(self.settings.pause_time)

        time.sleep(10)
        # turn off sources
        #turn_off_sources(self.lo_sources)

        if self.save_data:
            # print canccellation (full) plot
            if self.settings.compute_cancellation:
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
        print("Close plots to finish.")

    def compute_ab_params(self, lo_datadir):
        """
        Compute the ab parameters using noise as an input.
        The ab paramters are the power of the first input (a2), the power
        of the second input (b2), and the correlation between the inputs,
        i.e. the first multiplied by the conjugated of the second (ab).
        :param lo_datadir: directory for the data of the current LO frequency 
            combination.
        :return: ab parameters.
        """
        # get power-crosspower data
        time.sleep(10)
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

        return cal_a2, cal_b2, ab

    def compute_cancellation(self, lo_datadir, cal_consts):
        """
        Compare spectra from uncalibrated, ideal constants and digital 
        calibrated balance mixer.
        :param lo_datadir: diretory for the data of the current LO frequency 
            combination.
        """
        # get power data
        a2  = self.fpga.get_bram_data(self.settings.spec_info)[0]

        # load constants
        consts = self.settings.ideal_const*np.ones(self.nchannels, dtype=np.complex)
        print "\tLoading ideal constants..."; step_time = time.time()
        consts_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts))
        consts_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts))
        self.fpga.write_bram_data(self.settings.const_brams_info, 
            [consts_real, consts_imag])
        print "\tdone (" + str(time.time() - step_time) + "[s])"
        time.sleep(1)
        ideal_syn = self.fpga.get_bram_data(self.settings.synth_info)

        consts = cal_consts
        print "\tLoading calibration constants..."; step_time = time.time()
        consts_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts))
        consts_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts))
        self.fpga.write_bram_data(self.settings.const_brams_info, 
            [consts_real, consts_imag])
        print "\tdone (" + str(time.time() - step_time) + "[s])"
        time.sleep(1)
        syn = self.fpga.get_bram_data(self.settings.synth_info)

        # plot cancellation
        a2_plot = self.scale_dbfs_spec_data(a2, self.settings.spec_info)
        ideal_syn_plot = self.scale_dbfs_spec_data(ideal_syn, self.settings.synth_info)
        syn_plot = self.scale_dbfs_spec_data(syn, self.settings.synth_info)
        self.synfigure.axes[0].plot([a2_plot, ideal_syn_plot, syn_plot])

        # save syn data
        if self.save_data:
            np.savez(lo_datadir+"/cancellation", 
                uncalibrated=a2_plot, ideal=ideal_syn_plot, calibrated=syn_plot)

    def print_cancellation_plot(self):
        """
        Print cancellation plot using the data saved from the test.
        """
        fig = plt.figure()
        for lo_comb in self.lo_combinations:
            lo_label = '_'.join(['LO'+str(i+1)+'_'+str(lo/1e3)+'GHZ' for i,lo in enumerate(lo_comb)]) 
            datadir = self.datadir + '/' + lo_label

            cancellation_data = np.load(datadir + '/cancellation.npz')
            
            freqs = lo_comb[0]/1.0e3 + sum(lo_comb[1:])/1.0e3 + self.freqs/1.e3
            
            colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
            plt.plot(freqs, cancellation_data['uncalibrated'], colors[0])
            plt.plot(freqs, cancellation_data['ideal'], colors[1])
            plt.plot(freqs, cancellation_data['calibrated'], colors[2])
            plt.grid()
            plt.xlabel('Frequency [GHz]')
            plt.ylabel('Noise Power [dB]')
            # legend
            handles = [Rectangle((0,0),1,1,color=c,ec="k") for c in colors[:3]]
            labels= ["uncalibrated", "ideal constants", "calibrated constants"]
            plt.legend(handles, labels)
        
        plt.savefig(self.datadir + '/cancellation.pdf', bbox_inches='tight')
