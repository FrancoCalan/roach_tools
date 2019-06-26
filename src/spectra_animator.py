import numpy as np
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
        self.bw = self.settings.bw
        self.nchannels = get_nchannels(self.settings.spec_info)
        self.freqs = np.linspace(0, self.bw, self.nchannels, endpoint=False)
        
        self.n_inputs = len(self.settings.spec_titles)
        self.figure = CalanFigure(n_plots=self.n_inputs, create_gui=True)
        for i, spec_title in enumerate(self.settings.spec_titles):
            self.figure.create_axis(i, SpectrumAxis, self.freqs, spec_title)
        
    def add_figure_widgets(self):
        """
        Add widgets to spectrometer figure.
        """
        # save button/entry
        self.add_save_widgets('spec_data')
        # reset button
        self.add_reset_button(self.settings.reset_regs, 'Reset')
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
        spec_data = self.fpga.get_bram_data(self.settings.spec_info)
        spec_data = self.scale_dbfs_spec_data(spec_data, self.settings.spec_info)
        
        return spec_data
