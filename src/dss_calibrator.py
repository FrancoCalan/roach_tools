import time
import numpy as np
from experiment import Experiment
from spectra_animator import SpectraAnimator

class DssCalibrator(Experiment):
    """
    This class is used to calibrate a Sideband Separating receiver.
    """
    def __init__(self, calanfpga):
        Experiment.__init__(self, calanfpga)
        self.calplotter = DssCalibratedPlotter(self.fpga)
        
    def run_dss_calibration(self):
        """
        Perform a full DSS calibration with constants and SRR computation. 
        """
        run_srr_computation(self)

    def run_srr_computation(self, ideal=False):
        """
        Compute SRR from the calibrated receiver using ideal or computed
        calibration constants.
        """
        if ideal:
            self.load_ideal_constants()

        self.calplotter.show_plot()
        while True:
            time.sleep(1)
            self.calplotter.plot_axes()

    def load_ideal_constants(self):
        """
        Load ideal constants into de DSS receiver.
        """
        nbram = len(self.settings.cal_brams_info['bram_list2d'][0])
        depth = 2**self.settings.cal_brams_info['addr_width']
        
        bram_info_zero = self.settings.cal_bram_info
        bram_info_zero['bram_list'] = self.settings.cal_brams_info['bram_list2d'][0]
        bram_info_ones = self.settings.cal_bram_info
        bram_info_ones['bram_list'] = self.settings.cal_brams_info['bram_list2d'][1]

        fpga.write_bram_list_data(bram_info_zero, np.zeros(brams, depth))
        fpga.write_bram_list_data(bram_info_ones, np.ones(brams, depth))

    class DssCalibratedPlotter(SpectraAnimator):
        """
        Inner class for post-calibration plots.
        """
        def __init__(self, calanfpga):
            SpectraAnimator.__init__(self, calanfpga)
            #self.nplots = 4

        def show_plot(self):
            """
            Override Plotter show plot to only show the matplotlib fig (no GUI).
            """
            sel.ffig.set_tight_layout(True)
            self.create_window(create_gui=False)

