import time, itertools
import numpy as np
import matplotlib.pyplot as plt
from experiment import Experiment
from plotter import Plotter
from axes.spectrum_axis import SpectrumAxis
from axes.mag_ratio_axis import MagRatioAxis
from axes.angle_diff_axis import AngleDiffAxis
from axes.srr_axis import SrrAxis
from equipment.generator import Generator

class DssCalibrator(Experiment):
    """
    This class is used to calibrate a Sideband Separating receiver.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.nchannels = self.get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(0, self.settings.bw, self.nchannels, endpoint=False)
        
        # const dtype info
        self.const_nbits = self.settings.const_brams_info['data_width']/2 # bitwidth of real part (=imag part)
        self.const_bin_pt = self.settings.const_bin_pt

        # sources (RF and LOs)
        self.rf_source = Generator(self.settings.rf_source)
        self.lo_sources = [Generator(lo_source) for lo_source in self.settings.lo_sources]
        
    def run_dss_test(self):
        """
        Perform a full DSS test, with constants and SRR computation. 
        """
        # set power and turn on sources
        self.rf_source.set_power_dbm()
        self.rf_source.turn_output_on()
        for lo_source in self.lo_sources():
            self.lo_source.set_power_dbm()
            self.lo_source.turn_output_on()

        lo_combinations = self.get_lo_combination()
        for lo_comb in lo_combinations:
            print ', '.join(['LO'+str(i+1)+': '+str(lo)+'MHz' for i,lo in enumerate(lo_comb)])

            for i, lo in enumerate(lo_comb):
                self.lo_sources[i].set_freq_mhz(lo)
                time.sleep(1)
                
                # Hot-Cold Measurement
                if.self.settings.kerr_correction:
                    M_DSB = self.make_hotcold_measurement()
                else:
                    M_DSB = np.ones(self.nchannels)
                
                # compute calibration constants (sideband ratios)
                if not self.settings.ideal_consts['load']:
                    sb_ratios_usb = self.compute_sb_ratios(center_freq=sum(lo_comb), tone_in_usb=True)
                    sb_ratios_lsb = self.compute_sb_ratios(center_freq=sum(lo_comb), tone_in_usb=False)
                else:
                    const = self.settings.ideal_consts['val']
                    sb_ratios_usb = const * np.zeros(self.nchannels, dtype=np.complex128)
                    sb_ratios_lsb = const * np.zeros(self.nchannels, dtype=np.complex128)

                # load constants
                [sb_ratio_usb, sb_ratio_lsb] = self.float2fixed_comp(self.consts_nbits, 
                    self.consts_bin_pt, [sb_ratio_usb, sb_ratio_lsb])
                print "Loading constants to FPGA brams..."
                self.write_bram_list2d_data(self.settings.const_brams_info, [sb_ratios_usb, sb_ratios_lsb])
                print "done"

                # compute SRR
                self.compute_ssr(M_DSB, center_freq=sum(lo_comb))
    
    def get_lo_combination(self):
        """
        Creates a list of tuples with all the possible LO combinations from
        the lo_sources parameter of the config file. Used to perform a
        nested loop that set all LO combinations in generators.
        """
        lo_freqs_arr = [lo_source['lo_freqs'] for lo_source in self.settings.lo_sources]
        return list(itertools.product(*lo_freqs_arr))

    def make_hotclod_test(self):
        """
        Perform a hotcold test (Kerr calibration) to the determine the M_DSB parameter to
        correctly compute the Sideband Rejection Ratio (SRR) in Sideband separating receivers.
        More information in ALMA's Memo 357 (http://legacy.nrao.edu/alma/memos/html-memos/abstracts/abs357.html)
        """
        # make the receiver cold
        self.chopper.move_90cw()
        a2_cold, b2_cold = self.fpga.get_bram_list_interleaved_data(self.settings.cal_pow_info)
        # make the receiver hot
        self.chopper.move_90ccw()
        a2_hot, b2_hot = self.fpga.get_bram_list_interleaved_data(self.settings.cal_pow_info)

        # TODO check correct formula for a and b
        M_DSB = (a_hot - a_cold) / (b_hot - b_cold)
        
        return M_DSB

    def compute_sb_ratios(self, center_freq=0, tone_in_usb=True):
        """
        Sweep a tone through the receiver bandwidth and computes the
        sideband ratio for a number of FFT channel. The total number of 
        channels used for the computations depends in the config file parameter 
        cal_chnl_step. The channels not measured are interpolated.
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
        self.calplotter.create_window()
        
        print "Computing sideband ratios, tone in " + ("USB" if tone_in_usb else "LSB") + "..."
        for chnl in channels:
            freq = self.freqs[chnl]
            # set generator frequency
            if tone_in_usb:
                self.rf_source.set_freq_mhz(center_freq + freq)
            else: # tone in lsb
                self.rf_source.set_freq_mhz(center_freq - freq)    
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
        print "done computing sideband ratios, tone in " + ("USB" if tone_in_usb else "LSB") + "."

        # compute interpolations
        sb_ratios = np.interp(range(self.nchannels), channels, sb_ratios)
            
        return sb_ratios

    def float2fixed_comp(self, nbits, bin_pt, data):
        """
        Convert a numpy array with complex values into CASPER complex 
        format ([realpart:imagpart]). The real and imaginary part have
        the same bitwidth given by nbits. bin_pt indicates the binary
        point position for both the real and imaginary part. The 
        resulting array should have an integer numpy datatype, of 
        bitwidth 2*nbits, and it should be in big endian format: >Xi.
        :param nbits: bitwidth of real part (=imag part).
        :param bin_pt: binary point of real part (= imag part).
        :param data: data array to convert.
        :return: converted data array.
        """
        data_real = np.real(data)
        data_imag = np.imag(data)

        self.check_overflow(nbits, bit_pt,  data_real)
        self.check_overflow(nbits, bit_pt,  data_imag)
        
        data_real = (2**bin_pt * data_real).astype('>i'+str(nbits/8))
        data_imag = (2**bin_pt * data_imag).astype('>i'+str(nbits/8))

        # combine real and imag data
        data_real = 2**nbits * (data_real.astype('>i'+str(2*bits/8)))
        data_comp = data_real + data_imag

        return data_comp

    def run_srr_computation(self, M_DSB, center_freq):
        """
        Compute SRR from the DSS receiver using the Kerr method
        (see ALMA Memo 357 (http://legacy.nrao.edu/alma/memos/html-memos/abstracts/abs357.html)).
        The channel total number of channels used for the SRR computations
        can be controlled by the config file parameter synth_channel_step.
        :param M_DSB: constant computed in the hotcold test used for the Kerr method.
        :param center_freq: analog center frequency of the downconverted 
            signal. Used to properly set the RF input.
        """
        channels = range(self.nchannels)[1::self.settings.synth_chnl_step]
        partial_freqs = [] # for plotting
        srr_usb = []
        srr_lsb = []

        self.srrplotter = DssSrrPlotter(self.fpga)
        self.srrplotter.create_window()
        
        print "Computing SRR..."
        for chnl in channels:
            freq = self.freqs[chnl]
            # set generator at USB frequency
            self.rf_source.set_freq_mhz(center_freq + freq)
            plt.pause(1) 
            # get USB and LSB power data
            a2_tone_usb, b2_tone_usb = self.fpga.get_bram_list_interleaved_data(self.settings.spec_info)

            # plot data specta
            for spec_data, axis in zip([a2_tone_USB, b2_tone_LSB], self.calplotter.axes[:2]):
                spec_data = spec_data / float(self.fpga.read_reg('synth_acc_len')) # divide by accumulation
                spec_data = self.linear_to_dBFS(spec_data)
                axis.plot(spec_data)

            # set generator at LSB frequency
            self.rf_source.set_freq_mhz(center_freq - freq)
            plt.pause(1) 
            # get USB and LSB power data
            cal_a2_tone_lsb, cal_b2_tone_lsb = self.fpga.get_bram_list_interleaved_data(self.settings.spec_info)

            # plot data specta
            for spec_data, axis in zip([a2_tone_USB, b2_tone_LSB], self.srrplotter.axes[:2]):
                spec_data = spec_data / float(self.fpga.read_reg('synth_acc_len')) # divide by accumulation
                spec_data = self.linear_to_dBFS(spec_data)
                axis.plot(spec_data)
            plt.pause(1) 

            # Compute SRRs
            ratio_usb = a2_tone_usb[chnl] / b2_tone_usb[chnl]
            ratio_lsb = b2_tone_lsb[chnl] / a2_tone_lsb[chnl]
            
            # TODO check formulas
            new_srr_usb = ratio_usb * (ratio_lsb*M_DSB[chnl] - 1) / (ratio_usb - M_DSB[chnl])
            srr_usb.append(10*np.log10(new_srr_usb))
            new_srr_lsb = ratio_lsb * (ratio_usb - M_DSB[chnl]) / (ratio_lsb*M_DSB[chnl] - 1)
            srr_lsb.append(10*np.log10(new_srr_lsb))

            partial_freqs.append(freq)
            # plot magnitude ratio
            self.srrplotter.axes[2].plot(partial_freqs, srr_usb)
            # plot angle difference
            self.srrplotter.axes[3].plot(partial_freqs, srr_lsb)

        # plot last frequency
        plt.pause(1) 
        print "done computing SRR."

    def check_overflow(self, nbits, bin_pt, data):
        """
        Given a signed fixed point representation of bitwidth nbits and 
        binary point bin_pt, check if the data array contians values that
        will produce overflow if it would be cast. If overflow is detected,
        a warning signal is printed.
        :param nbits: bitwidth of the signed fixed point representation.
        :param bin_pt: binary point of the signed fixed point representation.
        :param data: data array to check.
        """
        max_val = (2.0**(nbits-1)-1) / (2**bin_pt)
        min_val = (-2.0**(nbits-1))  / (2**bin_pt)

        max_data = np.max(data)
        min_data = np.min(data)

        if max_data > max_val:
            print "WARNING! Maximum value surpassed in overflow check."
            print "Max allowed value: " + str(max_val)
            print "Max data value: " + str(max_data)

        if min_data < min_val:
            print "WARNING! Minimum value surpassed in overflow check."
            print "Min allowed value: " + str(min_val)
            print "Min data value: " + str(min_data)

class DssCalibrationPlotter(Plotter):
    """
    Inner class for calibration plots.
    """
    def __init__(self, calanfpga):
        self.create_gui = False
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
        self.create_gui = False
        Plotter.__init__(self, calanfpga)
        self.nplots = 4
        mpl_axes = self.create_axes()
        self.nchannels = self.get_nchannels(self.settings.spec_info)

        # add custom axes
        self.axes.append(SpectrumAxis(mpl_axes[0], self.nchannels,
                self.settings.bw, 'USB spec'))
        self.axes.append(SpectrumAxis(mpl_axes[1], self.nchannels,
                self.settings.bw, 'LSB spec'))
        self.axes.append(SrrAxis(mpl_axes[2], self.nchannels,
                self.settings.bw, 'SRR USB'))
        self.axes.append(SrrAxis(mpl_axes[3], self.nchannels,
                self.settings.bw, 'SRR LSB'))
