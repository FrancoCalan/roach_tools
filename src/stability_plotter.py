import sys, os
sys.path.append(os.getcwd())
import numpy as np
from plotter import Plotter
from axes.mag_ratio_time_axis import MagRatioTimeAxis
from axes.angle_diff_time_axis import AngleDiffTimeAxis

class StabilityPlotter(Plotter):
    """
    Class responsable for drawing magnitude ratio and angle difference
    in order to visualize the stability between two signals.
    """
    def __init__(self, calanfpga):
        Plotter.__init__(self, calanfpga)
        self.figure = CalaanFigure(2, create_gui=True)

        # get xdata
        n_specs = 2**self.settings.inst_chnl_info['addr_width']
        self.time_arr = get_spec_time_arr(self.settings.bw, n_specs, self.settings.spec_info)
        
        self.figure.create_axis(0, MagRatioTimeAxis, self.time_arr, 'Magnitude Ratio')
        self.figure.create_axis(1, AngleDiffTimeAxis, self.time_arr, 'Angle Difference')

    def get_save_data(self):
        """
        Get stability data for saving.
        :returns: stability data in dictionary format.
        """
        save_data = Plotter.get_save_data(self)
        self.data_dict['channel'] = self.fpga.read_reg('channel')

    def get_data(self):
        """
        Gets the complex data from a single channel within consecutive instantaneous spectra
        for different inputs. Then computes the magnitude ratio and angle difference.
        :return: stability data array.
        """
        [[chnl0_data_real, chnl0_data_imag], [chnl1_data_real, chnl1_data_imag]] =\
            self.fpga.get_bram_list2d_data(self.settings.inst_chnl_info)

        chnl0_data = np.array(chnl0_data_real) + 1j*np.array(chnl0_data_imag)
        chnl1_data = np.array(chnl1_data_real) + 1j*np.array(chnl1_data_imag)

        stability_data = chnl1_data / chnl0_data

        return [np.abs(stability_data), np.angle(stability_data, deg=True)]

