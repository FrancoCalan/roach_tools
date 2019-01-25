import numpy as np
from ..plotter import Plotter
from ..calanfigure import CalanFigure
from spectrogram_axis import SpectrogramAxis

class DramSpectrogramPlotter(Plotter):
    """
    Class to plot an spectrogram (consecutive spectra) saved
    in ROACH's DRAM.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.nchannels = self.settings.specgram_info['n_channels']
        self.figure = CalanFigure(n_plots=1, create_gui=True)
        self.figure.create_axis(0, SpectrogramAxis, self.nchannels, self.settings.bw, self.figure.fig, 'DRAM Spectrogram')

    def get_data(self):
        """
        Get spectrogram data from ROACH's dram.
        :return: spectrogram data.
        """
        return get_dram_spectrogram_data(self.fpga, self.settings.specgram_info)

def get_dram_spectrogram_data(fpga, specgram_info):
    """
    Get spectrogram data from DRAM given the CalanFpga object 
    and dram_info dict.
    :param fpga: CalanFpga object.
    :param spec_info: dictionary with info of the dram memory 
        spectrogram data in the FPGA.
    :return: spectrogram data in dBFS.
    """
    nchnls = specgram_info['n_channels']
    specgram_arr = fpga.get_dram_data(specgram_info)
    specgram_mat = specgram_arr.reshape(nchnls, len(specgram_arr)/nchnls) # convert spectrogram data into a time x freq matrix
    specgram_mat = np.transpose(specgram_mat) # rotate matrix to have freq in y axis, and time in x axis
    specgram_mat = 10*np.log10(specgram_mat+1) # convert data to dB
    
    return [specgram_mat]

            
