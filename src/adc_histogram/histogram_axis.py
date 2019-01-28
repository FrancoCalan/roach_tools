from ..axes.bar_axis import BarAxis

class HistogramAxis(BarAxis):
    """
    Class representing an axis for aDC raw data histogram.
    """
    def __init__(self, ax, xdata, title=""):
        BarAxis.__init__(self, ax, xdata, title)

        self.ax.set_xlim((xdata[0], xdata[-1]))
        self.ax.set_ylim((0, 0.035)) # Hardcoded 8-bit ADC
        self.ax.set_xlabel('Code')
        self.ax.set_ylabel('Normalized Frequency')
