import numpy as np
from ..axes.single_line_axis import SingleLineAxis

class SrrAxis(SingleLineAxis):
    """
    Class representing an axis from sideband rejection ratio plot 
    (sideband separating receivers).
    """
    def __init__(self, ax, nchannels, bw, title=""):
        xdata = np.linspace(0, bw, nchannels, endpoint=False)
        SingleLineAxis.__init__(self, ax, xdata, title)

        self.ax.set_xlim((0, bw))
        self.ax.set_ylim((0, 80))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Sideband Rejection Ratio [dB]')

