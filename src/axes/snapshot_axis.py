from single_line_axis import SingleLineAxis

class SnapshotAxis(SingleLineAxis):
    """
    Class representing an axis from a snapshot plot.
    """
    def __init__(self, ax, snap_samples, title=""):
        xdata = range(snap_samples)
        SingleLineAxis.__init__(self, ax, xdata, title)

        self.ax.set_xlim((0, snap_samples))
        self.ax.set_ylim((-140, 140)) # Hardcoded 8-bit ADC
        self.ax.set_xlabel('Sample')
        self.ax.set_ylabel('Amplitude [a.u.]')
