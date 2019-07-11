from ..axes.multi_line_axis import MultiLineAxis

class CancellationAxis(MultiLineAxis):
    """
    Class representing an axis from a spectrum plot, intendend
    for displaying the results of of the balance mixer calibrator.
    """
    def __init__(self, ax, freqs, title=""):
        legends = ['Uncalibrated', 'Ideal Constants', 'Calibrated Constants']
        MultiLineAxis.__init__(self, ax, freqs, legends, title)

        self.ax.set_xlim((self.xdata[0], self.xdata[-1]))
        self.ax.set_ylim((-100, 10))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Power [dBFS]')

