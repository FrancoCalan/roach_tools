from axes.fullpower_bar_axis import FullPowerBarAxis

class FullpowerAnimator(Plotter):
    """
    Class used to plot full bandwidth power of ADC signals
    as bar plot. Useful to test the power calibration of 
    multiple ADC.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfoga)
        self.figure = CalanFigure(n_plots=1, create_gui=True)
        self.figure.create_axis(0, FullPowerBarAxis, self.settings.pow_info['reg_list'])

    def add_figure_widgets(self):
        """
        Add widgets to full power figure.
        """
        # save button/entry
        self.add_save_widgets("spec_data")

        # acc_len entry
        self.add_reg_entry(self.settings.pow_info['acc_len_reg'])

    def get_data(self):
        """
        Get full power data from FPGA bram memory.
        """
        pow_data_arr = self.fpga.get_reg_list_data(self.settings.pow_info['reg_list'])
        pow_data_arr = pow_data_arr / float(fpga.read_reg(self.settings.pow_info['acc_len_reg']))
        return pow_data
