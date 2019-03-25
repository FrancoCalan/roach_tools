import time, datetime, json
import numpy as np
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels
from ..calanfigure import CalanFigure
from ..instruments.generator import create_generator
from ..spectra_animator import scale_dbfs_spec_data
from ..axes.spectrum_axis import SpectrumAxis

class FrequencyResponse(Experiment):
    """
    Class to perform a frequency response experiment, that is,
    compute the gain v/s frequency of a device under test.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)

        self.init_freq = self.settings.init_freq
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(self.init_freq, self.init_freq+self.bw, self.nchannels, endpoint=False)

        self.source = create_generator(self.settings.test_source)
        self.test_channels = range(1, self.nchannels, self.settings.chnl_step)

        self.figure = CalanFigure(n_plots=2, create_gui=False)
        self.figure.create_axis(0, SpectrumAxis, self.nchannels, self.init_freq, self.bw, "Current Spectrum")
        self.figure.create_axis(1, SpectrumAxis, self.nchannels, self.init_freq, self.bw, "Frequency Response")

        self.datadir = self.settings.datadir + '_' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.testinfo = {'init_freq'    : self.init_freq,
                         'bw'           : self.bw,
                         'nchannels'    : self.nchannels,
                         'acc_len'      : self.fpga.read_reg(self.settings.spec_info['acc_len_reg']),
                         'source_power' : self.settings.test_source['def_power']}

    def run_frequency_response_test(self):
        """
        Performs a frequency response test. Sweeps tone in the input and computes
        the power at the output.
        """
        Hf_arr = [] # frequency response array

        # set source power
        self.source.set_power_dbm()
        self.source.turn_output_on()

        print "Computing frequency response..."
        for i, chnl in enumerate(self.test_channels):
            # set generator frequency
            self.source.set_freq_mhz(self.freqs[chnl])
            time.sleep(self.settings.pause_time)

            # get spectrum data
            spec_data = self.fpga.get_bram_data_interleave(self.settings.spec_info)
            # consider only the first spectrum if multiple are defined
            if isinstance(spec_data, list):
                spec_data = spec_data[0]
            spec_data_dbfs = scale_dbfs_spec_data(self.fpga, spec_data, self.settings.spec_info)

            # update frequency response
            Hf_arr.append(spec_data_dbfs[chnl])

            # plot spectrum and frequency response
            self.figure.axes[0].plot(spec_data_dbfs)
            partial_freqs = self.freqs[self.test_channels[:i+1]]
            self.figure.axes[1].plot(partial_freqs, Hf_arr)

            plt.pause(self.settings.pause_time)

        self.source.turn_output_off()
        print "done"

        # print plot
        print "Printing figure..."
        freqs =[self.freqs[chnl] for chnl in self.test_channels]
        fig = plt.figure()
        plt.plot(freqs, Hf_arr)
        plt.grid()
        plt.xlabel('Frequncy [MHz]')
        plt.ylabel('dBFS')
        plt.savefig(self.datadir + '.pdf', bbox_inches='tight')
        print "done"

        # save data
        print "Saving data..."
        self.testinfo['frequency_response'] = Hf_arr
        with open(self.datadir+'.json', 'w') as jsonfile:
            json.dump(self.testinfo, jsonfile, indent=4)
        print "done"

