import time, datetime, json
import numpy as np
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels, get_channel_from_freq
from ..calanfigure import CalanFigure
from ..instruments.generator import create_generator
from ..spectra_animator import scale_dbfs_spec_data
from ..axes.spectrum_axis import SpectrumAxis
from magratio_axis import MagRatioAxis
from anglediff_axis import AngleDiffAxis

class VVFreqTest(Experiment):
    """
    Class used to test the vector voltmeter. A vector
    voltmeter has two sinewaves with the same frequency as
    input an outputs the magnitude ratio and the angle
    difference of the inputs. The test consists in comparing
    the output for two equivalent sinewaves with different
    magnitude ratio. The variance of the measurement for each
    magnitude ratio tested is also computed.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)

        self.nchannels = get_nchannels(self.settings.spec_info)

        self.source = create_generator(self.settings.test_source)
        self.nsamples = self.settings.nsamples
        self.tested_magratios = self.settings.tested_magratios
        self.test_freq = self.settings.test_source['def_freq']
        self.test_chnl = get_channel_from_freq(self.settings.bw, 
            self.test_freq, self.settings.spec_info)

        self.figure = CalanFigure(n_plots=4, create_gui=False)
        self.figure.create_axis(0, SpectrumAxis, self.nchannels, self.settings.bw, "ZDOK0")
        self.figure.create_axis(1, SpectrumAxis, self.nchannels, self.settings.bw, "ZDOK1")
        self.figure.create_axis(2, MagRatioAxis, range(self.nsamples), "Power Ratio")
        self.figure.create_axis(3, AngleDiffAxis, range(self.nsamples), "Angle Difference")

        self.datadir = self.settings.datadir + '_' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.testinfo = {'bw'               : self.settings.bw,
                         'nchannels'        : self.nchannels,
                         'tested_magratios' : self.settings.tested_magratios,
                         'acc_len'          : self.fpga.read_reg(self.settings.spec_info['acc_len_reg']),
                         'source_freq'      : self.settings.test_source['def_freq'],
                         'source_power'     : self.settings.test_source['def_power']}

    def run_vmfreq_test(self):
        """
        Performs a vmfreq test. fix an input signal for both inputs, 
        and computed the magnitude ratio and the phase difference.
        Takes several samples (given by the self.nsamples variable)
        and them computes the variance of the data. Perfom this test
        for several levels of magnitude ratio, that have to be manually
        set by the user.
        """
        # set power source (set to default given in config file)
        self.source.set_power_dbm()
        self.source.set_freq_mhz()
        self.source.turn_output_on()

        # iterates for all the magnitude ratio to test
        print "Starting VMFreq test..."
        for test_magratio in self.tested_magratios:
            raw_input("Set the power ratio ZDOK0/ZDOK1=" + str(test_magratio) + "dB.\n" +
                "Press enter to continue.")
            
            comp_ratios = []
            # compute power ratio and angle diff nsamples times
            for i in range(self.nsamples):
                # get power-crosspower data
                a2, b2 = self.fpga.get_bram_data_interleave(self.settings.spec_info)
                ab_re, ab_im = self.fpga.get_bram_data_interleave(self.settings.crosspow_info)

                # compute complex ratios
                ab = ab_re[self.test_chnl] + 1j*ab_im[self.test_chnl]
                #comp_ratios.append(ab / b2[self.test_chnl]) # ab* / bb* = a/b = USB/LSB.
                comp_ratios.append(np.conj(ab) / a2[self.test_chnl]) # (ab*)* / bb* = b/a = LSB/USB.

                # plot spec data
                a2_dbfs = scale_dbfs_spec_data(self.fpga, a2, self.settings.spec_info)
                self.figure.axes[0].plot(a2_dbfs)
                b2_dbfs = scale_dbfs_spec_data(self.fpga, b2, self.settings.spec_info)
                self.figure.axes[1].plot(b2_dbfs)

                # plot power ratio
                #self.figure.axes[2].plot(range(i+1), 20*np.log10(np.abs(comp_ratios)))
                self.figure.axes[2].plot(range(i+1), -1*20*np.log10(np.abs(comp_ratios)))
                # plot angle difference
                #self.figure.axes[3].plot(range(i+1), np.angle(comp_ratios, deg=True))
                self.figure.axes[3].plot(range(i+1), -1*np.angle(comp_ratios, deg=True))

                #print "a^2/b^2 power ratio: \t" + str(a2_dbfs[self.test_chnl] - b2_dbfs[self.test_chnl])
                #print "(ab/b^2)^2 power ratio: " + str(10*np.log10(np.abs(comp_ratios[-1])**2))

                plt.pause(self.settings.pause_time)

            self.testinfo['data_'+str(test_magratio)+'db'] = {'mag_ratios'  : np.abs(comp_ratios).tolist(),
                                                              'angle_diffs' : np.angle(comp_ratios).tolist()}

        self.source.turn_output_off()
        print "test done"

        # save data
        print "Saving data..."
        with open(self.datadir+'.json', 'w') as jsonfile:
            json.dump(self.testinfo, jsonfile, indent=4)
        print "done"
