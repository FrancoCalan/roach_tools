from ..axes.single_line_axis import SingleLineAxis

class PolAxis(SingleLineAxis):
    """
    Class representing an axis from an polarization isolation
    test (for digital omt calibration tests).
    """
    def __init__(self, ax, freqs, title=""):
        SingleLineAxis.__init__(self, ax, freqs, title)

        self.ax.set_xlim((self.xdata[0], self.xdata[-1]))
        self.ax.set_ylim((0, 80))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Polarization Isolation [dB]')

