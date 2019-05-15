import os, time, datetime, json
import numpy as np
import matplotlib.pyplot as plt
from ..experiment import Experiment, get_nchannels, init_sources, turn_off_sources
from ..calanfigure import CalanFigure
from ..instruments.generator import create_generator
from ..axes.spectrum_axis import SpectrumAxis

class FrequencyResponse(Experiment):
    """
    Class to perform a frequency response experiment, that is,
    compute the gain v/s frequency of a device under test.
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
        self.figure = CalanFigure(n_plots=2*self.n_inputs, create_gui=False)
        for i, spec_title in enumerate(self.settings.spec_titles):
            self.figure.create_axis(i, SpectrumAxis, self.freqs, "Spectrum " + spec_title)
        for i, spec_title in enumerate(self.settings.spec_titles):
            self.figure.create_axis(i+self.n_inputs, SpectrumAxis, self.freqs, "Freq resp " + spec_title)

        # backup parameters
        self.dataname = os.path.splitext(self.setttings.boffile)[0]
        self.dataname = 'frequency_response ' + self.dataname + ' '
        self.datadir = self.dataname + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.testinfo = {'freqs'        : list(self.test_freqs),
                         'acc_len'      : self.fpga.read_reg(self.settings.spec_info['acc_len_reg']),
                         'source_power' : self.settings.test_source['def_power']}

    def run_frequency_response_test(self):
        """
        Performs a frequency response test. Sweeps tone in the inputs 
        and computes the power at the outputs.
        """
        freq_resp = [[] for i in range(self.n_inputs)]
        init_sources(self.rf_source)
        
        print "Computing frequency response..."
        for i, chnl in enumerate(self.test_channels):
            # set generator frequency
            self.rf_source.set_freq_mhz(self.freqs[chnl])
            time.sleep(self.settings.pause_time)

            # get spectrum data
            spec_data = self.fpga.get_bram_data_interleave(self.settings.spec_info)

            # scale spectrum data and convert it into dBFS
            spec_data_dbfs = self.scale_dbfs_spec_data(spec_data, self.settings.spec_info)

            partial_freqs = self.freqs[self.test_channels[:i+1]]
            for j, spec in enumerate(spec_data_dbfs):
                # update frequency response
                freq_resp[j].append(spec[chnl])

                # plot spectrum and frequency response
                self.figure.axes[j].plot(spec)
                self.figure.axes[j+self.n_inputs].plotxy(partial_freqs, freq_resp[j])
            
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
        self.testinfo['frequency_response'] = freq_resp
        with open(self.datadir+'.json', 'w') as jsonfile:
            json.dump(self.testinfo, jsonfile, indent=4)
        print "done"
