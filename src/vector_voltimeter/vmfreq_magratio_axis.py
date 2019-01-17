from single_line_axis import SingleLineAxis

class VMFreqMagRatioAxis(SingleLineAxis):
    """
    Class representing an axis from a magnitude ratio v/s test number.
    """
    def __init__(self, ax, xdata, title=""):
        SingleLineAxis.__init__(self, ax, xdata, title)

        self.ax.set_xlim((0, self.xdata[-1]))
        self.ax.set_ylim((-1, 80))
        self.ax.set_xlabel('Test number')
        self.ax.set_ylabel('Magnitude ratio [dB]')

