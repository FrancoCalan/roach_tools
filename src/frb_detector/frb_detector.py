import numpy as np
import Tkinter as Tk
from decimal import Decimal
from ..spectra_animator import SpectraAnimator, scale_dbfs_spec_data_arr
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
        """
        spec_data_arr = self.fpga.get_bram_list_data_interleave(self.settings.spec_info)
        
        self.labels[0]['text'] = 'Total power = ' + "{:.3E}".format(np.sum(spec_data_arr[2]))
        
        if self.fpga.read_reg('frb_detector') == 1:
            self.labels[1]['text'] = 'FRB detected! :D'
        else:
            self.label[1]['text'] = 'No FRB detected :('

        spec_plot_arr = scale_dbfs_spec_data_arr(self.fpga, spec_data_arr, self.settings.spec_info)
        return spec_plot_arr
