from single_line_axis import SingleLineAxis

class SpectrumAxis(SingleLineAxis):
    """
    Class representing an axis from a spectrum plot.
    """
    def __init__(self, ax, freqs, title=""):
        SingleLineAxis.__init__(self, ax, freqs, title)

        self.ax.set_xlim((self.xdata[0], self.xdata[-1]))
        self.ax.set_ylim((-100, 10))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Power [dBFS]')

