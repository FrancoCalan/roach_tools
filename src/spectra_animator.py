import numpy as np
import Tkinter as Tk
from itertools import chain
from animator import Animator
from calanfigure import CalanFigure
from axes.spectrum_axis import SpectrumAxis
from experiment import get_nchannels

class SpectraAnimator(Animator):
    """
    Class responsable for drawing spectra plots.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.figure = CalanFigure(n_plots=len(self.settings.plot_titles), create_gui=True)
        self.nchannels = get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(0, self.settings.bw, self.nchannels, endpoint=False)
        
        for i in range(self.figure.n_plots):
            self.figure.create_axis(i, SpectrumAxis, self.freqs, self.settings.plot_titles[i])
        
    def add_figure_widgets(self):
        """
        Add widgets to spectrometer figure.
        """
        # save button/entry
        self.add_save_widgets('spec_data')
        # reset button
        self.add_reset_button('cnt_rst', 'Reset')
        # acc_len entry
        self.add_reg_entry(self.settings.spec_info['acc_len_reg'])

    def get_save_data(self):
        """
        Get spectra data for saving.
        :return: spectra data in dictionary format.
        """
        save_data = Animator.get_save_data(self)
        save_data['acc_len'] = self.fpga.read_reg('acc_len')

        return save_data

    def get_data(self):
        """
        Gets the spectra data from the spectrometer model.
        :return: spectral data.
        """
        spec_data = self.fpga.get_bram_data_interleave(self.settings.spec_info)
        spec_data = self.scale_dbfs_spec_data(spec_data, self.settings.spec_info)
        
        return spec_data
