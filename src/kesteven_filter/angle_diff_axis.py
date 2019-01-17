from ..axes.single_line_axis import SingleLineAxis

class AngleDiffAxis(SingleLineAxis):
    """
    Class representing an axis from an angle difference v/s time plot.
    """
    def __init__(self, ax, xdata, title=""):
        SingleLineAxis.__init__(self, ax, xdata, title)

        self.ax.set_xlim((0, self.xdata[-1]))
        self.ax.set_ylim((-200, 200))
        self.ax.set_xlabel('Time [$\mu$s]')
        self.ax.set_ylabel('Angle difference [Deg]')

