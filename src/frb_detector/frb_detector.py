import numpy as np
import Tkinter as Tk
from decimal import Decimal
from ..spectra_animator import SpectraAnimator, scale_dbfs_spec_data
from ..experiment import get_freq_from_channel

class FRBDetector(SpectraAnimator):
    """
    Class used to detect FRB with a dedisperion model.
    """
    def __init__(self, calanfpga):
        SpectraAnimator.__init__(self, calanfpga)

    def add_figure_widgets(self):
        """
        Add widgets for frb detector figure.
        """
        SpectraAnimator.add_figure_widgets(self)

        # theta entry (threshold)
        self.add_reg_entry('theta')

        # total power label
        self.add_label("Total power = ") # = self.labels[0]

        # detection label
        self.add_label("No FRB detected :(") # = self.labels[1]

    def get_data(self):
        """
        Gets the spectra data from FRB detector model, this includes the dispersed signal,
        the dedisperded signal, and th desispersed freezed signal. Also, manage the labels
        to show the current total power in the freezed data, and if an FRB was detected.
        :return: spectral data.
        """
        spec_data = self.fpga.get_bram_data_interleave(self.settings.spec_info)
        
        self.labels[0]['text'] = 'Total power = ' + "{:.3E}".format(np.sum(spec_data[2]))
        
        if self.fpga.read_reg('frb_detector') == 1:
            self.labels[1]['text'] = 'FRB detected! :D'
        else:
            self.label[1]['text'] = 'No FRB detected :('

        spec_data = scale_dbfs_spec_data(self.fpga, spec_data, self.settings.spec_info)
        return spec_data
