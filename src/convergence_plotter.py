import sys, os
sys.path.append(os.getcwd())
from experiment import linear_to_dBFS, get_spec_time_arr
from plotter import Plotter
from calanfigure import CalanFigure
from axes.convergence_axis import ConvergenceAxis

class ConvergencePlotter(Plotter):
    """
    Class responsable for drawing power plots v/s time for filter output. 
    It includes channel power, max power, and mean power.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.figure = CalanFigure(1, create_gui=True)
        
        # get xdata
        n_specs = 2**self.settings.conv_info_chnl['addr_width']
        self.time_arr = get_spec_time_arr(self.settings.bw, n_specs, self.settings.spec_info)
        
        self.figure.create_axis(0, ConvergenceAxis, self.time_arr)

    def add_figure_widgets(self):
        """
        Add widgets for convergence figure.
        """
        self.add_save_widgets("conv_data")

    def get_save_data(self):
        """
        Get convergence data for saving.
        :return: convergence data in dictionary format.
        """
        save_data = Plotter.get_save_data(self)
        save_data.update(self.figure.axes[0].gen_xdata_dict())
        save_data['filter_gain'] = self.fpga.read_reg('filter_gain')
        save_data['filter_acc'] = self.fpga.read_reg('filter_acc')
        save_data['channel'] = self.fpga.read_reg('channel')
        
        return save_data

    def get_data(self):
        """
        Gets the convergence analysis data. This includes single channel power,
        max channel power, and mean channel power.
        :return: convergence data array.
        """
        # single channel
        [chnl_data_real, chnl_data_imag] = self.fpga.get_bram_list_data(self.settings.conv_info_chnl)
        chnl_data = chnl_data_real**2 + chnl_data_imag**2 # compute power
        chnl_data = linear_to_dBFS(chnl_data, self.settings.spec_info)
        
        # max channel
        max_data = self.fpga.get_bram_data(self.settings.conv_info_max)
        max_data = linear_to_dBFS(max_data, self.settings.spec_info)

        # mean channel
        mean_data = self.fpga.get_bram_data(self.settings.conv_info_mean)
        mean_data = linear_to_dBFS(mean_data, self.settings.spec_info)

        return [[chnl_data, max_data, mean_data]]
