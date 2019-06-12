import os, time, datetime, json
import numpy as np
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels, init_sources, turn_off_sources
from ..calanfigure import CalanFigure
from ..instruments.generator import Generator, create_generator
from ..axes.spectrum_axis import SpectrumAxis
from mag_ratio_axis import MagRatioAxis
from angle_diff_axis import AngleDiffAxis

class PocketCorrelator(Experiment):
    """
    This class is used to compute the correlation
    of a system in ROACH. By correlation we mean the
    magnitude ratio and phase difference between two or
    more inputs. The first input is always used as the
    reference for the other inputs, where first is as defined
    by the ROACH model. 
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(0, self.bw, self.nchannels, endpoint=False)
                
        # test channels array
        chnl_start = self.settings.chnl_start
        chnl_stop  = self.settings.chnl_stop
        chnl_step  = self.settings.chnl_step
        self.test_channels = range(chnl_start, chnl_stop, chnl_step)
        self.test_freqs = self.freqs[self.test_channels]

        # sources
        self.rf_source = create_generator(self.settings.test_source)

        # figures and axes
        self.n_inputs = len(self.settings.spec_titles)
        self.figure = CalanFigure(n_plots=self.n_inputs+2, create_gui=False)

        for i, spec_title in enumerate(self.settings.spec_titles):
            self.figure.create_axis(i, SpectrumAxis,  self.freqs, spec_title)
        self.legends = self.settings.corr_legends
        self.figure.create_axis(self.n_inputs, MagRatioAxis, self.freqs, self.legends, 'Magnitude Ratio')
        self.figure.create_axis(self.n_inputs+1, AngleDiffAxis, self.freqs, self.legends, 'Angle Difference')

        # data save attributes
        self.dataname = os.path.splitext(self.settings.boffile)[0]
        self.dataname = 'pocket_correlator ' + self.dataname + ' '
        self.datadir = self.dataname + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.testinfo = {'bw'           : self.bw,
                         'nchannels'    : self.nchannels,
                         'acc_len'      : self.fpga.read_reg(self.settings.spec_info['acc_len_reg']),
                         'source_power' : self.settings.test_source['def_power']}

    def run_pocket_correlator_test(self):
        """
        Perform a pocket correlator test. Sweeps a tone in the inputs
        and compute the magnitude ratios and the phase differences at
        the outputs.
        """
        ratios = [[] for i in range(len(self.legends))]
        init_sources(self.rf_source)

        print "Computing correlation..."
        for i, chnl in enumerate(self.test_channels):
            # set generator frequency
            self.rf_source.set_freq_mhz(self.freqs[chnl])
            time.sleep(self.settings.pause_time)

            # get spectrum and cross spectrum data
            pow_data = self.fpga.get_bram_data(self.settings.spec_info)
            crosspow_data = self.fpga.get_bram_data(self.settings.crosspow_info)

            # combine real and imaginary part of crosspow data
            crosspow_data = np.array(crosspow_data[0::2]) + 1j*np.array(crosspow_data[1::2])

            # compute the complex ratios (magnitude ratio and phase difference)
            # use first input as reference
            aa = pow_data[0][chnl]
            for j, ab in enumerate(crosspow_data):
                ratios[j].append(np.conj(ab[chnl]) / aa) # (ab*)* / aa* = a*b / aa* = b/a
                
            # plot spectrum
            spec_data_dbfs = self.scale_dbfs_spec_data(pow_data, self.settings.spec_info)
            for j, spec in enumerate(spec_data_dbfs):
                self.figure.axes[j].plot(spec)
            
            # plot the magnitude ratio and phase difference
            self.figure.axes[-2].plotxy(self.test_freqs[:i+1], np.abs(ratios))
            self.figure.axes[-1].plotxy(self.test_freqs[:i+1], np.angle(ratios, deg=True))

            plt.pause(self.settings.pause_time)

        self.rf_source.turn_output_off()
        print "done"

        # print plot
        print "Printing figure..."
        self.figure.fig.set_tight_layout(False)
        self.figure.fig.savefig(self.datadir + '.pdf', bbox_inches='tight')
        print "done"

        # save data
        print "Saving data..."
        ratios_mag = np.abs(ratios).tolist() 
        ratios_ang = np.angle(ratios, deg=True).tolist() 
        self.testinfo['correlation_magnitudes'] = ratios_mag
        self.testinfo['correlation_angles'] = ratios_ang
        with open(self.datadir+'.json', 'w') as jsonfile:
            json.dump(self.testinfo, jsonfile, indent=4)
        print "done"
