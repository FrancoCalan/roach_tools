import numpy as np
from single_line_axis import SingleLineAxis

class MagRatioAxis(SingleLineAxis):
    """
    Class representing an axis from a magnitude ratio plot.
    """
    def __init__(self, ax, nchannels, bw, title=""):
        xdata = np.linspace(0, bw, nchannels, endpoint=False)
        SingleLineAxis.__init__(self, ax, xdata, title)

        self.ax.set_xlim((0, bw))
        self.ax.set_ylim((0, 2))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Magnitude ratio [linear]')

