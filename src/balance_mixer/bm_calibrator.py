import os, time, datetime, itertools, json, tarfile, shutil
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels, init_sources, turn_off_sources
from ..calanfigure import CalanFigure
from ..instruments.generator import Generator, create_generator
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis
from srr_axis import SrrAxis

class DssCalibrator(Experiment):
    """
    This class is used to calibrate a Sideband Separating receiver.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.synth_info)
        self.freqs = np.linspace(0, self.bw, self.nchannels, endpoint=False)
        
        # test channels array
        self.cal_channels  = range(1, self.nchannels, self.settings.cal_chnl_step)
        self.syn_channels  = range(1, self.nchannels, self.settings.syn_chnl_step)
        self.cal_freqs = self.freqs[self.cal_channels]
        self.syn_freqs = self.freqs[self.syn_channels]

        # const dtype info
        self.consts_nbits = np.dtype(self.settings.const_brams_info['data_type']).alignment * 8
        self.consts_bin_pt = self.settings.const_bin_pt

        # sources (RF and LOs)
        self.rf_source   = create_generator(self.settings.rf_source)
        self.test_source = create_generator(self.settings.test_source)
        self.lo_sources  = [create_generator(lo_source) for lo_source in self.settings.lo_sources]
        self.sources = self.lo_sources + [self.rf_source, test_source]
        self.lo_combinations = get_lo_combinations(self.settings.lo_sources)
        
        # figures
        self.calfigure_lsb = CalanFigure(n_plots=4, create_gui=False)
        self.calfigure_usb = CalanFigure(n_plots=4, create_gui=False)
        self.synfigure     = CalanFigure(n_plots=3, create_gui=False)
        
        # axes on figures
        self.calfigure_lsb.create_axis(0, SpectrumAxis,  self.freqs, 'ZDOK0 spec')
        self.calfigure_lsb.create_axis(1, SpectrumAxis,  self.freqs, 'ZDOK1 spec')
        self.calfigure_lsb.create_axis(2, MagRatioAxis,  self.freqs, ['ZDOK0/ZDOK1'], 'Magnitude Ratio')
        self.calfigure_lsb.create_axis(3, AngleDiffAxis, self.freqs, ['ZDOK0-ZDOK1'], 'Angle Difference')
        self.calfigure_usb.set_window_title('Calibration USB ' + lo_label)
        #
        self.calfigure_usb.create_axis(0, SpectrumAxis,  self.freqs, 'ZDOK0 spec')
        self.calfigure_usb.create_axis(1, SpectrumAxis,  self.freqs, 'ZDOK1 spec')
        self.calfigure_usb.create_axis(2, MagRatioAxis,  self.freqs, ['ZDOK1/ZDOK0'], 'Magnitude Ratio')
        self.calfigure_usb.create_axis(3, AngleDiffAxis, self.freqs, ['ZDOK1-ZDOK0'], 'Angle Difference')
        self.calfigure_lsb.set_window_title('Calibration LSB ' + lo_label)
        #
        self.synfigure.create_axis(0, SpectrumAxis, self.freqs, 'Synth spec')
        self.synfigure.create_axis(1, SpectrumAxis, self.freqs, 'Noise Power USB')
        self.synfigure.create_axis(2, SpectrumAxis, self.freqs, 'Noise Power LSB')
        self.synfigure.fig.canvas.set_window_title('SRR Computation ' + lo_label)

        # data save attributes
        self.dataname = os.path.splitext(self.settings.boffile)[0]
        self.dataname = 'bmtest ' + self.dataname + ' '
        self.datadir = self.settings.datadir + '_' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        os.mkdir(self.datadir)
        self.testinfo = {'bw'               : self.bw,
                         'nchannels'        : self.nchannels,
                         'cal_acc_len'      : self.fpga.read_reg(self.settings.spec_info['acc_len_reg']),
                         'syn_acc_len'      : self.fpga.read_reg(self.settings.synth_info['acc_len_reg']),
                         'cal_method'       : self.settings.cal_method,
                         'cal_chnl_step'    : self.settings.cal_chnl_step,
                         'syn_chnl_step'    : self.settings.srr_chnl_step,
                         'lo_combinations'  : self.lo_combinations}

        with open(self.datadir + '/testinfo.json', 'w') as jsonfile:
            json.dump(self.testinfo, jsonfile, indent=4)
        
    def run_dss_test(self):
        """
        Perform a full DSS test, with constants and SRR computation. 
        """
        init_sources(self.sources)

        initial_time = time.time()
        for lo_comb in self.lo_combinations:
            cycle_time = time.time()
            lo_label = '_'.join(['LO'+str(i+1)+'_'+str(lo/1e3)+'GHZ' for i,lo in enumerate(lo_comb)]) 
            lo_datadir = self.datadir + "/" + lo_label
            os.mkdir(lo_datadir)
            
            print lo_label
            for i, lo in enumerate(lo_comb):
                self.lo_sources[i].set_freq_mhz(lo)
                
                # compute calibration constants (sideband ratios)
                print "\tComputing sideband ratios, tone in USB..."; step_time = time.time()
                sb_ratios_usb = self.compute_sb_ratios_usb(lo_comb, lo_datadir)
                print "\tdone (" + str(time.time() - step_time) + "[s])" 

                print "\tComputing sideband ratios, tone in LSB..."; step_time = time.time()
                sb_ratios_lsb = self.compute_sb_ratios_lsb(lo_comb, lo_datadir)
                print "\tdone (" + str(time.time() - step_time) + "[s])"

                # save sb ratios
                np.savez(lo_datadir+'/sb_ratios', sb_ratios_usb=sb_ratios_usb, sb_ratios_lsb=sb_ratios_lsb)

                # constant computation
                if self.settings.method == 'LSB'
                    consts = -1.0 * sb_ratios_lsb
                elif self.settings.method == 'Higher'
                    consts = -1.0 * get_higher_constants(sb_ratios_lsb, sb_ratios_usb)
                elif self.settings.method == 'Optimal'
                    consts = -1.0 * # a2_usb x b2_usb* + a2_lsb x b2_lsb* /
                                    # b2_usb + b2_lsb

                # load constants
                print "\tLoading constants..."; step_time = time.time()
                consts_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts))
                consts_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts))
                self.fpga.write_bram_data_interleave(self.settings.const_brams_info, 
                    [consts_real, consts_imag])
                print "\tdone (" + str(time.time() - step_time) + "[s])"

                # compute Noise Power
                print "\tComputing Noise Power..."; step_time = time.time()
                self.compute_srr(lo_comb, lo_datadir)
                print "\tdone (" + str(time.time() - step_time) + "[s])"

        # turn off sources
        turn_off_sources(self.sources)

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

    def compute_sb_ratios_usb(self, lo_comb, lo_datadir):
        """
        Sweep a tone through the receiver bandwidth and computes the USB
        sideband ratio for a number of FFT channel. The USB sideband ratio is 
        defined as the complex division LSB/USB when the test tone is in the USB.
        The total number of  channels used for the computations depends in the config 
        file parameter cal_chnl_step. The channels not measured are interpolated.
        :param lo_comb: LO frequency combination for the test. Used to properly set
            the RF test input.
        :param lo_datadir: diretory for the data of the current LO frequency combination.
        :return: USB sideband ratios
        """
        sb_ratios = []
        rf_freqs = lo_comb[0] + sum(lo_comb[1:]) + self.freqs

        cal_datadir = lo_datadir + '/cal_rawdata'
        # creates directory for the raw calibration data
        os.mkdir(cal_datadir)

        for i, chnl in enumerate(self.cal_channels):
            # set generator frequency
            self.rf_source.set_freq_mhz(rf_freqs[chnl])    
            # plot while the generator is changing to frequency to give the system time to update
            plt.pause(self.settings.pause_time) 

            # get power-crosspower data
            cal_a2, cal_b2 = self.fpga.get_bram_data_interleave(self.settings.spec_info)
            cal_ab_re, cal_ab_im = self.fpga.get_bram_data_interleave(self.settings.crosspow_info)

            # save cal rawdata
            np.savez(cal_datadir + '/usb_chnl_' + str(chnl), 
                cal_a2=cal_a2, cal_b2=cal_b2, cal_ab_re=cal_ab_re, cal_ab_im=cal_ab_im)

            # compute constant
            ab = cal_ab_re[chnl] + 1j*cal_ab_im[chnl]
            sb_ratios.append(np.conj(ab) / cal_a2[chnl]) # (ab*)* / aa* = a*b / aa* = b/a = LSB/USB

            # plot spec data
            [cal_a2_plot, cal_b2_plot] = \
                self.scale_dbfs_spec_data([cal_a2, cal_b2], self.settings.spec_info)
            self.calfigure_usb.axes[0].ploty(cal_a2_plot)
            self.calfigure_usb.axes[1].ploty(cal_b2_plot)

            # plot the magnitude ratio and phase difference
            self.calfigure_usb.axes[2].plotxy(self.cal_freqs[:i+1], np.abs(sb_ratios))
            self.calfigure_usb.axes[3].plotxy(self.cal_freqs[:i+1], np.angle(sb_ratios, deg=True))

        # plot last frequency
        plt.pause(self.settings.pause_time) 

        # compute interpolations
        sb_ratios = np.interp(range(self.nchannels), self.cal_channels, sb_ratios)

        return sb_ratios

    def compute_sb_ratios_lsb(self, lo_comb, lo_datadir):
        """
        Sweep a tone through the receiver bandwidth and computes the LSB
        sideband ratio for a number of FFT channel. The LSB sideband ratio is 
        defined as the complex division USB/LSB when the test tone is in the LSB.
        The total number of  channels used for the computations depends in the config 
        file parameter cal_chnl_step. The channels not measured are interpolated.
        :param lo_comb: LO frequency combination for the test. Used to properly set
            the RF test input.
        :param lo_datadir: diretory for the data of the current LO frequency combination.
        :return: USB sideband ratios
        """
        sb_ratios = []
        rf_freqs = lo_comb[0] - sum(lo_comb[1:]) - self.freqs

        cal_datadir = lo_datadir + '/cal_rawdata'

        for i, chnl in enumerate(self.cal_channels):
            # set generator frequency
            self.rf_source.set_freq_mhz(rf_freqs[chnl])    
            # plot while the generator is changing to frequency to give the system time to update
            plt.pause(self.settings.pause_time) 

            # get power-crosspower data
            cal_a2, cal_b2 = self.fpga.get_bram_data_interleave(self.settings.spec_info)
            cal_ab_re, cal_ab_im = self.fpga.get_bram_data_interleave(self.settings.crosspow_info)

            # save cal rawdata
            np.savez(cal_datadir + '/lsb_chnl_' + str(chnl), 
                cal_a2=cal_a2, cal_b2=cal_b2, cal_ab_re=cal_ab_re, cal_ab_im=cal_ab_im)

            # compute constant
            ab = cal_ab_re[chnl] + 1j*cal_ab_im[chnl]
            sb_ratios.append(ab / cal_b2[chnl]) # ab* / bb* = a/b = USB/LSB.

            # plot spec data
            [cal_a2_plot, cal_b2_plot] = \
                self.scale_dbfs_spec_data([cal_a2, cal_b2], self.settings.spec_info)
            self.calfigure_lsb.axes[0].ploty(cal_a2_plot)
            self.calfigure_lsb.axes[1].ploty(cal_b2_plot)
            
            # plot the magnitude ratio and phase difference
            self.calfigure_lsb.axes[2].plotxy(self.cal_freqs[:i+1], np.abs(sb_ratios))
            self.calfigure_lsb.axes[3].plotxy(self.cal_freqs[:i+1], np.angle(sb_ratios, deg=True))

        # plot last frequency
        plt.pause(self.settings.pause_time) 

        # compute interpolations
        sb_ratios = np.interp(range(self.nchannels), self.cal_channels, sb_ratios)

        return sb_ratios

    def compute_srr(self, M_DSB, lo_comb, lo_datadir):
        """
        Compute SRR from the DSS receiver using the Kerr method
        (see ALMA Memo 357 (http://legacy.nrao.edu/alma/memos/html-memos/abstracts/abs357.html)).
        The total number of channels used for the SRR computations
        can be controlled by the config file parameter srr_chnl_step.
        :param M_DSB: constant computed in the hotcold test used for the Kerr method.
        :param lo_comb: LO frequency combination for the test. Used to properly set
            the RF test input.
        :param lo_datadir: diretory for the data of the current LO frequency combination.
        """
        srr_usb = []
        srr_lsb = []
        rf_freqs_usb = lo_comb[0] + sum(lo_comb[1:]) + self.freqs
        rf_freqs_lsb = lo_comb[0] - sum(lo_comb[1:]) - self.freqs

        syn_datadir = lo_datadir + '/srr_rawdata'
        os.mkdir(syn_datadir)
 
        for i, chnl in enumerate(self.srr_channels):
            # set generator at USB frequency
            self.rf_source.set_freq_mhz(rf_freqs_usb[chnl])
            # plot while the generator is changing to frequency to give the system time to update
            plt.pause(self.settings.pause_time) 
            
            # get USB and LSB power data
            a2_tone_usb, b2_tone_usb = self.fpga.get_bram_data_interleave(self.settings.synth_info)

            # plot spec data
            [a2_tone_usb_plot, b2_tone_usb_plot] = \
                self.scale_dbfs_spec_data([a2_tone_usb, b2_tone_usb], self.settings.synth_info)
            self.srrfigure.axes[0].plot(a2_tone_usb_plot)
            self.srrfigure.axes[1].plot(b2_tone_usb_plot)

            # set generator at LSB frequency
            self.rf_source.set_freq_mhz(rf_freqs_lsb[chnl])
            # plot while the generator is changing to frequency to give the system time to update
            plt.pause(self.settings.pause_time) 
            
            # get USB and LSB power data
            a2_tone_lsb, b2_tone_lsb = self.fpga.get_bram_data_interleave(self.settings.synth_info)

            # save syn rawdata
            np.savez(syn_datadir+'/chnl_'+str(chnl), a2_tone_usb=a2_tone_usb, b2_tone_usb=b2_tone_usb, 
                a2_tone_lsb=a2_tone_lsb, b2_tone_lsb=b2_tone_lsb)

            # plot spec data
            [a2_tone_lsb_plot, b2_tone_lsb_plot] = \
                self.scale_dbfs_spec_data([a2_tone_lsb, b2_tone_lsb], self.settings.synth_info)
            self.srrfigure.axes[0].ploty(a2_tone_lsb_plot)
            self.srrfigure.axes[1].ploty(b2_tone_lsb_plot)

            # Compute sideband ratios
            ratio_usb = np.divide(a2_tone_usb[chnl], b2_tone_usb[chnl], dtype=np.float64)
            ratio_lsb = np.divide(b2_tone_lsb[chnl], a2_tone_lsb[chnl], dtype=np.float64)
            
            # Compute SRR as per Kerr calibration if set in config file
            if self.settings.kerr_correction:
                new_srr_usb = ratio_usb * (ratio_lsb*M_DSB[chnl] - 1) / (ratio_usb - M_DSB[chnl])
                new_srr_lsb = ratio_lsb * (ratio_usb - M_DSB[chnl]) / (ratio_lsb*M_DSB[chnl] - 1)
            else: # compute SRR as sideband ratio
                new_srr_usb = ratio_usb
                new_srr_lsb = ratio_lsb

            srr_usb.append(10*np.log10(new_srr_usb))
            srr_lsb.append(10*np.log10(new_srr_lsb))

            # plot the magnitude ratio and phase difference
            self.srrfigure.axes[2].plotxy(self.srr_freqs[:i+1], srr_usb)
            self.srrfigure.axes[3].plotxy(self.srr_freqs[:i+1], srr_lsb)
        
        # plot last frequency
        plt.pause(self.settings.pause_time)

        # save srr data
        np.savez(lo_datadir+"/srr", srr_usb=srr_usb, srr_lsb=srr_lsb)
