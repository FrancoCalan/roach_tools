import os, time, datetime, itertools, json, tarfile, shutil
import numpy as np
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels, init_sources, turn_off_sources
from ..calanfigure import CalanFigure
from ..instruments.generator import Generator, create_generator
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis
from ..digital_sideband_separation.dss_calibrator import get_lo_combination, float2fixed, check_overflow
#from srr_axis import SrrAxis

class DomtCalibrator(Experiment):
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
        self.rf_source  = create_generator(self.settings.rf_source)
        self.lo_sources = [create_generator(lo_source) for lo_source in self.settings.lo_sources]
        self.sources = self.lo_sources + [self.rf_source]
        self.lo_combinations = get_lo_combinations(self.settings.lo_sources)
        
        # figures
        self.calfigure_0deg  = CalanFigure(n_plots=6, create_gui=False)
        self.calfigure_45deg = CalanFigure(n_plots=6, create_gui=False)
        self.calfigure_90deg = CalanFigure(n_plots=6, create_gui=False)
        #self.synfigure       = CalanFigure(n_plots=4, create_gui=False)
        
        # axes on figures
        self.calfigure_0deg.create_axis(0, SpectrumAxis,  self.freqs, 'ZDOK0 a spec')
        self.calfigure_0deg.create_axis(1, SpectrumAxis,  self.freqs, 'ZDOK0 c spec')
        self.calfigure_0deg.create_axis(2, SpectrumAxis,  self.freqs, 'ZDOK1 a spec')
        self.calfigure_0deg.create_axis(3, SpectrumAxis,  self.freqs, 'ZDOK1 c spec')
        self.calfigure_0deg.create_axis(4, MagRatioAxis,  self.freqs, ['2/1', '3/1', '4/1'], 'Magnitude Ratio')
        self.calfigure_0deg.create_axis(5, AngleDiffAxis, self.freqs, ['2-1', '3-1', '4-1'], 'Angle Difference')
        #
        self.calfigure_45deg.create_axis(0, SpectrumAxis,  self.freqs, 'ZDOK0 a spec')
        self.calfigure_45deg.create_axis(1, SpectrumAxis,  self.freqs, 'ZDOK0 c spec')
        self.calfigure_45deg.create_axis(2, SpectrumAxis,  self.freqs, 'ZDOK1 a spec')
        self.calfigure_45deg.create_axis(3, SpectrumAxis,  self.freqs, 'ZDOK1 c spec')
        self.calfigure_45deg.create_axis(4, MagRatioAxis,  self.freqs, ['2/1', '3/1', '4/1'], 'Magnitude Ratio')
        self.calfigure_45deg.create_axis(5, AngleDiffAxis, self.freqs, ['2-1', '3-1', '4-1'], 'Angle Difference')
        #
        self.calfigure_90deg.create_axis(0, SpectrumAxis,  self.freqs, 'ZDOK0 a spec')
        self.calfigure_90deg.create_axis(1, SpectrumAxis,  self.freqs, 'ZDOK0 c spec')
        self.calfigure_90deg.create_axis(2, SpectrumAxis,  self.freqs, 'ZDOK1 a spec')
        self.calfigure_90deg.create_axis(3, SpectrumAxis,  self.freqs, 'ZDOK1 c spec')
        self.calfigure_90deg.create_axis(4, MagRatioAxis,  self.freqs, ['1/2', '3/2', '4/2'], 'Magnitude Ratio')
        self.calfigure_90deg.create_axis(5, AngleDiffAxis, self.freqs, ['1-2', '3-2', '4-2'], 'Angle Difference')
        #
        # synfigure axes...

        # data save attributes
        self.dataname = self.settings.boffile[:self.settings.boffile.index('.')]
        self.dataname = 'dsstest ' + self.dataname + ' '
        self.datadir = self.dataname + '_' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        os.mkdir(self.datadir)
        self.testinfo = {'bw'               : self.settings.bw,
                         'nchannels'        : self.nchannels,
                         'cal_acc_len'      : self.fpga.read_reg(self.settings.spec_info['acc_len_reg']),
                         'syn_acc_len'      : self.fpga.read_reg(self.settings.synth_info['acc_len_reg']),
                         'kerr_correction'  : self.settings.kerr_correction,
                         'use_ideal_consts' : self.settings.ideal_consts['load'],
                         'ideal_const'      : str(self.settings.ideal_consts['val']),
                         'cal_chnl_step'    : self.settings.cal_chnl_step,
                         'syn_chnl_step'    : self.settings.syn_chnl_step,
                         'lo_combinations'  : self.lo_combinations}

        with open(self.datadir + '/testinfo.json', 'w') as jsonfile:
            json.dump(self.testinfo, jsonfile, indent=4)
        
    def run_domt_test(self):
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
                if not self.settings.ideal_consts['load']:
                    print "\tComputing input ratios, angle 0°..."; step_time = time.time()
                    self.calfigure_0deg.set_window_title('Calibration 0° ' + lo_label)
                    in_ratios_0  = self.compute_input_ratios(lo_comb, lo_datadir, 0, self.calfigure_0deg)
                    print "\tdone (" + str(time.time() - step_time) + "[s])" 

                    print "\tComputing input ratios, angle 90°..."; step_time = time.time()
                    self.calfigure_90deg.set_window_title('Calibration 90° ' + lo_label)
                    in_ratios_90  = self.compute_input_ratios(lo_comb, lo_datadir, 1, self.calfigure_90deg)
                    print "\tdone (" + str(time.time() - step_time) + "[s])" 

                    print "\tComputing input ratios, angle 45°..."; step_time = time.time()
                    self.calfigure_45deg.set_window_title('Calibration 45° ' + lo_label)
                    in_ratios_45  = self.compute_input_ratios(lo_comb, lo_datadir, 0, self.calfigure_45deg)
                    print "\tdone (" + str(time.time() - step_time) + "[s])" 
                    
                    
                    ###############################################
                    # save sb ratios
                    #np.savez(lo_datadir+'/sb_ratios', sb_ratios_usb=sb_ratios_usb, sb_ratios_lsb=sb_ratios_lsb)

                    # constant computation
                    #consts_usb = -1.0 * sb_ratios_usb
                    #consts_lsb = -1.0 * sb_ratios_lsb

                #else:
                #    const = self.settings.ideal_consts['val']
                #    consts_usb = const * np.ones(self.nchannels, dtype=np.complex128)
                #    consts_lsb = const * np.ones(self.nchannels, dtype=np.complex128)

                # load constants
                #print "\tLoading constants..."; step_time = time.time()
                #consts_usb_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts_usb))
                #consts_usb_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts_usb))
                #consts_lsb_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts_lsb))
                #consts_lsb_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts_lsb))
                #self.fpga.write_bram_data(self.settings.const_brams_info, 
                #    [consts_lsb_real, consts_lsb_imag, consts_usb_real, consts_usb_imag])
                #print "\tdone (" + str(time.time() - step_time) + "[s])"

                # compute SRR
                #print "\tComputing SRR..."; step_time = time.time()
                #self.srrfigure.fig.canvas.set_window_title('SRR Computation ' + lo_label)
                #self.compute_srr(M_DSB, lo_comb, lo_datadir)
                #print "\tdone (" + str(time.time() - step_time) + "[s])"

        # turn off sources
        turn_off_sources(self.sources)

        # print srr (full) plot
        #self.print_srr_plot()

        # compress saved data
        print "\tCompressing data..."; step_time = time.time()
        tar = tarfile.open(self.datadir + ".tar.gz", "w:gz")
        for datafile in os.listdir(self.datadir):
            tar.add(self.datadir + '/' + datafile, datafile)
        
        Each element of the correlation 
        matrix correspond to the conjugated multiplication of a pair of complex
        inputs. The matrix is computed by detecting the input with higher power
        and obtaining the conjugated multiplication between this and the rest of
        the inputs. Then the rest is terms of the matrix are derived from the
        ones measured
        tar.close()
        print "\tdone (" + str(time.time() - step_time) + "[s])"

        # delete data folder
        shutil.rmtree(self.datadir)

        print "Total time: " + str(time.time() - initial_time) + "[s]"

    def compute_input_ratios(self, lo_comb, lo_datadir, ref, fig):
        """
        Sweep a tone through the receiver bandwidth and computes the input ratios
        for a number of FFT channel. The input ratios are the complex ratios
        (magnitude ratio and phase difference) between the omt input and a
        designated reference input. The total number of  channels used for the 
        computations depends in the config file parameter cal_chnl_step. The 
        channels not measured are interpolated.
        :param lo_comb: LO frequency combination for the test. Used to properly 
        set the RF test input.
        :param lo_datadir: diretory for the data of the current LO frequency 
            combination.
        :param ref: index of the input used as reference.
        :param fig: figure to plot.
        :return: input ratios as a list of vectors.
        """
        in_ratios = [4*[]]
        rf_freqs = lo_comb[0] + sum(lo_comb[1:]) + self.freqs

        cal_datadir = lo_datadir + '/cal_rawdata'
        # creates directory for the raw calibration data
        os.mkdir(cal_datadir)

        # set the reference for correlation computation
        self.fpga.set_reg('ref_select', ref)

        for i, chnl in enumerate(self.cal_channels):
            # set generator frequency
            self.rf_source.set_freq_mhz(rf_freqs[chnl])    
            # plot while the generator is changing to frequency to give the system time to update
            plt.pause(self.settings.pause_time) 

            # get power-crosspower data
            cal_pow = self.fpga.get_bram_data(self.settings.spec_info)
            cal_crosspow = self.fpga.get_bram_data(self.settings.crosspow_info)

            # combine real and imaginary part of crosspow data
            crosspow_data = np.array(crosspow_data[0::2]) + 1j*np.array(crosspow_data[1::2])            

            # save cal rawdata
            np.savez(cal_datadir + '/'+str(deg)+'deg_chnl_' + str(chnl), 
                cal_pow=cal_pow, cal_crosspow=cal_crosspow)

            # compute ratios
            # get the reference power
            aa = pow_data[ref][chnl]
            for j, ab in enumerate(crosspow_cal):
                in_ratios[j].append(np.conj(ab[chnl]) / aa) # (ab*)* / aa* = a*b / aa* = b/a

            # plot spec data
            cal_pow_plot = self.scale_dbfs_spec_data(cal_pow, self.settings.spec_info)
            for i, spec_plot in enumerate(cal_pow_plot):
                fig.axes[i].plot(spec_plot)

            # plot the magnitude ratio and phase difference
            fig.axes[4].plotxy(self.cal_freqs[:i+1], [np.abs(in_ratios)])
            fig.axes[5].plotxy(self.cal_freqs[:i+1], [np.angle(in_ratios, deg=True)])

        # plot last frequency
        plt.pause(self.settings.pause_time) 

        # compute interpolations
        for i, ratio_arr in enumerate(in_ratios):
            in_ratios[i] = np.interp(range(self.nchannels), self.cal_channels, ratio_arr)

        return in_ratios

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
            a2_tone_usb, b2_tone_usb = self.fpga.get_bram_data(self.settings.synth_info)

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
            a2_tone_lsb, b2_tone_lsb = self.fpga.get_bram_data(self.settings.synth_info)

            # save syn rawdata
            np.savez(syn_datadir+'/chnl_'+str(chnl), a2_tone_usb=a2_tone_usb, b2_tone_usb=b2_tone_usb, 
                a2_tone_lsb=a2_tone_lsb, b2_tone_lsb=b2_tone_lsb)

            # plot spec data
            [a2_tone_lsb_plot, b2_tone_lsb_plot] = \
                self.scale_dbfs_spec_data([a2_tone_lsb, b2_tone_lsb], self.settings.synth_info)
            self.srrfigure.axes[0].plot(a2_tone_lsb_plot)
            self.srrfigure.axes[1].plot(b2_tone_lsb_plot)

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

            # plot SRR
            self.srrfigure.axes[2].plotxy(self.srr_freqs[:i+1], srr_usb)
            self.srrfigure.axes[3].plotxy(self.srr_freqs[:i+1], srr_lsb)
        
        # plot last frequency
        plt.pause(self.settings.pause_time)

        # save srr data
        np.savez(lo_datadir+"/srr", srr_usb=srr_usb, srr_lsb=srr_lsb)

    def print_srr_plot(self):
        """
        Print SRR plot using the data saved from the test.
        """
        fig = plt.figure()
        for lo_comb in self.lo_combinations:
            lo_label = '_'.join(['LO'+str(i+1)+'_'+str(lo/1e3)+'GHZ' for i,lo in enumerate(lo_comb)]) 
            datadir = self.datadir + '/' + lo_label

            srrdata = np.load(datadir + '/srr.npz')
            
            usb_freqs = lo_comb[0]/1.0e3 + sum(lo_comb[1:])/1.0e3 + self.srr_freqs
            lsb_freqs = lo_comb[0]/1.0e3 - sum(lo_comb[1:])/1.0e3 - self.srr_freqs
            
            plt.plot(usb_freqs, srrdata['srr_usb'], '-r')
            plt.plot(lsb_freqs, srrdata['srr_lsb'], '-b')
            plt.grid()
            plt.xlabel('Frequency [GHz]')
            plt.ylabel('SRR [dB]')

        plt.savefig(self.datadir + '/srr.pdf', bbox_inches='tight')
