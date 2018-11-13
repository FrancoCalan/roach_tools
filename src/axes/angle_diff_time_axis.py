import numpy as np
from single_line_axis import SingleLineAxis

class AngleDiffTimeAxis(SingleLineAxis):
    """
    Class representing an axis from an angle difference v/s time plot.
    """
    def __init__(self, ax, time_arr, bw, title=""):
        SingleLineAxis.__init__(self, ax, time_arr, title)

        self.ax.set_xlim((0, self.xdata[-1]))
        self.ax.set_ylim((-200, 200))
        self.ax.set_xlabel('Time [$\mu$s]')
        self.ax.set_ylabel('Angle difference [Deg]')

