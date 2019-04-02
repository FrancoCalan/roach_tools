import numpy as np
import Tkinter as Tk
from decimal import Decimal
from ..spectra_animator import SpectraAnimator
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
        self.add_label("power_label", "Total power = ")

        # detection label
        self.add_label("detection_label", "No FRB detected :(")

    def get_data(self):
        """
        Gets the spectra data from FRB detector model, this includes the dispersed signal,
        the dedisperded signal, and th desispersed freezed signal. Also, manage the labels
        to show the current total power in the freezed data, and if an FRB was detected.
        :return: spectral data.
        """
        spec_data = self.fpga.get_bram_data_interleave(self.settings.spec_info)
        
        self.labels['power_label']['text'] = 'Total power = ' + "{:.3E}".format(np.sum(spec_data[2]))
        
        if self.fpga.read_reg('frb_detector') == 1:
            self.labels['detection_label']['text'] = 'FRB detected! :D'
        else:
            self.label['detection_label']['text'] = 'No FRB detected :('

        spec_data = self.scale_dbfs_spec_data(spec_data, self.settings.spec_info)
        return spec_data
