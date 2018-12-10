from multi_line_axis import MultiLineAxis

class SnapshotCalAxis(MultiLineAxis):
    """
    Class representing an axis from a snapshot plot, intendend to plot two snapshot
    in the same axis. Used to test calibration results.
    """
    def __init__(self, ax, snap_samples, title=""):
        xdata = range(snap_samples)
        legends = ['Uncalibrated', 'Calibrated']
        MultiLineAxis.__init__(self, ax, xdata, legends, title)

        self.ax.set_xlim((0, snap_samples))
        self.ax.set_ylim((-140, 140)) # Hardcoded 8-bit ADC
        self.ax.set_xlabel('Sample')
        self.ax.set_ylabel('Amplitude [a.u.]')
