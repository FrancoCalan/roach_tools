import numpy as np
from multi_line_axis import MultiLineAxis

class SpectrumCalAxis(MultiLineAxis):
    """
    Class representing an axis from a spectrum plot, intendend to plot two spectra
    in the same axis. Used to test calibration results.
    """
    def __init__(self, ax, nchannels, bw, title=""):
        xdata = np.linspace(0, bw, nchannels, endpoint=False)
        legends = ['Uncalibrated', 'Calibrated']        
        MultiLineAxis.__init__(self, ax, xdata, legends, title)

        self.ax.set_xlim((0, bw))
        self.ax.set_ylim((-100, 10))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Power [dBFS]')

