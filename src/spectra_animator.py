import numpy as np
import Tkinter as Tk
from itertools import chain
from animator import Animator
from calanfigure import CalanFigure
from axes.spectrum_axis import SpectrumAxis
from experiment import linear_to_dBFS, get_nchannels

class SpectraAnimator(Animator):
    """
    Class responsable for drawing spectra plots.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.figure = CalanFigure(n_plots=len(self.settings.plot_titles), create_gui=True)
        self.nchannels = get_nchannels(self.settings.spec_info)
        
        for i in range(self.figure.n_plots):
            self.figure.create_axis(i, SpectrumAxis, 
                self.nchannels, self.settings.bw, self.settings.plot_titles[i])
        
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
        spec_info = self.settings.spec_info
        spec_data = self.fpga.get_bram_data_interleave(spec_info)
        spec_data = scale_dbfs_spec_data(self.fpga, spec_data, spec_info)
        
        return spec_data

def scale_dbfs_spec_data(fpga, spec_data, spec_info):
    """
    Scale spectral data by the accumulation length given by the
    accumulation reg in the spec_info dictionary, and convert
    the data to dBFS. Used for plotting spectra.
    :param fpga: CalanFpga object.
    :param spec_data: spectral data in linear scale, as read with CalanFpga's
        get_bram_data(). Can be a numpy array or a list (with possible more 
        inner lists) of numpy arrays.
    :param spec_info: dictionary with info of the memory with 
        the spectral data in the FPGA.
    :return: spectral data in dBFS.
    """
    if isinstance(spec_data, np.ndarray): 
        spec_data = spec_data / float(fpga.read_reg(spec_info['acc_len_reg'])) # divide by accumulation
        spec_data = linear_to_dBFS(spec_data, spec_info)
        return spec_data
        
    else: # spec_data is list
        spec_data = [scale_dbfs_spec_data(fpga, spec_data_item, spec_info) for spec_data_item in spec_data]
        return spec_data
