from ..axes.multi_line_axis import MultiLineAxis

class SpectrumAxis(MultiLineAxis):
    """
    Class representing an axis from a spectrum plot, intendend to plot two spectra
    in the same axis. Used to test calibration results.
    """
    def __init__(self, ax, freqs, title=""):
        legends = ['Uncalibrated', 'Calibrated']        
        MultiLineAxis.__init__(self, ax, freqs, legends, title)

        self.ax.set_xlim((self.xdata[0], self.xdata[-1]))
        self.ax.set_ylim((-100, 10))
        self.ax.set_xlabel('Frequency [MHz]')
        self.ax.set_ylabel('Power [dBFS]')

