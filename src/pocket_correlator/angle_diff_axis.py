from ..axes.multi_line_axis import MultiLineAxis

class AngleDiffAxis(MultiLineAxis):
    """
    Class representing an axis from an angle difference plot.
    """
    def __init__(self, ax, freqs, legends, title=""):
        MultiLineAxis.__init__(self, ax, freqs, legends, title)

        self.ax.set_xlim((self.xdata[0], self.xdata[-1]))
        self.ax.set_ylim((-200, 200))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Angle difference [Deg]')

