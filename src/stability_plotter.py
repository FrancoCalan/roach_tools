import sys, os
sys.path.append(os.getcwd())
import numpy as np
from plotter import Plotter
from single_line_axis import SingleLineAxis

class StabilityPlotter(Plotter):
    """
    Class responsable for drawing magnitude ratio and angle difference
    in order to visualize the stability between two signals.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.ylims = [(-1, 10), (-200, 200)]
        self.ylabels = ['Magnitude ratio', 'Angle difference [deg]']

        # get current channel frequency for title
        chnl_freq = self.get_freq_from_channel(self.fpga.read_reg('channel'))
        self.titles = ['Stability Test\nChannel at freq: ' + str(chnl_freq), '']
        self.nplots = len(self.titles)
        mpl_axes = self.create_axes()

        # get xdata
        n_specs = 2**self.settings.inst_chnl_info['addr_width']
        self.xdata = self.get_spec_time_arr(n_specs)

        for i, ax in enumerate(mpl_axes):
            ax.set_title(self.titles[i])
            ax.set_xlim((0, self.xdata[-1]))
            ax.set_ylim(self.ylims[i])
            ax.set_xlabel('Time [$\mu$s]')
            ax.set_ylabel(self.ylabels[i])
            self.axes.append(SingleLineAxis(ax, self.xdata))

    def get_data(self):
        """
        Gets the complex data from a single channel within consecutive instantaneous spectra
        for different inputs. Then computes the magnitude ratio and angle difference.
        """
        [[chnl0_data_real, chnl0_data_imag], [chnl1_data_real, chnl1_data_imag]] =\
            self.fpga.get_bram_list2d_data(self.settings.inst_chnl_info)

        chnl0_data = np.array(chnl0_data_real) + 1j*np.array(chnl0_data_imag)
        chnl1_data = np.array(chnl1_data_real) + 1j*np.array(chnl0_data_imag)

        stability_data = chnl1_data / chnl0_data

        return [np.abs(stability_data), np.angle(stability_data, deg=True)]

    def data2dict(self):
        """
        Creates dict with stability data for file saving.
        """
        data_dict = {}

        data_arr = self.get_data()
        for axis, data in zip(self.axes, data_arr):
            data_dict[axis.ax.get_title() + ' ' + axis.ax.get_ylabel()] = data.tolist()

        data_dict[axis.ax.get_xlabel()] = self.xdata.tolist()

        return data_dict
