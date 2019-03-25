import numpy as np
from single_line_axis import SingleLineAxis

class SpectrumAxis(SingleLineAxis):
    """
    Class representing an axis from a spectrum plot.
    """
    def __init__(self, ax, nchannels, init_freq, bw, title=""):
        xdata = np.linspace(init_freq, init_freq+bw, nchannels, endpoint=False)
        SingleLineAxis.__init__(self, ax, xdata, title)

        self.ax.set_xlim((init_freq, init_freq+bw))
        self.ax.set_ylim((-100, 10))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Power [dBFS]')

