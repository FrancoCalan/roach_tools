import numpy as np
from ..axes.single_line_axis import SingleLineAxis

class AngleDiffAxis(SingleLineAxis):
    """
    Class representing an axis from an angle difference plot.
    """
    def __init__(self, ax, nchannels, bw, title=""):
        xdata = np.linspace(0, bw, nchannels, endpoint=False)
        SingleLineAxis.__init__(self, ax, xdata, title)

        self.ax.set_xlim((0, bw))
        self.ax.set_ylim((-200, 200))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Angle difference [Deg]')

