from single_line_axis import SingleLineAxis

class MagRatioTimeAxis(SingleLineAxis):
    """
    Class representing an axis from a magnitude ratio v/s time plot.
    """
    def __init__(self, ax, time_arr, title=""):
        SingleLineAxis.__init__(self, ax, time_arr, title)

        self.ax.set_xlim((0, self.xdata[-1]))
        self.ax.set_ylim((-1, 10))
        self.ax.set_xlabel('Time [$\mu$s]')
        self.ax.set_ylabel('Magnitude ratio [linear]')

