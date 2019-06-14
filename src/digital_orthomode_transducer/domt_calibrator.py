# -*- coding: utf-8 -*-
import os, time, datetime, itertools, json, tarfile, shutil
import numpy as np
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels, init_sources, turn_off_sources
from ..calanfigure import CalanFigure
from ..instruments.generator import Generator, create_generator
from ..axes.spectrum_axis import SpectrumAxis
from ..pocket_correlator.mag_ratio_axis import MagRatioAxis
from ..pocket_correlator.angle_diff_axis import AngleDiffAxis
from ..digital_sideband_separation.dss_calibrator import get_lo_combinations, float2fixed, check_overflow
from pol_axis import PolAxis

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
        self.polfigure       = CalanFigure(n_plots=4, create_gui=False)
        
        # axes on figures
        self.calfigure_0deg.create_axis(0, SpectrumAxis,  self.freqs, 'ZDOK0 a spec')
        self.calfigure_0deg.create_axis(1, SpectrumAxis,  self.freqs, 'ZDOK0 c spec')
        self.calfigure_0deg.create_axis(2, SpectrumAxis,  self.freqs, 'ZDOK1 a spec')
        self.calfigure_0deg.create_axis(3, SpectrumAxis,  self.freqs, 'ZDOK1 c spec')
        self.calfigure_0deg.create_axis(4, MagRatioAxis,  self.freqs, ['1/1', '2/1', '3/1', '4/1'], 'Magnitude Ratio')
        self.calfigure_0deg.create_axis(5, AngleDiffAxis, self.freqs, ['1-1', '2-1', '3-1', '4-1'], 'Angle Difference')
        #
        self.calfigure_45deg.create_axis(0, SpectrumAxis,  self.freqs, 'ZDOK0 a spec')
        self.calfigure_45deg.create_axis(1, SpectrumAxis,  self.freqs, 'ZDOK0 c spec')
        self.calfigure_45deg.create_axis(2, SpectrumAxis,  self.freqs, 'ZDOK1 a spec')
        self.calfigure_45deg.create_axis(3, SpectrumAxis,  self.freqs, 'ZDOK1 c spec')
        self.calfigure_45deg.create_axis(4, MagRatioAxis,  self.freqs, ['1/1', '2/1', '3/1', '4/1'], 'Magnitude Ratio')
        self.calfigure_45deg.create_axis(5, AngleDiffAxis, self.freqs, ['1-1', '2-1', '3-1', '4-1'], 'Angle Difference')
        #
        self.calfigure_90deg.create_axis(0, SpectrumAxis,  self.freqs, 'ZDOK0 a spec')
        self.calfigure_90deg.create_axis(1, SpectrumAxis,  self.freqs, 'ZDOK0 c spec')
        self.calfigure_90deg.create_axis(2, SpectrumAxis,  self.freqs, 'ZDOK1 a spec')
        self.calfigure_90deg.create_axis(3, SpectrumAxis,  self.freqs, 'ZDOK1 c spec')
        self.calfigure_90deg.create_axis(4, MagRatioAxis,  self.freqs, ['1/2', '2/2', '3/2', '4/2'], 'Magnitude Ratio')
        self.calfigure_90deg.create_axis(5, AngleDiffAxis, self.freqs, ['1-2', '2-2', '3-2', '4-2'], 'Angle Difference')
        #
        self.polfigure.create_axis(0, SpectrumAxis, self.freqs, 'X pol')
        self.polfigure.create_axis(1, SpectrumAxis, self.freqs, 'Y pol')
        self.polfigure.create_axis(2, PolAxis, self.freqs, 'X pol isolation')
        self.polfigure.create_axis(3, PolAxis, self.freqs, 'Y pol isolation')

        # data save attributes
        self.dataname = self.settings.boffile[:self.settings.boffile.index('.')]
        self.dataname = 'domttest ' + self.dataname + ' '
        self.datadir = self.dataname + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        os.mkdir(self.datadir)
        self.testinfo = {'bw'               : self.settings.bw,
                         'nchannels'        : self.nchannels,
                         'cal_acc_len'      : self.fpga.read_reg(self.settings.spec_info['acc_len_reg']),
                         'syn_acc_len'      : self.fpga.read_reg(self.settings.synth_info['acc_len_reg']),
                         'use_ideal_consts' : self.settings.ideal_consts,
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
                if not self.settings.ideal_consts:
                    raw_input('Please angle the OMT cavity to 0° and press enter...')
                    print "\tComputing input ratios, angle 0°..."; step_time = time.time()
                    self.calfigure_0deg.set_window_title('Calibration 0° ' + lo_label)
                    in_ratios_0deg  = self.compute_input_ratios(lo_comb, lo_datadir, 0, self.calfigure_0deg)
                    print "\tdone (" + str(time.time() - step_time) + "[s])" 

                    raw_input('Please angle the OMT cavity to 90° and press enter...')
                    print "\tComputing input ratios, angle 90°..."; step_time = time.time()
                    self.calfigure_90deg.set_window_title('Calibration 90° ' + lo_label)
                    in_ratios_90deg  = self.compute_input_ratios(lo_comb, lo_datadir, 1, self.calfigure_90deg)
                    print "\tdone (" + str(time.time() - step_time) + "[s])" 

                    #print "\tComputing input ratios, angle 45°..."; step_time = time.time()
                    #self.calfigure_45deg.set_window_title('Calibration 45° ' + lo_label)
                    #in_ratios_45deg  = self.compute_input_ratios(lo_comb, lo_datadir, 0, self.calfigure_45deg)
                    #print "\tdone (" + str(time.time() - step_time) + "[s])" 
                    
                    # save in ratios
                    np.savez(lo_datadir+'/in_ratios', in_ratios_0deg=in_ratios_0deg, 
                        in_ratios_90deg=in_ratios_90deg)

                    # constant computation
                    H = compute_cal_consts(in_ratios_0deg, in_ratios_90deg)

                else: # use ideal constants
                    #H = self.nchannels * [np.array([[0.5, 0, -0.5, 0],[0, 0.5, 0, -0.5]])]
                    n = self.nchannels
                    H = [[0.5*np.ones(n), np.zeros(n), -0.5*np.ones(n),     np.zeros(n)],
                         [np.zeros(n), 0.5*np.ones(n),     np.zeros(n), -0.5*np.ones(n)]]

                # test H dimensions
                print "H dims: " + str(len(H)) + ", " + str(len(H[0])) + ", " + str(len(H[0][0]))

                # load constants
                #print "\tLoading constants..."; step_time = time.time()
                H_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(H))
                H_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(H))
                self.fpga.write_bram_data(self.settings.const_brams_info, [H_real, H_imag])
                print "\tdone (" + str(time.time() - step_time) + "[s])"

                # compute pol isolation
                raw_input('Please angle the OMT cavity to 0° and press enter...')
                print "\tComputing pol-x iso..."; step_time = time.time()
                self.isofigure.fig.canvas.set_window_title('Pol Iso Computation ' + lo_label)
                self.compute_pol_iso(lo_comb, lo_datadir, 'x', self.isofigure.axes[2])
                print "\tdone (" + str(time.time() - step_time) + "[s])"
                raw_input('Please angle the OMT cavity to 90° and press enter...')
                print "\tComputing pol-y iso..."; step_time = time.time()
                self.compute_pol_iso(lo_comb, lo_datadir, 'y', self.isofigure.axes[3])
                print "\tdone (" + str(time.time() - step_time) + "[s])"

        # turn off sources
        turn_off_sources(self.sources)

        # print iso (full) plot
        #self.print_iso_plot()

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
        in_ratios = [[] for i in range(4)]
        rf_freqs = lo_comb[0] + sum(lo_comb[1:]) + self.freqs

        cal_datadir = lo_datadir + '/cal_rawdata'
        # creates directory for the raw calibration data if doesn't exists
        try:
            os.mkdir(cal_datadir)
        except OSError:
            pass

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
            cal_crosspow = np.array(cal_crosspow[0::2]) + 1j*np.array(cal_crosspow[1::2])            

            # save cal rawdata
            np.savez(cal_datadir + '/'+'ref_'+str(ref)+'_chnl_' + str(chnl), 
                cal_pow=cal_pow, cal_crosspow=cal_crosspow)

            # compute ratios
            # get the reference power
            aa = cal_pow[ref][chnl]
            for j, ab in enumerate(cal_crosspow):
                in_ratios[j].append(np.conj(ab[chnl]) / aa) # (ab*)* / aa* = a*b / aa* = b/a

            # plot spec data
            cal_pow_plot = self.scale_dbfs_spec_data(cal_pow, self.settings.spec_info)
            for j, spec_plot in enumerate(cal_pow_plot):
                fig.axes[j].plot(spec_plot)

            # plot the magnitude ratio and phase difference
            fig.axes[4].plotxy(self.cal_freqs[:i+1], np.abs(in_ratios))
            fig.axes[5].plotxy(self.cal_freqs[:i+1], np.angle(in_ratios, deg=True))

        # plot last frequency
        plt.pause(self.settings.pause_time) 

        # compute interpolations
        for i, ratio_arr in enumerate(in_ratios):
            in_ratios[i] = np.interp(range(self.nchannels), self.cal_channels, ratio_arr)

        return in_ratios

    def compute_pol_iso(self, lo_comb, lo_datadir, pol, ax):
        """
        Compute the polarization isolation from the DOMT receiver.
        The total number of channels used for the isolation computations
        can be controlled by the config file parameter syn_chnl_step.
        :param lo_comb: LO frequency combination for the test. Used to properly set
            the RF test input.
        :param lo_datadir: diretory for the data of the current LO frequency combination.
        :param pol: polarization being measured (i.e. omt input angle).
        :param ax: axis to plot polarization isolation.
        """
        iso = []
        rf_freqs = lo_comb[0] + sum(lo_comb[1:]) + self.freqs

        syn_datadir = lo_datadir + '/pol_rawdata'
        try:
            os.mkdir(syn_datadir)
        except OSError:
            pass
 
        for i, chnl in enumerate(self.syn_channels):
            # set generator
            self.rf_source.set_freq_mhz(rf_freqs_usb[chnl])
            # plot while the generator is changing to frequency to give the system time to update
            plt.pause(self.settings.pause_time) 
            
            # get polarization power data
            polx, poly = self.fpga.get_bram_data(self.settings.synth_info)

            # plot spec data
            [polx_plot, poly_plot] = \
                self.scale_dbfs_spec_data([polx, poly], self.settings.synth_info)
            self.synfigure.axes[0].plot(polx_plot)
            self.synfigure.axes[1].plot(poly_plot)

            # save syn rawdata
            np.savez(syn_datadir+'/pol'+str(pol)+'_chnl_'+str(chnl), polx=polx, poly=poly)

            # Compute polarization isolation
            if pol == 'x':
                iso.append(np.divide(poly[chnl], polx[chnl], dtype=np.float64))
            else: # pol=='y'
                iso.append(np.divide(polx[chnl], poly[chnl], dtype=np.float64))

            # plot polarization isolation
            ax.plotxy(self.syn_freqs[:i+1], iso)
        
        # plot last frequency
        plt.pause(self.settings.pause_time)

        # save srr data
        np.save(lo_datadir+"/pol_"+str(pol)+"_iso", iso)

    def print_iso_plot(self):
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

def compute_cal_consts(gx, gy):
    """
    Compute the calibration constants as the pseudo inverse of the
    gain matrix of an OMT. As the gain matrix is frequency dependant
    an array of gains element is expected for each frequency component.
    More info about the pseudo-inverse:
    https://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.pinv.html
    :param gx: x components of the gain matrix
    :param gy: y components of the gain matrix
    :return: list of calibration matrices H
    """
    # combine gx and gy to form an array of matrices
    G = np.transpose(np.dstack((gx,gy)), (1,0,2))

    # compute pseudo inverse
    H = np.linalg.pinv(G)

    return H
