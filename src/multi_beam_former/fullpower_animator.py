import numpy as np
from ..animator import Animator
from ..calanfigure import CalanFigure
from fullpower_axis import FullpowerAxis

class FullpowerAnimator(Animator):
    """
    Class used to plot full bandwidth power of ADC signals
    as bar plot. Useful to test the power calibration of 
    multiple ADC.
    """
    def __init__(self, calanfpga):
        Animator.__init__(self, calanfpga)
        self.figure = CalanFigure(n_plots=1, create_gui=True)
        self.figure.create_axis(0, FullpowerAxis, self.settings.pow_info['reg_list'])

    def add_figure_widgets(self):
        """
        Add widgets to full power figure.
        """
        # save button/entry
        self.add_save_widgets("fullpower_data")
        # reset button
        self.add_reset_button('pow_rst', 'Reset')
        # acc_len entry
        self.add_reg_entry(self.settings.pow_info['acc_len_reg'])

    def get_data(self):
        """
        Get full power data from FPGA bram memory.
        """
        pow_data_arr = self.fpga.get_reg_list_data(self.settings.pow_info['reg_list'])
        pow_data_arr = pow_data_arr / float(self.fpga.read_reg(self.settings.pow_info['acc_len_reg'])) # divide by accumulation
        pow_data_arr = 10*np.log10(pow_data_arr) # convert to db
        pow_data_arr = pow_data_arr - (6.02*8 + 1.76) # convert to dBFS (Hardcoded 8-bit ADC) 
        return pow_data_arr
