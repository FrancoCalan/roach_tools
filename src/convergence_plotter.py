import sys, os
sys.path.append(os.getcwd())
from plotter import Plotter
from experiment import linear_to_dBFS
from axes.multi_line_axis import MultiLineAxis

class ConvergencePlotter(Plotter):
    """
    Class responsable for drawing power plots v/s time for filter output. 
    It includes channel power, max power, and mean power.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.nplots = 1
        self.legends = ['chnl', 'max', 'mean']
        mpl_axis = self.create_axes()[0]

        # get xdata
        n_specs = 2**self.settings.conv_info_chnl['addr_width']
        self.xdata = self.get_spec_time_arr(n_specs)

        mpl_axis.set_title('')
        mpl_axis.set_xlim(0, self.xdata[-1])
        mpl_axis.set_ylim((-100, 10))
        mpl_axis.set_xlabel('Time [$\mu$s]')
        mpl_axis.set_ylabel('Power [dBFS]')
        self.axes.append(MultiLineAxis(mpl_axis, self.xdata, self.legends))


    def get_data(self):
        """
        Gets the convergence analysis data. This includes single channel power,
        max channel power, and mean channel power.
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

    def data2dict(self):
        """
        Creates dict with convergence data for file saving.
        """
        self.get_ydata_to_dict()
        self.data_dict.update(self.axes[0].gen_xdata_dict())
        self.data_dict['filter_gain'] = self.fpga.read_reg('filter_gain')
        self.data_dict['filter_acc'] = self.fpga.read_reg('filter_acc')
        self.data_dict['channel'] = self.fpga.read_reg('channel')
