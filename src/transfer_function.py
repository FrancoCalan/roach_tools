import numpy as np
import matplotlib.pyplot as plt
from experiment import Experiment, get_nchannels
from calanfigure import CalanFigure
from spectra_animator import scale_spec_data

class TransferFunction(Experiment):
    """
    Class to perform a transfer function experiment, that is,
    compute the gain v/s frequency of a device under test.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)

        self.nchannels = get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(0, self.settings.bw, self.nchannels, endpoint=False)

        self.source = self.create_instrument(self.settings.source)
        self.test_channels = range(1, self.nchannels, self.settings.chnl_step)

        self.figure = CalanFigure(n_plots=2, create_gui=False)
        self.figure.create_axis(0, SpectrumAxis, self.nchannels, self.settings.bw, "Current Spectrum")
        self.figure.create_axis(1, SpectrumAxis, self.nchannels, self.settings.bw, "Transfer Function")

    def run_transfer_function_test(self):
        """
        Performs a transfer funcion test. Sweeps tone in the input and computes
        the power at the output.
        """
        Hf_arr = [] # transfer function array

        # set source power
        self.source.set_power_dbm()
        self.source.turn_output_on()

        for i, chnl in enumerate(self.test_channels):
            # set generator frequency
            self.source.set_freq_mhz(self.freqs[chnl])
            time.sleep(self.settings.pause_time)

            # get spectrum data
            spec_data = self.get_bram_interleaved_data(self.settings.spec_info)
            spec_data_dbfs = scale_spec_data(spec_data, self.settings.spec_info)

            # update transfer function
            Hf_arr.append(spec_data_dbfs[chnl])

            # plot spectrum and transfer function
            self.figure.axis[0].plot(spec_data_dbfs)
            partial_freqs = self.freqs[self.test_channels[:i+1]]
            self.figure.axis[1].plot(partial_freqs, Hf_arr)

            plt.pause(self.settings.pause_time)

        self.source.turn_output_off()
