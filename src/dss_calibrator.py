import time, datetime, json, itertools
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from experiment import Experiment
from plotter import Plotter
from experiment import linear_to_dBFS, get_nchannels
from axes.spectrum_axis import SpectrumAxis
from axes.mag_ratio_axis import MagRatioAxis
from axes.angle_diff_axis import AngleDiffAxis
from axes.srr_axis import SrrAxis
from instruments.generator import Generator

class DssCalibrator(Experiment):
    """
    This class is used to calibrate a Sideband Separating receiver.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.nchannels = get_nchannels(self.settings.synth_info)
        self.freqs = np.linspace(0, self.settings.bw, self.nchannels, endpoint=False)
        
        # const dtype info
        self.consts_nbits = self.settings.const_brams_info['data_width']
        self.consts_bin_pt = self.settings.const_bin_pt

        # sources (RF and LOs)
        self.rf_source = self.create_instrument(self.settings.rf_source)
        self.lo_sources = [self.create_instrument(lo_source) for lo_source in self.settings.lo_sources]
        
        # data save attributes
        self.datafile = self.settings.datafile + '_' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '_'
        self.dss_data = {'freq_if' : self.freqs.tolist()}

    def synchronize_adcs(self):
        """
        Compute the delay difference between ADC (expected to be 
        an integer of the smaple time), and apply that delay to the
        ADC running ahead in order to sychronize both ADCs. This is 
        frequency based synchronization methods, that is an alternative
        to the stand-alone time-based adc_synchornator method, with the
        benefit that is less cumbersome when using DSS backends, and more
        precise.
        """
        test_channels = range(1, 101, 10)

        self.calplotter = DssCalibrationPlotter(self.fpga)
        self.calplotter.axes[2].ax.set_xlim((self.freqs[test_channels[0]], self.freqs[test_channels[-1]]))
        self.calplotter.axes[3].ax.set_xlim((self.freqs[test_channels[0]], self.freqs[test_channels[-1]]))
        self.calplotter.create_window()
        
        # set power and turn on sources
        self.rf_source.set_power_dbm()
        self.rf_source.turn_output_on()
        for lo_source in self.lo_sources:
            lo_source.set_power_dbm()
            lo_source.turn_output_on()
        
        # set LO freqs as fisrt freq combination
        lo_comb = self.get_lo_combinations()[0]
        for lo_source, freq in zip(self.lo_sources, lo_comb):
            lo_source.set_freq_mhz(freq)
        center_freq = sum(lo_comb)

        print "Synchronizing ADCs..."
        while True:
            sb_ratios = []
            partial_freqs = [] # for plotting
            for chnl in test_channels:
                freq = self.freqs[chnl]
                # set generator frequency
                self.rf_source.set_freq_mhz(center_freq + freq)
                plt.pause(1) 

                # get power-crosspower data
                cal_a2, cal_b2 = self.fpga.get_bram_list_interleaved_data(self.settings.cal_pow_info)
                cal_ab_re, cal_ab_im = self.fpga.get_bram_list_interleaved_data(self.settings.cal_crosspow_info)

                # compute constant
                ab = cal_ab_re[chnl] + 1j*cal_ab_im[chnl]
                sb_ratios.append(np.conj(ab) / cal_a2[chnl]) # (ab*)* / aa* = a*b / aa* = b/a = LSB/USB

                # plot spec data
                for spec_data, axis in zip([cal_a2, cal_b2], self.calplotter.axes[:2]):
                    spec_data = spec_data / float(self.fpga.read_reg(self.settings.cal_pow_info['acc_len_reg'])) # divide by accumulation
                    spec_data = linear_to_dBFS(spec_data, self.settings.cal_pow_info)
                    axis.plot(spec_data)
            
                partial_freqs.append(freq)
                # plot magnitude ratio
                self.calplotter.axes[2].plot(partial_freqs, np.abs(sb_ratios))
                # plot angle difference
                self.calplotter.axes[3].plot(partial_freqs, np.angle(sb_ratios, deg=True))

            # plot last frequency
            plt.pause(1) 

            # compute delay difference
            angles = np.angle(sb_ratios)
            linregress_results = scipy.stats.linregress(partial_freqs, angles)
            angle_slope = linregress_results.slope
            delay = int(round(angle_slope * 2*self.settings.bw / (2*np.pi))) # delay = dphi/df * Fs / 2pi
            print "Computed delay: " + str(delay)
            print "Error standard deviation: " + str(linregress_results.stderr)

            # check adc sync status, apply delay if needed
            if delay == 0:
                print "ADCs successfully synthronized"
                plt.close(self.calplotter.fig)
                return
            elif delay > 0: # if delay is positive adc1 is ahead, hence delay adc1
                self.fpga.set_reg('adc1_delay', delay)
            else: # (delay < 0) if delay is negative adc0 is ahead, hence delay adc0
                self.fpga.set_reg('adc0_delay', -1*delay)

    def run_dss_test(self):
        """
        Perform a full DSS test, with constants and SRR computation. 
        """
        # set power and turn on sources
        self.rf_source.set_power_dbm()
        self.rf_source.turn_output_on()
        for lo_source in self.lo_sources:
            lo_source.set_power_dbm()
            lo_source.turn_output_on()

        lo_combinations = self.get_lo_combinations()
        initial_time = time.time()
        for lo_comb in lo_combinations:
            cycle_time = time.time()
            lo_label = '_'.join(['lo'+str(i+1)+'_'+str(lo/1e3)+'ghz' for i,lo in enumerate(lo_comb)]) 
            print lo_label.upper().replace("_", " ")

            for i, lo in enumerate(lo_comb):
                self.lo_sources[i].set_freq_mhz(lo)
                time.sleep(1)
                
                # Hot-Cold Measurement
                if self.settings.kerr_correction:
                    print "\tMake hotcold test..."; step_time = time.time()
                    M_DSB = self.make_hotcold_measurement()
                    print "\tdone (" + str(time.time() - step_time) + "[s])"
                else:
                    M_DSB = None
                
                # compute calibration constants (sideband ratios)
                if not self.settings.ideal_consts['load']:
                    print "\tComputing sideband ratios, tone in USB..."; step_time = time.time()
                    center_freq = lo_comb[0] + sum(lo_comb[1:])
                    sb_ratios_usb = self.compute_sb_ratios(center_freq, tone_in_usb=True)
                    consts_lsb = -1.0*sb_ratios_usb
                    print "\tdone (" + str(time.time() - step_time) + "[s])" 
                    print "\tComputing sideband ratios, tone in LSB..."; step_time = time.time()
                    center_freq = lo_comb[0] - sum(lo_comb[1:])
                    sb_ratios_lsb = self.compute_sb_ratios(center_freq, tone_in_usb=False)
                    consts_usb = -1.0*sb_ratios_lsb
                    print "\tdone (" + str(time.time() - step_time) + "[s])"
                else:
                    const = self.settings.ideal_consts['val']
                    consts_usb = const * np.ones(self.nchannels, dtype=np.complex128)
                    consts_lsb = const * np.ones(self.nchannels, dtype=np.complex128)

                # load constants
                print "\tLoading constants..."; step_time = time.time()
                consts_usb_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts_usb))
                consts_usb_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts_usb))
                consts_lsb_real = float2fixed(self.consts_nbits, self.consts_bin_pt, np.real(consts_lsb))
                consts_lsb_imag = float2fixed(self.consts_nbits, self.consts_bin_pt, np.imag(consts_lsb))
                self.fpga.write_bram_list_interleaved_data(self.settings.const_brams_info, 
                    [consts_usb_real, consts_usb_imag, consts_lsb_real, consts_lsb_imag])
                print "\tdone (" + str(time.time() - step_time) + "[s])"

                # compute SRR
                print "\tComputing SRR..."; step_time = time.time()
                center_freq_usb = lo_comb[0] + sum(lo_comb[1:])
                center_freq_lsb = lo_comb[0] - sum(lo_comb[1:])
                self.compute_srr(M_DSB, center_freq_usb, center_freq_lsb)
                print "\tdone (" + str(time.time() - step_time) + "[s])"

                # save data to file
                #datafile = self.datafile + lo_label
                #with open(datafile+'.json', 'w') as jsonfile:
                #    json.dump(self.dss_data, jsonfile,  indent=4)
                #print "\tData saved"
                #print "\tCycle time: " + str(time.time() - cycle_time) + "[s]"

        # turn off sources
        self.rf_source.turn_output_off()
        for lo_source in self.lo_sources:
            lo_source.turn_output_off()

        print "Total time: " + str(time.time() - initial_time) + "[s]"

    def get_lo_combinations(self):
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

        # Compute Kerr's parameter.
        M_DSB = np.divide(a2_hot - a2_cold, b2_hot - b2_cold, dtype=np.float64)

        # save hotcold data
        hotcold_data = {'a2_cold' : a2_cold.tolist(), 'b2_cold' : b2_cold.tolist(),
                        'a2_hot'  : a2_hot.tolist(),  'b2_hot'  : b2_hot.tolist(), 
                        'M_DSB'   : MDSB.tolist()}
        self.dss_data['hotcold'] = hotcold_data
        
        return M_DSB

    def compute_sb_ratios(self, center_freq, tone_in_usb):
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
        cal_data = {}

        self.calplotter = DssCalibrationPlotter(self.fpga)
        self.calplotter.create_window()
        
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

            # save spec data
            cal_data['a2_ch_'+str(chnl)] = cal_a2.tolist()
            cal_data['b2_ch_'+str(chnl)] = cal_b2.tolist()

            # compute constant
            ab = cal_ab_re[chnl] + 1j*cal_ab_im[chnl]
            if tone_in_usb:
                sb_ratios.append(np.conj(ab) / cal_a2[chnl]) # (ab*)* / aa* = a*b / aa* = b/a = LSB/USB
            else: # tone in lsb
                sb_ratios.append(ab / cal_b2[chnl]) # ab* / bb* = a/b = USB/LSB.

            # plot spec data
            for spec_data, axis in zip([cal_a2, cal_b2], self.calplotter.axes[:2]):
                spec_data = spec_data / float(self.fpga.read_reg(self.settings.cal_pow_info['acc_len_reg'])) # divide by accumulation
                spec_data = linear_to_dBFS(spec_data, self.settings.cal_pow_info)
                axis.plot(spec_data)
            
            partial_freqs.append(freq)
            # plot magnitude ratio
            self.calplotter.axes[2].plot(partial_freqs, np.abs(sb_ratios))
            # plot angle difference
            self.calplotter.axes[3].plot(partial_freqs, np.angle(sb_ratios, deg=True))

        # plot last frequency
        plt.pause(1) 

        # compute interpolations
        sb_ratios = np.interp(range(self.nchannels), channels, sb_ratios)

        # save calibration data
        cal_data['sbratios'] = sb_ratios.tolist()
        if tone_in_usb:
            cal_data['rf_freq'] = (center_freq + self.freqs).tolist()
            self.dss_data['cal_tone_usb'] = cal_data
        else: # tone_in_lsb
            cal_data['rf_freq'] = (center_freq - self.freqs).tolist()
            self.dss_data['cal_tone_lsb'] = cal_data
            
        return sb_ratios

    def compute_srr(self, M_DSB, center_freq_usb, center_freq_lsb):
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
        synth_data = {}

        self.srrplotter = DssSrrPlotter(self.fpga)
        self.srrplotter.create_window()
        
        for chnl in channels:
            freq = self.freqs[chnl]
            # set generator at USB frequency
            self.rf_source.set_freq_mhz(center_freq_usb + freq)
            plt.pause(1) 
            
            # get USB and LSB power data
            a2_tone_usb, b2_tone_usb = self.fpga.get_bram_list_interleaved_data(self.settings.synth_info)

            # save spec data
            synth_data['a2_ch_'+str(chnl)+'_tone_usb'] = a2_tone_usb.tolist()
            synth_data['b2_ch_'+str(chnl)+'_tone_usb'] = b2_tone_usb.tolist()

            # plot spec data
            for spec_data, axis in zip([a2_tone_usb, b2_tone_usb], self.srrplotter.axes[:2]):
                spec_data = spec_data / float(self.fpga.read_reg(self.settings.synth_info['acc_len_reg'])) # divide by accumulation
                spec_data = linear_to_dBFS(spec_data, self.settings.synth_info)
                axis.plot(spec_data)

            # set generator at LSB frequency
            self.rf_source.set_freq_mhz(center_freq_lsb - freq)
            plt.pause(1) 
            
            # get USB and LSB power data
            a2_tone_lsb, b2_tone_lsb = self.fpga.get_bram_list_interleaved_data(self.settings.synth_info)

            # save spec data
            synth_data['a2_ch'+str(chnl)+'_tone_lsb'] = a2_tone_lsb.tolist()
            synth_data['b2_ch'+str(chnl)+'_tone_lsb'] = b2_tone_lsb.tolist()

            # plot spec data
            for spec_data, axis in zip([a2_tone_lsb, b2_tone_lsb], self.srrplotter.axes[:2]):
                spec_data = spec_data / float(self.fpga.read_reg(self.settings.synth_info['acc_len_reg'])) # divide by accumulation
                spec_data = linear_to_dBFS(spec_data, self.settings.synth_info)
                axis.plot(spec_data)
            #plt.pause(1) 

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

            partial_freqs.append(freq)
            # plot magnitude ratio
            self.srrplotter.axes[2].plot(partial_freqs, srr_usb)
            # plot angle difference
            self.srrplotter.axes[3].plot(partial_freqs, srr_lsb)
        
        # plot last frequency
        plt.pause(1)

        # save srr data
        synth_data['srr_usb'] = srr_usb
        synth_data['srr_lsb'] = srr_lsb
        self.dss_data['synth'] = synth_data

class DssCalibrationPlotter(Plotter):
    """
    Inner class for calibration plots.
    """
    def __init__(self, calanfpga):
        self.create_gui = False
        Plotter.__init__(self, calanfpga)
        self.nplots = 4
        mpl_axes = self.create_axes()
        self.nchannels = get_nchannels(self.settings.cal_pow_info)
        
        # add custom axes
        self.axes.append(SpectrumAxis(mpl_axes[0], self.nchannels,
                self.settings.bw, 'ZDOK0 spec'))
        self.axes.append(SpectrumAxis(mpl_axes[1], self.nchannels,
                self.settings.bw, 'ZDOK1 spec'))
        self.axes.append(MagRatioAxis(mpl_axes[2], self.nchannels,
                self.settings.bw, 'Magnitude ratio'))
        self.axes.append(AngleDiffAxis(mpl_axes[3], self.nchannels,
                self.settings.bw, 'Angle difference'))
       
class DssSrrPlotter(Plotter):
    """
    Inner class for post-calibration plots.
    """
    def __init__(self, calanfpga):
        self.create_gui = False
        Plotter.__init__(self, calanfpga)
        self.nplots = 4
        mpl_axes = self.create_axes()
        self.nchannels = get_nchannels(self.settings.synth_info)

        # add custom axes
        self.axes.append(SpectrumAxis(mpl_axes[0], self.nchannels,
                self.settings.bw, 'USB spec'))
        self.axes.append(SpectrumAxis(mpl_axes[1], self.nchannels,
                self.settings.bw, 'LSB spec'))
        self.axes.append(SrrAxis(mpl_axes[2], self.nchannels,
                self.settings.bw, 'SRR USB'))
        self.axes.append(SrrAxis(mpl_axes[3], self.nchannels,
                self.settings.bw, 'SRR LSB'))

def float2fixed(nbits, bin_pt, data):
    """
    Convert a numpy array with float point numbers into big-endian 
    (ROACH compatible) fixed point numbers. An overflow check is done 
    and a warning is printed if the float number can't be represented
    with the fixed point parameters (round is allowed).
    :param nbits: bitwidth of the fixed point representation.
    :param bin_pt: binary point of the fixed point representation.
    :param data: data array to convert.
    :return: converted data array.
    """
    check_overflow(nbits, bin_pt, data)
    fixedpoint_data = (2**bin_pt * data).astype('>i'+str(nbits/8))
    return fixedpoint_data

def float2fixed_comp(nbits, bin_pt, data):
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

    check_overflow(nbits, bin_pt,  data_real)
    check_overflow(nbits, bin_pt,  data_imag)
    
    data_real = (2**bin_pt * data_real).astype('>u'+str(nbits/8))
    data_imag = (2**bin_pt * data_imag).astype('>u'+str(nbits/8))

    # combine real and imag data
    data_real = 2**nbits * (data_real.astype('>u'+str(2*nbits/8)))
    data_comp = (data_real + data_imag).astype('>u'+str(2*nbits/8))

    return data_comp

def check_overflow(nbits, bin_pt, data):
    """
    Given a signed fixed point representation of bitwidth nbits and 
    binary point bin_pt, check if the data array contains values that
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
        print "WARNING! Maximum value exceeded in overflow check."
        print "Max allowed value: " + str(max_val)
        print "Max data value: " + str(max_data)

    if min_data < min_val:
        print "WARNING! Minimum value exceeded in overflow check."
        print "Min allowed value: " + str(min_val)
        print "Min data value: " + str(min_data)
