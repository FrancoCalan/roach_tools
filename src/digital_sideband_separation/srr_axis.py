from ..axes.single_line_axis import SingleLineAxis

class SrrAxis(SingleLineAxis):
    """
    Class representing an axis from sideband rejection ratio plot 
    (sideband separating receivers).
    """
    def __init__(self, ax, freqs, title=""):
        SingleLineAxis.__init__(self, ax, freqs, title)

        self.ax.set_xlim((self.xdata[0], self.xdata[-1]))
        self.ax.set_ylim((0, 80))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Sideband Rejection Ratio [dB]')

