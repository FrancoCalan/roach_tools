from single_line_axis import SingleLineAxis

class VMFreqAngleDiffAxis(SingleLineAxis):
    """
    Class representing an axis from an angle difference v/s test number.
    """
    def __init__(self, ax, xdata, title=""):
        SingleLineAxis.__init__(self, ax, xdata, title)

        self.ax.set_xlim((0, self.xdata[-1]))
        self.ax.set_ylim((-200, 200))
        self.ax.set_xlabel('Test number')
        self.ax.set_ylabel('Angle difference [Deg]')

